import discord
from discord.ext import commands
import json
from urllib.request import urlopen
import random
import io
import aiohttp
import PIL
from PIL import Image
from abc import ABC, abstractmethod

# Organize extra classes into different file later
class ImageLoadError(Exception):
   """Raised when an image cannot be loaded"""
   pass

class GachaHandler():
    rates = None

    def __init__(self):
        self.rnd_card = None

    def gen_rarity(self):
        rates = self.rates
        rnd_num = random.randint(1, 100)

        print('Random Number: ' + str(rnd_num))

        rarity = None
        prev_key = 0

        for key, val in rates.items():
            print(str(prev_key + key))
            if rnd_num < prev_key + key:
                rarity = val
                print('New Rarity: ' + val)
                break
            prev_key += key

        return rarity

    @abstractmethod
    def random_card(self):
        pass

    # @abstractmethod
    # def random_card(self, character):
    #     pass

class SIFGacha(GachaHandler):
    rates = {80: 'R', 15: 'SR', 4: 'SSR', 1: 'UR'}

    def __init__(self):
        super().__init__()

    def random_card(self):
        rarity = self.gen_rarity()
        id_list = json.load(urlopen('http://schoolido.lu/api/cardids?' +\
            'is_promo=false&rarity=' + rarity))

        rnd_id = id_list[random.randint(0, len(id_list) - 1)]
        self.rnd_card = json.load(urlopen('http://schoolido.lu/api/cards/' + str(rnd_id) + '/'))
        rnd_card = self.rnd_card
        rnd_idol = rnd_card.get('idol')

        print(rnd_card)
        # Use an iterator
        cardstr = '**ID:** ' + str(rnd_card.get('id')) + '\n**Name:** ' +\
            rnd_idol.get('name')
        if rnd_idol.get('main_unit') is not None:
            cardstr += '\n**Main Unit:** ' + rnd_idol.get('main_unit')
        if rnd_idol.get('sub_unit') is not None:
            cardstr += '\n**Sub Unit:** ' + rnd_idol.get('sub_unit')
        cardstr += '\n**Rarity:** ' + rnd_card.get('rarity')
        if rnd_idol.get('attribute') is not None:
            cardstr += '\n**Attribute:** ' + str(rnd_card.get('attribute'))

        return cardstr

    # def random_card(self, character):
    #     rarity = self.gen_rarity()
    #     # TODO
    #     # Get list of IDs matching character name and rarity

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

    def __init__(self):
        super().__init__()

    def random_card(self):
        pass

    # def random_card(self, character):
    #     pass

class Gacha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def roll(self, ctx, game):
        handlers = {'sif': SIFGacha(), 'gbp': GBPGacha()}

        handler = handlers.get(game)
        cardstr = handler.random_card()

        try:
            image = await handler.get_image()
        except ImageLoadError:
            await ctx.send('Oops, something went wrong with ' +\
                'downloading the image.')
            return

        if image is not None:
            await ctx.send(content=cardstr, file=image)
        else:
            await ctx.send(cardstr)


def setup(bot):
    bot.add_cog(Gacha(bot))
