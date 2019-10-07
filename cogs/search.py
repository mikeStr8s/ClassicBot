from discord.ext import commands


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def classic(self, ctx, category, query):
        await ctx.send('Commands are not implemented yet. But if they were I would return an "{}" search for "{}"'.format(category, query))


def setup(bot):
    bot.add_cog(Search(bot))
