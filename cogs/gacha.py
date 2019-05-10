import discord
from discord.ext import commands
import json
from urllib.request import urlopen
import random

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
            random_card(self, ctx)

    @commands.command()
    async def inv(self, ctx):
        await ctx.send('Here is a list of the cards in your inventory:')

    async def random_card(self, ctx):
        id_list = json.load(urlopen('http://schoolido.lu/api/cardids/'))
        rnd_id = random.randint(1, len(id_list))
        rnd_card = json.load(urlopen('http://schoolido.lu/api/cards/' + str(rnd_id) + '/'))
        rnd_idol = rnd_card.get('idol')

        cardstr = '**ID:** ' + str(rnd_card.get('id')) + '\n**Name:** ' +\
            rnd_idol.get('name') + '\n**Main Unit:** ' + rnd_idol.get('main_unit') +\
            '\n**Sub Unit:** ' + rnd_idol.get('sub_unit') + '\n**Rarity:** ' +\
            rnd_card.get('rarity') + '\n**Attribute:** ' + str(rnd_card.get('attribute'))

        # url1 = rnd_card.get('card_image')
        # url2 = rnd_card.get('card_idolized_image')
        #
        # img1=urllib.FancyURLopener()
        # img1.retrieve(url1, str(rnd_card.get('id')) + 'unidolized')
        #
        # img2=urllib.FancyURLopener()
        # img2.retrieve(url2, str(rnd_card.get('id')) + 'idolized')
        #
        #
        # images = Attachment(cardstr, img1, img2)
        # return cardstr
        ctx.send(cardstr)

def setup(bot):
    bot.add_cog(Gacha(bot))
