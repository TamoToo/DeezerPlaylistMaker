import discord
from discord.ext import commands
import deezer
import requests
import json

access_token='frBaED5OSO90k05rvxvinPwOHYJmGT6m46kD6CFz6zlvt9sXzA'
deezer_client = deezer.Client(app_id='534982', app_secret='e9a25ec2d6d09e95416770615222bed9', access_token=access_token)
playlist_id = 10190019482


result = deezer_client.search(artist="micheal jackson", track="")
#for x in result:
#    print(x)
for i in range(5):
    print(i)
print(type(result))
songs_data = {'id':[song.id for song in result], 'artist':[song.artist.name for song in result], 'title':[song.title for song in result], 'cover':[song.album.cover for song in result]}

for i in range(len(songs_data['id'])):
    print(songs_data['id'][i], songs_data['artist'][i], songs_data['title'][i], songs_data['cover'][i])
