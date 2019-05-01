import discord

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
        await channel.send('The bot is currently under development and is not functional')


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
