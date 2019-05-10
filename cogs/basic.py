import discord
from discord.ext import commands

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def help(self, ctx, *args):
        prefix = self.bot.command_prefix

        if len(args) == 0:
            helpmsg = 'Here is a list of all available GachaBot commands:\n'
            helpmsg += '**Gacha:** inv roll\n'
            helpmsg += '**Info:** card idol\n'
            helpmsg += '**Bot Management:** defprefix\n\n'
            helpmsg += 'For help with individual commands, type ' + prefix + 'help ' +\
                '[command]'
            await ctx.send(helpmsg)
        elif len(args) >= 1:
            cmd = args[0]
            if cmd == 'inv':
                return 'Displays the cards currently contained in a user\'s inventory.\n' +\
                    'Proper format is ' + prefix + 'inv.\n\nAdditional parameters:\n' +\
                    '[@user] - Checks the inventory of a user on the Discord server.'
            elif cmd == 'roll':
                return 'Rolls the gacha.\nProper format is ' + prefix + 'roll.\n\n' +\
                    'Additional parameters:\n[name] - Name of the character for ' +\
                    'character-specific rolls\n[rarity] - Rarity of the card for ' +\
                    'rarity-specific rolls\n[num] - Number of rolls up to 5'
            elif cmd == 'card':
                return 'Returns information about a specific card.\nProper format is ' +\
                    prefix + 'card [card id]'
            elif cmd == 'idol':
                return 'Returns information on a specific SIF idol.\nProper format is ' +\
                    prefix + 'idol [idol name]'
            elif cmd == 'defprefix':
                return 'Sets the prefix for GachaBot.\nProper format is ' + prefix +\
                    'defprefix [new prefix]'
            else:
                return 'Invalid command. Check ' + prefix + 'help for the list of commands.'

def setup(bot):
    bot.add_cog(Basic(bot))
