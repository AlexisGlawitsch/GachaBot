import discord
from discord.ext import commands
import json
import urllib
from urllib.request import urlopen
import random
import io
import aiohttp
import PIL
from PIL import Image
from abc import ABC, abstractmethod
from collections import OrderedDict

# Organize extra classes into different file later
class ImageLoadError(Exception):
   """Raised when an image cannot be loaded"""
   pass

class GachaHandler():
    rates = None
    info_list = None

    def __init__(self):
        self.rnd_card = None

    def gen_rarity(self):
        rates = self.rates
        rnd_num = random.randint(1, 100)

        rarity = None
        prev_key = 0

        for key, val in rates.items():
            if rnd_num < prev_key + key:
                rarity = val
                break
            prev_key += key

        return rarity

    def gen_info(self):
        info_list = self.info_list

        infomsg = ''

        for key, val in info_list.items():
            if (member.get(key) is not None):
                temp = member.get(key)
                infomsg += '**' + val + ':** ' + temp + '\n'
        return infomsg

    @abstractmethod
    def random_card(self, *args):
        pass

class SIFGacha(GachaHandler):
    rates = {80: 'R', 15: 'SR', 4: 'SSR', 1: 'UR'}
    rarities = ['UR', 'SSR', 'SR', 'R', 'N']
    info_list = OrderedDict([('id', 'ID'), ('name', 'Name'), ('main_unit', 'Main Unit'),\
        ('sub_unit', 'Sub Unit'), ('translated_collection', 'Collection'),\
        ('attribute', 'Attribute'), ('skill', 'Skill'), ('skill_details', '')])

    def __init__(self):
        super().__init__()

    def random_card(self, *args):
        rarity = self.gen_rarity()
        id_list = json.load(urlopen('http://schoolido.lu/api/cardids?' +\
            'is_promo=false&rarity=' + rarity))

        rnd_id = id_list[random.randint(0, len(id_list) - 1)]
        self.rnd_card = json.load(urlopen('http://schoolido.lu/api/cards/' + str(rnd_id) + '/'))
        rnd_card = self.rnd_card
        rnd_idol = rnd_card.get('idol')

        cardstr = ''
        for key, val in self.info_list.items():
            if (rnd_card.get(key)) is not None:
                cardstr += '**' + val + '**: ' + str(rnd_card.get(key)) + '\n'

        return cardstr

    async def get_image(self):
        rnd_card = self.rnd_card

        img1 = None
        img2 = None

        # Retrieve card image(s) and send with message
        if (rnd_card.get('card_image') is not None):
            url1 = 'http:' + rnd_card.get('card_image')
            async with aiohttp.ClientSession() as session:
                async with session.get(url1) as resp:
                    if resp.status != 200:
                        raise ImageError
                        return
                    img1 = io.BytesIO(await resp.read())
        if (rnd_card.get('card_idolized_image') is not None):
            url2 = 'http:' + rnd_card.get('card_idolized_image')
            async with aiohttp.ClientSession() as session:
                async with session.get(url2) as resp:
                    if resp.status != 200:
                        raise ImageLoadError
                        return
                    img2 = io.BytesIO(await resp.read())
        if ((img1 is not None) and (img2 is not None)):
            # Stitch together unidolized and idolized images
            image1 = Image.open(img1)
            image2 = Image.open(img2)

            (width1, height1) = image1.size
            (width2, height2) = image2.size

            result_width = width1 + width2
            result_height = max(height1, height2)

            result = Image.new('RGBA', (result_width, result_height))
            result.paste(im=image1, box=(0, 0))
            result.paste(im=image2, box=(width1, 0))

            byte_io = io.BytesIO()
            result.save(byte_io, format='PNG')
            content = byte_io.getvalue()

            image = discord.File(io.BytesIO(content), str(rnd_card.get('id')) + '.png')
            return image
        elif ((img2 is not None)):
            image = discord.File(img2, str(rnd_card.get('id')) + '.png')
            return image
        else:
            return None

class GBPGacha(GachaHandler):
    rates: {88.5: '2', 8.5: '3', 3: '4'}
    info_list = OrderedDict([('id', 'ID'), ('member', ''), ('i_rarity', 'Rarity'),\
        ('name', 'Card Name'), ('skill_name', 'Skill Name')])
    member_ids = {6: 'Kasumi Toyama', 7: 'Tae Hanazono', 8: 'Rimi Ushigome',\
        9: 'Saaya Yamabuki', 10: 'Arisa Ichigaya', 11: 'Ran Mitake', 12: 'Moca Aoba',\
        13: 'Himari Uehara', 14: 'Tomoe Udagawa', 15: 'Tsugumi Hazawa',\
        16: 'Kokoro Tsurumaki', 17: 'Kaoru Seta', 18: 'Hagumi Kitazawa',\
        19: 'Kanon Matsubara', 20: 'Misaki Okusawa', 21: 'Aya Maruyama',\
        22: 'Hina Hikawa', 23: 'Chisato Shirasagi', 24: 'Maya Yamato',\
        25: 'Eve Wakamiya', 26: 'Yukina Minato', 27: 'Sayo Hikawa', 28: 'Lisa Imai',\
        29: 'Ako Udagawa', 30: 'Rinko Shirokane'}

    def __init__(self):
        super().__init__()

    # Update this for GBP
    def random_card(self, *args):
        request = urllib.request.Request('http://bandori.party/api/cardids')

        request.add_header('user-agent',"Mozilla/5.0 (Windows NT 10.0; Win64;' +\
        ' x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131' +\
        ' Safari/537.36}")

        id_list = json.load(urlopen(request))

        rnd_id = id_list[random.randint(0, len(id_list) - 1)]

        request = urllib.request.Request('http://bandori.party/api/cards/' + str(rnd_id))

        request.add_header('user-agent',"Mozilla/5.0 (Windows NT 10.0; Win64;' +\
        ' x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131' +\
        ' Safari/537.36}")

        self.rnd_card = json.load(urlopen(request))
        rnd_card = self.rnd_card
        rnd_member = rnd_card.get('idol')

        # Use an iterator
        cardstr = ''
        for key, val in self.info_list.items():
            if (rnd_card.get(key)) is not None:
                if (key == 'member'):
                    cardstr += '**Name**: ' + self.member_ids.get(rnd_card.get(key)) +'\n'
                    continue
                cardstr += '**' + val + '**: ' + str(rnd_card.get(key)) + '\n'

        return cardstr

    async def get_image(self):
        rnd_card = self.rnd_card

        img1 = None
        img2 = None

        # Retrieve card image(s) and send with message
        if (rnd_card.get('art') is not None):
            url1 = rnd_card.get('art')
            async with aiohttp.ClientSession() as session:
                async with session.get(url1) as resp:
                    if resp.status != 200:
                        raise ImageError
                        return
                    img1 = io.BytesIO(await resp.read())
        if (rnd_card.get('art_trained') is not None):
            url2 = rnd_card.get('art_trained')
            async with aiohttp.ClientSession() as session:
                async with session.get(url2) as resp:
                    if resp.status != 200:
                        raise ImageLoadError
                        return
                    img2 = io.BytesIO(await resp.read())
        if ((img1 is not None) and (img2 is not None)):
            # Stitch together unidolized and idolized images
            image1 = Image.open(img1)
            image2 = Image.open(img2)

            (width1, height1) = image1.size
            (width2, height2) = image2.size

            result_width = max(width1, width2)
            result_height = height1 + height2

            result = Image.new('RGBA', (result_width, result_height))
            result.paste(im=image1, box=(0, 0))
            result.paste(im=image2, box=(0, height1))

            byte_io = io.BytesIO()
            result.save(byte_io, format='PNG')
            content = byte_io.getvalue()

            image = discord.File(io.BytesIO(content), str(rnd_card.get('id')) + '.png')
            return image
        elif ((img1 is not None)):
            image = discord.File(img1, str(rnd_card.get('id')) + '.png')
            return image
        else:
            return None

class Gacha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def roll(self, ctx, game):
        handlers = {'sif': SIFGacha(), 'gbp': GBPGacha()}

        handler = handlers.get(game)
        # try:
        cardstr = handler.random_card()
        # except AttributeError:
        #     await ctx.send('Sorry, I couldn\'t find the game you\'re looking' +\
        #         ' for.\nUse `sif` for Love Live! School Idol Festival! and ' +\
        #         '`gbp` for Bang Dream! Girls Band Party.\n\nType `' + self.bot.command_prefix +\
        #         'help roll` for more information.')
        #     return

        try:
            image = await handler.get_image()
        except ImageLoadError:
            await ctx.send('Oops, something went wrong with ' +\
                'downloading the image.')

        if image is not None:
            await ctx.send(content=cardstr, file=image)
        else:
            await ctx.send(cardstr)


def setup(bot):
    bot.add_cog(Gacha(bot))
