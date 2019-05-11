import discord
from discord.ext import commands

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('{0}ms'.format(int(self.bot.latency * 1000)))

    @commands.command()
    async def help(self, ctx, *args):
        prefix = self.bot.command_prefix

        if len(args) == 0:
            helpmsg = 'Here is a list of all available GachaBot commands:\n'
            helpmsg += '**Basic:** `help` `ping`\n'
            helpmsg += '**Gacha:** `inv` `roll`\n'
            helpmsg += '**Info:** `card` `idol`\n'
            helpmsg += '**Config:** `defprefix`\n\n'
            helpmsg += 'For help with individual commands, type `' + prefix + 'help ' +\
                '[command]`'
            await ctx.send(helpmsg)
        elif len(args) >= 1:
            cmd = args[0]

            if cmd == 'inv':
                msg = 'Displays the cards currently contained in a user\'s inventory.\n' +\
                    'Proper format is `' + prefix + 'inv`.\n\nAdditional parameters:\n' +\
                    '`@user` - Checks the inventory of a user on the Discord server.'
            elif cmd == 'roll':
                msg = 'Rolls the gacha.\nProper format is `' + prefix + 'roll.`\n\n' +\
                    'Any amount of additional parameters can be added in this order:' +\
                    '\n`name` - Name of the character for character-specific rolls' +\
                    '\n`rarity` - Rarity of the card for rarity-specific rolls' +\
                    '\n`num` - Number of rolls up to 5'
            elif cmd == 'card':
                msg = 'Returns information about a specific card.\nProper format is `' +\
                    prefix + 'card [card id]`'
            elif cmd == 'idol':
                msg = 'Returns information on a specific SIF idol.\nProper format is `' +\
                    prefix + 'idol [idol name]`'
            elif cmd == 'defprefix':
                msg = 'Sets the prefix for GachaBot.\nProper format is `' + prefix +\
                    'defprefix [new prefix]`'
            elif cmd == 'ping':
                msg == 'Returns the bot\'s latency in ms.'
            else:
                msg = 'Invalid command. Check `' + prefix + 'help` for the list of commands.'

            await ctx.send(msg)

def setup(bot):
    bot.add_cog(Basic(bot))
