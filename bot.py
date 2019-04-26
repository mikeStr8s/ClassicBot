import discord

from item_search import search_for_item
from ability_search import search_for_ability
from user_vals import TOKEN
from exceptions import ItemSearchError, AbilitySearchError


TOKEN = TOKEN

client = discord.Client()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!item'):
        search = message.content.replace('!item ', '')
        channel = message.channel
        try:
            msg = search_for_item(search)
        except ItemSearchError as e:
            await channel.send('{}'.format(e))
        else:
            await channel.send(embed=msg)

    if message.content.startswith('!ability'):
        search = message.content.replace('!ability ', '')
        channel = message.channel
        try:
            msgs = search_for_ability(search)
        except AbilitySearchError as e:
            await channel.send(e)
        else:
            for msg in msgs:
                await channel.send(embed=msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
