# Work with Python 3.6
import discord
from discord.ext import commands
import json

with open('config.json', 'r') as f:
    config_dict = json.load(f)

TOKEN = config_dict['token']

bot = commands.Bot(command_prefix='g!', description="Simulates gacha rolls.")
cogs = ['cogs.basic', 'cogs.info', 'cogs.gacha', 'cogs.config']

bot.remove_command('help')
bot.remove_command('inv')

@bot.event
async def on_ready():
    global cogs

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    if __name__ == '__main__':
        for cog in cogs:
            bot.load_extension(cog)

    await bot.change_presence(status=discord.Status.online,\
        activity=discord.Game(name='' + bot.command_prefix + 'help'))

bot.run(TOKEN)
