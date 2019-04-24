import discord
import re

from item import build_item_message
from user_vals import TOKEN

TOKEN = TOKEN

client = discord.Client()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!item'):
        search = message.content.replace('!item ', '')
        channel = message.channel
        msg = build_item_message(search)
        if msg is not None:
            await channel.send(embed=msg)
        else:
            await channel.send('I could now find Item: {}'.format(search))


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
