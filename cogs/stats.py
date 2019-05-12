import discord
from discord.ext import commands

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def profile(self, ctx):
        await ctx.send('Here is your profile')
        
    @commands.command()
    async def inv(self, ctx):
        await ctx.send('Here is a list of the cards in your inventory:')

def setup(bot):
    bot.add_cog(Stats(bot))
