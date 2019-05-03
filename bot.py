import discord
import os

from user_vals import TOKEN
from open_search import OpenSearch, OpenSearchError, SearchObjectError

TOKEN = TOKEN

client = discord.Client()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!classic'):
        search = message.content.replace('!classic ', '')
        channel = message.channel
        if search[:4] == 'item':
            try:
                oser = OpenSearch('item', search.replace('item ', ''))
                oser.search_results.get_tooltip_data()
                image = oser.search_results.image
                await channel.send(file=discord.File(image))
                os.remove(image)
            except (OpenSearchError, SearchObjectError) as e:
                await channel.send(e)
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
