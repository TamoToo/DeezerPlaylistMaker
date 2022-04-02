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
test_channel_id = 959503035036467270


def findInfos(search_query):
    result = deezer_client.search(search_query)
    #for x in result:
    #    print(x)
    print(type(result))
    songs_data = {'id':[song.id for song in result], 'artist':[song.artist.name for song in result], 'title':[song.title for song in result], 'cover':[song.album.cover for song in result]}
    print(songs_data)
    return songs_data

def addToPlaylist(track_to_add):
    deezer_client.request("POST", f"/playlist/{playlist_id}/tracks", request_method="post", access_token=access_token, songs=track_to_add)
    #print("Done")

def deleteFromPlaylist(track_to_delete):
    deezer_client.request("DELETE", f"/playlist/{playlist_id}/tracks", request_method="delete", access_token=access_token, songs=track_to_delete)

def is_me(m):
    return m.author == bot.user

@bot.command()
async def playlist(ctx, cmd="", search_query=""):
    channel = bot.get_channel(959503035036467270)
    user = ctx.message.author
    await ctx.message.delete()
    if cmd == "":
        await ctx.send(f"https://deezer.com/fr/playlist/{playlist_id}")
    ### ADD HELP, INFO
    elif cmd == "add":
        if search_query != "":
            songs_data = findInfos(search_query)
            song_number = len(songs_data['id'])
            i = 0
            
            def check_reaction(reaction, user):
                return user == ctx.author and reaction.message.id == verification.id and str(reaction.emoji) in "✅❌⏭️⏮️"

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
                    await ctx.send("Choix annulé, timed out.")
                    return
                
                await channel.purge(limit=2, check=is_me)
                emoji_reacted = str(reaction.emoji)

                if emoji_reacted in "✅❌":
                    if emoji_reacted == "✅":
                        try:
                            addToPlaylist(songs_data['id'][i])
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
            await ctx.send("USAGE : **!addplaylist <request>**")
    elif cmd == "remove":
        playlist_tracks = deezer_client.get_playlist(playlist_id).get_tracks()
        playlist_data = {'id':[track.id  for track in playlist_tracks], 'artist':[track.artist.name for track in playlist_tracks], 'title':[track.title for track in playlist_tracks]}
        playlist_len = len(playlist_data['id'])
        str_embed = ""
        for i in range(playlist_len):
            str_embed += f"{i+1}. **{playlist_data['artist'][i]} - {playlist_data['title'][i]}**\n"
        embed = discord.Embed(title="Choose a track to delete (delete <numero_1>, <numero_2>...)",
                            description=str_embed)
        await ctx.send(embed=embed)

        def check_message(message):
                return message.author == ctx.author and message.channel.id == ctx.channel.id
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
                deleteFromPlaylist(id_to_delete)
                await ctx.send(f"**{playlist_data['artist'][index]} - {playlist_data['title'][index]}** a bien été retiré de la playlist\n")

bot.run("OTU5NDM5NTkxMjE4MjE3MDEw.Ykb5wA.Mv2zKxoGzQoNgNx7W03PWAABDdk")