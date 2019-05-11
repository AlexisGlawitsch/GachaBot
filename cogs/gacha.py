import discord
from discord.ext import commands
import json
from urllib.request import urlopen
import random
import io
import aiohttp
import PIL
from PIL import Image

class Gacha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def roll(self, ctx, *args):
        if len(args) > 1:
            # TODO list of valid character names
            charName = args[1];
        else:
            rnd_num = random.randint(1, 100)

            if rnd_num <= 80:
                rarity = 'R'
            elif rnd_num <= 95:
                rarity = 'SR'
            elif rnd_num <= 99:
                rarity = 'SSR'
            else:
                rarity = 'UR'

            id_list = json.load(urlopen('http://schoolido.lu/api/cardids?rarity=' + rarity))

            rnd_id = id_list[random.randint(0, len(id_list) - 1)]

            rnd_card = json.load(urlopen('http://schoolido.lu/api/cards/' + str(rnd_id) + '/'))
            rnd_idol = rnd_card.get('idol')

            cardstr = '**ID:** ' + str(rnd_card.get('id')) + '\n**Name:** ' +\
                rnd_idol.get('name')
            if rnd_idol.get('main_unit') is not None:
                cardstr += '\n**Main Unit:** ' + rnd_idol.get('main_unit')
            if rnd_idol.get('sub_unit') is not None:
                cardstr += '\n**Sub Unit:** ' + rnd_idol.get('sub_unit')
            cardstr += '\n**Rarity:** ' + rnd_card.get('rarity')
            if rnd_idol.get('attribute') is not None:
                cardstr += '\n**Attribute:** ' + str(rnd_card.get('attribute'))

            # Retrieve card image(s) and send with message
            if (rnd_card.get('card_image') is not None)
                (rnd_card.get('card_idolized_image') is not None)):
                url1 = 'http:' + rnd_card.get('card_image')
                url2 = 'http:' + rnd_card.get('card_idolized_image')

                async with aiohttp.ClientSession() as session:
                    async with session.get(url1) as resp:
                        if resp.status != 200:
                            print('Error: Could not download file')
                            await ctx.send('Oops, something went wrong with ' +\
                                'downloading the image.')
                            return
                        img1 = io.BytesIO(await resp.read())
                        image1 = Image.open(img1)
                async with aiohttp.ClientSession() as session:
                    async with session.get(url2) as resp:
                        if resp.status != 200:
                            print('Error: Could not download file')
                            await ctx.send('Oops, something went wrong with ' +\
                                'downloading the image.')
                            return
                        img2 = io.BytesIO(await resp.read())
                        image2 = Image.open(img2)
                (width1, height1) = image1.size
                (width2, height2) = image2.size

                result_width = width1 + width2
                result_height = max(height1, height2)

                result = Image.new('RGB', (result_width, result_height))
                result.paste(im=image1, box=(0, 0))
                result.paste(im=image2, box=(width1, 0))

                byte_io = io.BytesIO()
                result.save(byte_io, format='PNG')
                content = byte_io.getvalue()

                image = discord.File(io.BytesIO(content), str(rnd_id) + '.png')
                await ctx.send(content=cardstr, file=image)
            else:
                await ctx.send(cardstr)

    # @commands.command()
    # async def inv(self, ctx):
    #     await ctx.send('Here is a list of the cards in your inventory:')

def setup(bot):
    bot.add_cog(Gacha(bot))
