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

def is_me(m):
    return m.author == bot.user

@bot.command()
async def addplaylist(ctx, search_query):
    channel = bot.get_channel(959503035036467270)
    user = ctx.message.author
    print(search_query)
    #await ctx.message.delete()
    if search_query != "":
        songs_data = findInfos(search_query)
        song_number = len(songs_data['id'])
        i = 0
        
        def check(reaction, user):
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
                reaction, user = await bot.wait_for("reaction_add", check=check, timeout=30)
            except asyncio.TimeoutError:
                await ctx.send("Choix annulé, timed out.")
                return
            await channel.purge(limit=2, check=is_me)
            if str(reaction.emoji) == "✅":
                addToPlaylist(songs_data['id'][i])
                await ctx.send("OK")
                i = song_number
            elif str(reaction.emoji) == "❌":
                await ctx.send("PAS OK")
                i = song_number
            elif str(reaction.emoji) == "⏭️":
                i = i + 1
                await ctx.send(f"Titre : {songs_data['artist'][i]} - {songs_data['title'][i]}\nCover : {songs_data['cover'][i]}\n")
            elif str(reaction.emoji) == "⏮️":
                i = i - 1
                await ctx.send(f"Titre : {songs_data['artist'][i]} - {songs_data['title'][i]}\nCover : {songs_data['cover'][i]}\n")
    else:
        await ctx.send("USAGE : **!addplaylist <request>**")


@bot.command()
async def playlist(ctx):
    await ctx.send(f"https://deezer.com/fr/playlist/{playlist_id}")


# @bot.event
# async def on_reaction_add(reaction, user):
#     channel = reaction.message.channel
#     message = reaction.message
#     if (user != bot.user) and (message.author.id != user.id):
#         if message.content == "Est-ce correct ?":
#             while (reaction.emoji != "✅") and (reaction.emoji != "❌"):
#                 if reaction.emoji == ":track_next:":
#                     channel.purge(limit=1, check=is_me)
#                     channel.send()


#             await reaction.message.delete()
#             if reaction.emoji == "✅":
#                 addToPlaylist(playlist_id, access_token, track_searched_id)
#                 await channel.send("C'est ajouté !")
#             elif reaction.emoji == "❌":
#                 await channel.send("Sorry man recommence stp")

bot.run("OTU5NDM5NTkxMjE4MjE3MDEw.Ykb5wA.Mv2zKxoGzQoNgNx7W03PWAABDdk")