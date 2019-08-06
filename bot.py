import os

import discord

from open_search import OpenSearch, OpenSearchError, SearchObjectError
from user_vals import TOKEN

TOKEN = TOKEN

client = discord.Client()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    async def search(t, q, c):
        try:
            oser = OpenSearch(t, q)
            oser.search_results.get_tooltip_data(oser.kwargs['locale'])
            image = oser.search_results.image
            await c.send(file=discord.File(image))
            os.remove(image)
        except (OpenSearchError, SearchObjectError) as e:
            await c.send(e)

    channel = message.channel
    if message.content.startswith('!item'):
        query = message.content.replace('!item ', '')
        await search('item', query, channel)

    elif message.content.startswith('!ability'):
        query = message.content.replace('!ability ', '')
        await search('spell', query, channel)

    elif message.content.startswith('!spell'):
        query = message.content.replace('!spell ', '')
        await search('spell', query, channel)
    else:
        await channel.send(
            'The command you have entered was not recognized, make sure formatting looks like this: '
            '`!classic item training sword`')


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
