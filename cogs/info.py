import discord
from discord.ext import commands
import json
import urllib
from urllib.request import urlopen
import io
import aiohttp
import datetime
from collections import OrderedDict
import PIL
from PIL import Image
from PIL import ImageOps
import re

aliases = {'yohane':'yoshiko', 'elichika':'eli', 'maru':'hanamaru', 'pana':'hanayo'}

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

        lists = self.get_lists(name)
        idol_list = lists[0]
        member_list = lists[1]

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
        while (i < len(idol_list) and not self.is_name(name, idol_list[i].get('name'))):
            i += 1
        try:
            idol = idol_list[i]
            infomsg = SIFHandler.get_info(idol)
        except (TypeError, IndexError):
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
        i = 0
        while (i < len(member_list) and not self.is_name(name, member_list[i].get('name'))):
            i += 1
        try:
            member = member_list[i]
            infomsg = GBPHandler.get_info(member)
        except (TypeError, IndexError):
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

    @commands.command()
    async def bio(self, ctx, *args):
        if (len(args) < 1):
            await ctx.send('The correct format is ' + self.bot.command_prefix + 'info' +\
                ' [character name]')
            return

        name = args[0]

        lists = self.get_lists(name)
        idol_list = lists[0]
        member_list = lists[1]

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
        while (i < len(idol_list) and not self.is_name(name, idol_list[i].get('name'))):
            i += 1
        try:
            idol = idol_list[i]
            infomsg = '**' + idol.get('name') + '**\n'
            infomsg += SIFHandler.get_desc(idol)
        except (TypeError, IndexError):
            check_next = True
        else:
            await ctx.send(infomsg)

        # Check Bandori members
        i = 0
        while (i < len(member_list) and not self.is_name(name, member_list[i].get('name'))):
            i += 1
        try:
            member = member_list[i]
            infomsg = '**' + member.get('name') + '**\n'
            infomsg += GBPHandler.get_desc(member)
        except (TypeError, IndexError):
            if check_next is True:
                await ctx.send('I could not find the character you\'re looking for! The' +\
                    ' correct format is ' + self.bot.command_prefix + 'info [character name]')
                return
        else:
            await ctx.send(infomsg)

    def get_lists(self, name):
        """Fetches lists of cards from APIs"""
        if name in aliases:
            name = aliases.get(name)

        idol_list = json.load(urlopen('http://schoolido.lu/api/idols?search=' +\
            name)).get('results')

        url = 'http://bandori.party/api/members?search=' + name
        request = urllib.request.Request(url)

        request.add_header('user-agent',"Mozilla/5.0 (Windows NT 10.0; Win64;' +\
        ' x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131' +\
        ' Safari/537.36}")

        current_list = json.load(urllib.request.urlopen(request))
        member_list = current_list.get('results')

        while current_list.get('next') is not None:
            request = urllib.request.Request(current_list.get('next'))

            request.add_header('user-agent',"Mozilla/5.0 (Windows NT 10.0; Win64;' +\
            ' x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131' +\
            ' Safari/537.36}")
            current_list = json.load(urllib.request.urlopen(request))
            member_list = member_list + current_list.get('results')

        return (idol_list, member_list)

    def is_name(self, search_name, current_name):
        """Makes sure the name being searched for is standalone"""
        search_name = search_name.lower()
        current_name = current_name.lower()

        search_str = '\\b' + search_name + '\\b'
        found = re.search(search_str, current_name)

        if found is not None:
            return True
        return False

class SIFHandler():
    info_list = OrderedDict([('name', 'Name'), ('school', 'School'), ('year',\
        'Year'), ('main_unit', 'Unit'), ('attribute', 'Attribute'), ('birthday',\
        'Birthday'), ('astrological_sign', 'Star Sign'), ('blood', 'Blood Type'),\
        ('favorite_food', 'Favorite Food'), ('least_favorite_food', 'Least' +\
        ' Favorite Food'), ('hobbies', 'Hobbies')])

    @staticmethod
    def get_info(idol):
        # TODO handling for subunit formatting
        infomsg = ''
        for key, val in SIFHandler.info_list.items():
            if (idol.get(key) is not None):
                temp = idol.get(key)
                if (key == 'birthday'):
                    date = datetime.datetime(1970, int(temp[:2]), int(temp[3:]))
                    temp = date.strftime('%B %d')
                infomsg += '**' + val + ':** ' + temp + '\n'
        return infomsg

    @staticmethod
    def get_desc(idol):
        return idol.get('summary')

class GBPHandler():
    info_list = OrderedDict([('name', 'Name'), ('school', 'School'),\
        ('i_school_year','Year'), ('i_band', 'Band'), ('birthday', 'Birthday'),\
        ('i_astrological_sign', 'Star Sign'), ('food_likes', 'Favorite Food'),\
        ('food_dislikes', 'Least Favorite Food'), ('hobbies', 'Hobbies')])

    @staticmethod
    def get_info(member):
        infomsg = ''
        for key, val in GBPHandler.info_list.items():
            if (member.get(key) is not None):
                temp = member.get(key)
                if (key == 'birthday'):
                    date = datetime.datetime(1970, int(temp[5:-3]), int(temp[-2:]))
                    temp = date.strftime('%B %d')
                infomsg += '**' + val + ':** ' + temp + '\n'
        return infomsg

    @staticmethod
    def get_desc(member):
        return member.get('description')

def setup(bot):
    bot.add_cog(Info(bot))
