import os
from discord.ext import commands

from user_vals import TOKEN


INITIAL_EXTENSIONS = [
    'cogs.search',
]


class ClassicBot(commands.Bot):
    def __init__(self):
        super().__init__('!')  # Initialize bot with "!" as the command prefix
        self.token = TOKEN  # Set bot token

        # Load all extensions for bot
        for extension in INITIAL_EXTENSIONS:
            try:
                self.load_extension(extension)
                print('{} loaded'.format(extension))
            except Exception as e:
                print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    def run(self):
        super().run(self.token, reconnect=True)


if __name__ == '__main__':
    classicBot = ClassicBot()
    classicBot.run()
