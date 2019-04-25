import discord
import logging

from item_search import search_for_item
from ability_search import search_for_ability
from user_vals import TOKEN
from exceptions import ItemSearchException


TOKEN = TOKEN

client = discord.Client()

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!item'):
        search = message.content.replace('!item ', '')
        channel = message.channel
        try:
            msg = search_for_item(search)
            if msg is not None:
                await channel.send(embed=msg)
            else:
                await channel.send('I could not find Item: {}'.format(search))
        except ItemSearchException as e:
            logger.error(e, exc_info=True)
            await channel.send('{}'.format(e))

    if message.content.startswith('!ability'):
        search = message.content.replace('!ability ', '')
        channel = message.channel
        msgs = search_for_ability(search)
        for msg in msgs:
            await channel.send(embed=msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
