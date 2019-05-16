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

aliases = {'yohane': 'yoshiko', 'elichika': 'eli', 'maru': 'hanamaru', 'pana': 'hanayo',
           'michelle': 'misaki'}


class Info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def profile(self, ctx, username):
        """Retrieve a School Idol Tomodachi user by username and display in an embed"""

        user = json.load(urlopen('http://schoolido.lu/api/users/' + username +
                                 '?expand_accounts'))
        username = user.get('username')

        # Implement a way to display multiple accounts, e.g. prompt user to pick
        account = user.get('accounts')[0]

        if account is None:
            ctx.send('Sorry, I can\t find the account you\'re looking for!\n' +\
                'Make sure you\'re typing the School Idol Tomodachi username' +\
                ' rather than the SIF account name.\n\nFor more info, type `' +\
                self.bot.command_prefix + 'help profile`.')
            return

        nickname = account.get('nickname')
        website_url = account.get('website_url')
        friend_id = account.get('friend_id')
        img_url = 'http:' + account.get('center').get('round_image')
        version = account.get('language')
        os = account.get('os')
        device = account.get('device')
        play_with = account.get('play_with')
        rank = account.get('rank')
        ranking = account.get('ranking')

        preferences = json.load(urlopen('http://schoolido.lu/api/users/' + username +\
            '?expand_preferences')).get('preferences')
        description = preferences.get('description')
        best_girl = preferences.get('best_girl')

        embed=discord.Embed(title=nickname + ' | ' + str(friend_id) + ' | ' + version,\
            description=website_url, color=0x9186db)
        embed.set_thumbnail(url=img_url)
        if (len(description) != 0):
            embed.add_field(name='Description', value=description, inline=False)
        embed.add_field(name='Best Girl', value=best_girl, inline=False)
        embed.add_field(name='Rank', value = str(rank), inline=True)
        embed.add_field(name='Ranking', value= '#' + str(ranking), inline=True)
        embed.add_field(name='Device', value=os + ' | ' + device, inline=True)
        embed.add_field(name='Plays With', value=play_with, inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def characters(self, ctx, *args):
        if (args[0] == 'sif'):
            msg = SIFHandler.get_characters()
        elif (args[0] == 'gbp'):
            msg = GBPHandler.get_characters()
        else:
            await ctx.send('Invalid command. Proper format is `' + self.bot.command_prefix +\
                'characters [game]`. Valid games are `sif` for Love Live! School ' +\
                'Idol Festival! and `gbp` for BanG Dream! Girls Band Party.\n\n' +\
                'Type `' + self.bot.command_prefix + 'help characters` for more' +\
                ' information.')
            return

        await ctx.send(msg)

    @commands.command()
    async def info(self, ctx, *args):
        if (len(args) < 1):
            await ctx.send('The correct format is ' + self.bot.command_prefix + 'info' +\
                ' [character name]')
            return

        name = args[0]

        if name in aliases:
            name = aliases.get(name)

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
        while i < len(member_list) and not self.is_name(name, member_list[i].get('name')):
            i += 1
        try:
            member = member_list[i]
            infomsg = GBPHandler.get_info(member)
        except (TypeError, IndexError):
            if check_next is True:
                await ctx.send('I could not find the character you\'re looking for! The'
                               ' correct format is ' + self.bot.command_prefix + 'info [character name]')
                return

        if member is not None:
            if member.get('image') is not None:
                url = member.get('image')

                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            print('Error: Could not download file')
                            await ctx.send('Oops, something went wrong with '
                                           'downloading the image.')
                            return
                        data = io.BytesIO(await resp.read())

                        await ctx.send(content=infomsg,file=discord.File(data, name + '.png'))
            else:
                await ctx.send(infomsg)

    @commands.command()
    async def bio(self, ctx, *args):
        global aliases

        if len(args) < 1:
            await ctx.send('The correct format is ' + self.bot.command_prefix + 'bio'
                            ' [character name]')
            return

        name = args[0]

        if name in aliases:
            name = aliases.get(name)

        lists = self.get_lists(name)
        idol_list = lists[0]
        member_list = lists[1]

        if len(idol_list) == 0 and len(member_list) == 0:
            await ctx.send('I could not find the character you\'re looking for! The'
                           ' correct format is ' + self.bot.command_prefix + 'bio [character name]')
            return

        # May not be the best way to do this
        # Check SIF idols
        check_next = False
        i = 0
        while i < len(idol_list) and not self.is_name(name, idol_list[i].get('name')):
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
        while i < len(member_list) and not self.is_name(name, member_list[i].get('name')):
            i += 1
        try:
            member = member_list[i]
            infomsg = '**' + member.get('name') + '**\n'
            infomsg += GBPHandler.get_desc(member)
        except (TypeError, IndexError):
            if check_next is True:
                await ctx.send('I could not find the character you\'re looking for! The'
                               ' correct format is ' + self.bot.command_prefix + 'info [character name]')
                return
        else:
            await ctx.send(infomsg)

    @staticmethod
    def get_lists(name):
        """Fetches lists of cards from APIs"""
        idol_list = json.load(urlopen('http://schoolido.lu/api/idols?search=' +
                                      name)).get('results')

        url = 'http://bandori.party/api/members?search=' + name
        request = urllib.request.Request(url)

        request.add_header('user-agent', "Mozilla/5.0 (Windows NT 10.0; Win64;' +\
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
        return idol_list, member_list

    @staticmethod
    def is_name(search_name, current_name):
        """Makes sure the name being searched for is standalone"""
        search_name = search_name.lower()
        current_name = current_name.lower()

        search_str = '\\b' + search_name + '\\b'
        found = re.search(search_str, current_name)

        if found is not None:
            return True
        return False


class SIFHandler():
    info_list = OrderedDict([('name', 'Name'), ('school', 'School'), ('year',
        'Year'), ('main_unit', 'Unit'), ('attribute', 'Attribute'), ('birthday',
        'Birthday'), ('astrological_sign', 'Star Sign'), ('blood', 'Blood Type'),
        ('favorite_food', 'Favorite Food'), ('least_favorite_food', 'Least' +
        ' Favorite Food'), ('hobbies', 'Hobbies')])

    @staticmethod
    def get_info(idol):
        # TODO handling for subunit formatting
        infomsg = ''
        for key, val in SIFHandler.info_list.items():
            if idol.get(key) is not None:
                temp = idol.get(key)
                if key == 'birthday':
                    date = datetime.datetime(1970, int(temp[:2]), int(temp[3:]))
                    temp = date.strftime('%B %d')
                infomsg += '**' + val + ':** ' + temp + '\n'
        return infomsg

    @staticmethod
    def get_desc(idol):
        return idol.get('summary')

    @staticmethod
    def get_characters():
        infomsg = 'Love Live! School Idol Festival! Characters:\n\n'
        # infomsg += '**µ\'s**\nHonoka Kousaka\nUmi Sonoda\nKotori Minami\nMaki ' +\
        #     'Nishikino\nRin Hoshizora\nHanayo Koizumi\nNozomi Tojo\nEli Ayase\n' +\
        #     'Nico Yazawa\n\n'
        # infomsg += '**Aqours**\nChika Takami\nRiko Sakurauchi\nYou Watanabe\n' +\
        #     'Hanamaru Kunikinda\nRuby Kurosawa\nYoshiko Tsushima\nKanan Matsuura\n' +\
        #     'Mari Ohara\nDia Kurosawa'
        # return infomsg
        infomsg += '**µ\'s**\n'
        infomsg += '{:40}{:40}{:40}\n'.format('**Printemps**', '**Lily White**',
            '**BiBi**')
        infomsg += '`{:20}{:20}{:20}\n'.format('Honoka Kousaka', 'Nozomi Tojo',
            'Maki Nishikino')
        infomsg += '{:20}{:20}{:20}\n'.format('Kotori Minami', 'Rin Hoshizora',
                'Eli Ayase')
        infomsg += '{:20}{:20}{:20}`\n\n'.format('Hanayo Koizumi', 'Umi Sonoda',
                        'Nico Yazawa')
        infomsg += '**Aqours**\n'
        infomsg += '{:40}{:40}{:40}\n'.format('**CYaRon!**', '**Azalea**',
            '**Guilty Kiss**')
        infomsg += '`{:20}{:20}{:20}\n'.format('Chika Takami', 'Dia Kurosawa',
            'Riko Sakurauchi')
        infomsg += '{:20}{:20}{:20}\n'.format('You Watanabe', 'Hanamaru Kunikida',
                'Yoshiko Tsushima')
        infomsg += '{:20}{:20}{:20}`\n\n'.format('Ruby Kurosawa', 'Kanan Matsuura',
                        'Mari Ohara')
        return infomsg


class GBPHandler():
    info_list = OrderedDict([('name', 'Name'), ('school', 'School'),\
        ('i_school_year','Year'), ('i_band', 'Band'), ('birthday', 'Birthday'),\
        ('i_astrological_sign', 'Star Sign'), ('food_likes', 'Favorite Food'),\
        ('food_dislikes', 'Least Favorite Food'), ('hobbies', 'Hobbies')])

    @staticmethod
    def get_info(member):
        infomsg = ''
        for key, val in GBPHandler.info_list.items():
            if member.get(key) is not None:
                temp = member.get(key)
                if key == 'birthday':
                    date = datetime.datetime(1970, int(temp[5:-3]), int(temp[-2:]))
                    temp = date.strftime('%B %d')
                infomsg += '**' + val + ':** ' + temp + '\n'
        return infomsg

    @staticmethod
    def get_desc(member):
        return member.get('description')

    @staticmethod
    def get_characters():
        infomsg = 'BanG Dream! Girls Band Party Characters:\n\n'
        infomsg += '**Poppin\'Party**\nKasumi Toyama\nRimi Ushigome\nArisa ' +\
            'Ichigaya\nSaya Yamabuki\nTae Hanazono\n\n'
        infomsg += '**Afterglow**\nRan Mitake\nTomoe Udagawa\nHimari Uehara\n' +\
            'Moca Aoba\nTsugumi Hazawa\n\n'
        infomsg += '**Pastel\\*Palettes**\nAya Maruyama\nHina Hikawa\nEve ' +\
            ' Wakamiya\nMaya Yamato\nChisato Shirasagi\n\n'
        infomsg += '**Roselia**\nYukina Minato\nRinko Shirokane\nAko Udagawa\n' +\
            'Lisa Imai\nSayo Hikawa\n\n'
        infomsg += '**Hello, Happy World!**\nKokoro Tsurumaki\nHagumi Kitazawa\n' +\
            'Kanon Matsubara\nKaoru Seta\nMichelle (Misaki Okusawa)'
        return infomsg


def setup(bot):
    bot.add_cog(Info(bot))
