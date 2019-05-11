import discord
from discord.ext import commands
import json
import urllib
from urllib.request import urlopen
import io
import aiohttp
import datetime

aliases = {'yohane':'yoshiko', 'elichika':'eli', 'maru':'hanamaru'}

class SIFHandler():
    @staticmethod
    def get_info(idol):
        infomsg = '**Name:** ' + idol.get('name')
        if (idol.get('school') is not None):
            infomsg += '\n**School:** ' + idol.get('school')
        if (idol.get('year') is not None):
            infomsg += '\n**Year:** ' + idol.get('year')
        if (idol.get('main_unit') is not None):
            infomsg += '\n**Unit:** ' + idol.get('main_unit')
        if (idol.get('sub_unit') is not None):
            infomsg += ' | ' + idol.get('sub_unit')
        if (idol.get('attribute') is not None):
            infomsg += '\n**Attribute:** ' + idol.get('attribute')
        if (idol.get('birthday') is not None):
            # Formats birthday in [full month name] [DD] format
            bday = idol.get('birthday')
            date = datetime.datetime(1970, int(bday[:2]), int(bday[3:])),
            infomsg += '\n**Birthday:** ' + date[0].strftime('%B %d')
        if (idol.get('astrological_sign') is not None):
            infomsg += '\n**Star Sign:** ' + idol.get('astrological_sign')
        if (idol.get('blood') is not None):
            infomsg += '\n**Blood Type:** ' + idol.get('blood')
        if (idol.get('favorite_food') is not None):
            infomsg += '\n**Favorite Food:** ' + idol.get('favorite_food')
        if (idol.get('least_favorite_food') is not None):
            infomsg += '\n**Least Favorite Food:** ' + idol.get('least_favorite_food')
        if (idol.get('hobbies') is not None):
            infomsg += '\n**Hobbies:** ' + idol.get('hobbies')
        return infomsg

class GBPHandler():
    @staticmethod
    def get_info(member):
        infomsg = '**Name:** ' + member.get('name')
        infomsg += '\n**School: **' + member.get('school')
        infomsg += '\n**Year: **' + member.get('i_school_year')
        infomsg += '\n**Band: **' + member.get('i_band')
        return infomsg

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def info(self, ctx, *args):
        if (len(args) < 1):
            await ctx.send('The correct format is ' + self.bot.command_prefix + 'info' +\
                ' [character name]')
            return

        name = args[0]
        if name in aliases:
            name = aliases.get(name)

        idol_list = json.load(urlopen('http://schoolido.lu/api/idols?search=' +\
            name)).get('results')

        url = 'http://bandori.party/api/members?search=' + name
        request = urllib.request.Request(url)

        request.add_header('user-agent',"Mozilla/5.0 (Windows NT 10.0; Win64;' +\
        ' x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131' +\
        ' Safari/537.36}")

        member_list = json.load(urllib.request.urlopen(request)).get('results')

        if (len(idol_list) == 0 and len(member_list) == 0):
            await ctx.send('I could not find the character you\'re looking for! The' +\
                ' correct format is ' + self.bot.command_prefix + 'info [character name]')
            return

        idol = None
        member = None

        # May not be the best way to do this
        # Check SIF idols
        check_next = False
        i = 0
        while (i < len(idol_list) and name.lower() not in idol_list[i].get('name').lower()):
            i += 1
        try:
            idol = idol_list[i]
            infomsg = SIFHandler.get_info(idol)
        # TODO change this to just nonetype error instead of exception in general
        except Exception:
            check_next = True

        if idol is not None:
            if (idol.get('chibi_small') is not None):
                url = idol.get('chibi_small')

                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            print('Error: Could not download file')
                            await ctx.send('Oops, something went wrong with ' +\
                                'downloading the image.')
                            return
                        data = io.BytesIO(await resp.read())
                        await ctx.send(content=infomsg,file=discord.File(data, name + '.png'))
            else:
                await ctx.send(infomsg)

        # Check Bandori members
        if check_next is True or check_next is False:
            i = 0
            while (i < len(member_list) and name.lower() not in member_list[i].get('name').lower()):
                i += 1
            try:
                # Optimize this to be better written, e.g. iterate through categories
                member = member_list[i]
                infomsg = GBPHandler.get_info(member)
            except Exception:
                if check_next is True:
                    await ctx.send('I could not find the character you\'re looking for! The' +\
                        ' correct format is ' + self.bot.command_prefix + 'info [character name]')
                    return

        if (member is not None):
            if (member.get('image') is not None):
                url = member.get('image')

                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            print('Error: Could not download file')
                            await ctx.send('Oops, something went wrong with ' +\
                                'downloading the image.')
                            return
                        data = io.BytesIO(await resp.read())
                        await ctx.send(content=infomsg,file=discord.File(data, name + '.png'))
            else:
                await ctx.send(infomsg)

def setup(bot):
    bot.add_cog(Info(bot))
