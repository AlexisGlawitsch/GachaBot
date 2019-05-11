import discord
from discord.ext import commands

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    @commands.is_owner()
    async def defprefix(self, ctx, prefix):
        self.bot.command_prefix = prefix
        await ctx.send('GachaBot prefix changed to ' + prefix + '.')

    @defprefix.error
    async def defprefix_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You must be the server owner in order to set the prefix.')

def setup(bot):
    bot.add_cog(Config(bot))
