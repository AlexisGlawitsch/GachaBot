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

    @commands.command()
    async def stats(self, ctx):
        msg = 'Rolled Cards:\n\nLove Live! School Idol Festival!\n'
        msg += 'UR: 0\nSSR: 0\nSR: 0\nR: 0\n\nBang Dream! Girls Band Party\n'
        msg += '4 Star: 0\n3 Star: 0\n2 Star: 0'
        
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(Stats(bot))
