from distutils import errors
from distutils.log import error
from msilib.schema import Error
from turtle import title
import discord
from discord.ext import commands
import deezer
import asyncio
import requests
import json

access_token='frBaED5OSO90k05rvxvinPwOHYJmGT6m46kD6CFz6zlvt9sXzA'
deezer_client = deezer.Client(app_id='534982', app_secret='e9a25ec2d6d09e95416770615222bed9', access_token=access_token)
playlist_id = 10190019482


discord_client = discord.Client()
bot = commands.Bot(command_prefix="!", case_insensitive=True)


def findInfos(search_query: str):
    result = deezer_client.search(search_query)
    print(type(result))
    songs_data = {'id':[song.id for song in result], 'artist':[song.artist.name for song in result], 'title':[song.title for song in result], 'cover':[song.album.cover for song in result]}
    print(songs_data)
    return songs_data

def modifyPlaylist(method: str, track: int):
    deezer_client.request(method.upper(), f"/playlist/{playlist_id}/tracks", request_method=method.lower(), access_token=access_token, songs=track)

def requestInfosPlaylist():
    playlist_tracks = deezer_client.get_playlist(playlist_id).get_tracks()
    playlist_data = {'id':[track.id  for track in playlist_tracks], 'artist':[track.artist.name for track in playlist_tracks], 'title':[track.title for track in playlist_tracks]}
    return playlist_data
    
def is_me(m):
    return m.author == bot.user

@bot.command()
async def playlist(ctx, cmd="", search_query=""):
    await ctx.message.delete()
    if cmd == "help":
        help_string = discord.Embed(title="Help Menu", description='**!playlist**\n    - **add "<recherche>"** : Ajouter un son à la playlist\n  - **remove** : Retirer un son de la playlist\n - **info** : Envoie les titres de la playlist')
        await ctx.send(embed=help_string)
    elif cmd == "info":
        playlist_data = requestInfosPlaylist()
        playlist_len = len(playlist_data['id'])
        embed_str = ""

        for i in range(playlist_len):
            embed_str += f"{i+1}. **{playlist_data['artist'][i]} - {playlist_data['title'][i]}**\n"
        
        embed = discord.Embed(title="Liste des musiques", description=f"https://deezer.com/fr/playlist/{playlist_id}\n" + embed_str)
        await ctx.send(embed=embed)
    elif cmd == "add":
        if search_query != "":
            def check_reaction(reaction, user):
                return user == ctx.author and reaction.message.id == verification.id and str(reaction.emoji) in "✅❌⏭️⏮️"
        
            songs_data = findInfos(search_query)
            song_number = len(songs_data['id'])
            i = 0
            
            await ctx.send(f"Titre : {songs_data['artist'][i]} - {songs_data['title'][i]}\nCover : {songs_data['cover'][i]}\n")
            while(i < song_number):
                verification = await ctx.send("Est-ce correct ?")
                if i > 0:
                    await verification.add_reaction("⏮️")
                await verification.add_reaction("✅")
                await verification.add_reaction("❌")
                if i < song_number:
                    await verification.add_reaction("⏭️")

                try:
                    reaction, user = await bot.wait_for("reaction_add", check=check_reaction, timeout=30)
                except asyncio.TimeoutError:
                    await ctx.channel.purge(limit=2, check=is_me)
                    await ctx.send("Choix annulé, timed out.")
                    return
                
                await ctx.channel.purge(limit=2, check=is_me)
                emoji_reacted = str(reaction.emoji)

                if emoji_reacted in "✅❌":
                    if emoji_reacted == "✅":
                        try:
                            modifyPlaylist("post",songs_data['id'][i])
                            await ctx.send(f"**{songs_data['artist'][i]} - {songs_data['title'][i]}** a bien été ajouté à la playlist")
                        except deezer.exceptions.DeezerErrorResponse:
                            await ctx.send(f"**{songs_data['artist'][i]} - {songs_data['title'][i]}** est déjà dans la playlist")
                    i = song_number
                elif emoji_reacted in "⏭️⏮️":
                    if emoji_reacted == "⏭️":
                        i = i + 1
                    else:
                        i = i - 1
                    await ctx.send(f"Titre : **{songs_data['artist'][i]} - {songs_data['title'][i]}**\nCover : {songs_data['cover'][i]}\n")
        else:
            await ctx.send("USAGE : **!playlist add <request>**")
    elif cmd == "remove":
        def check_message(message):
                return message.author == ctx.author and message.channel.id == ctx.channel.id
        
        playlist_data = requestInfosPlaylist()
        playlist_len = len(playlist_data['id'])
        embed_str = ""
        for i in range(playlist_len):
            embed_str += f"{i+1}. **{playlist_data['artist'][i]} - {playlist_data['title'][i]}**\n"
        embed = discord.Embed(title="Choose a track to delete (delete <numero_1>, <numero_2>...)",
                            description=embed_str)
        await ctx.send(embed=embed)
        
        try:
            confirm = await bot.wait_for("message", check=check_message, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send("Choix annulé, timed out.")
            return

        tracks_to_delete = []
        for word in confirm.content.split():
            if word.isdigit():
                try:
                    tracks_to_delete.append(playlist_data['id'][int(word)-1])
                except IndexError:
                    await ctx.send(f"Numéro {word} Invalide")

        if "delete" in confirm.content:
            for id_to_delete in tracks_to_delete:
                index = playlist_data['id'].index(id_to_delete)
                modifyPlaylist("delete", id_to_delete)
                await ctx.send(f"**{playlist_data['artist'][index]} - {playlist_data['title'][index]}** a bien été retiré de la playlist\n")
    else:
        await ctx.send("try **!playlist help**")

bot.run("OTU5NDM5NTkxMjE4MjE3MDEw.Ykb5wA.Mv2zKxoGzQoNgNx7W03PWAABDdk")