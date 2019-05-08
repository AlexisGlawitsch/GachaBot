# Work with Python 3.6
import discord
import json
from urllib.request import urlopen
import random

TOKEN = 'NTcwNjY3NjkzNzA3ODg2NjE0.XMCh4Q.VN0fqVjv7mpnKvxl9M2LL0wISYs'
prefix = 'g!'

client = discord.Client()

@client.event
async def on_message(message):
    global prefix

    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    userMsg = message.content
    wordList = userMsg.split()

    if wordList[0] == prefix + 'roll':
        # Check if char name is valid
        if len(wordList) > 1:
            # TODO list of valid character names
            charName = wordList[1];
        else:
            await message.channel.send(random_card())
    elif wordList[0] == prefix + 'inv':
        await message.channel.send('You currently have these cards in your inventory:')
    elif wordList[0] == prefix + 'help':
        if len(wordList) == 1:
            helpmsg = 'Here is a list of all available GachaBot commands:\n'
            helpmsg += '**Gacha:** inv roll\n'
            helpmsg += '**Info:** card idol\n'
            helpmsg += '**Bot Management:** defprefix\n\n'
            helpmsg += 'For help with individual commands, type ' + prefix + 'help ' +\
                '[command]'
            await message.channel.send(helpmsg)
        else:
            await message.channel.send(command_help(wordList[1]))
    elif wordList[0] == prefix + 'defprefix':
        if message.author == Guild.owner:
            if len(wordList) > 1:
                prefix = wordList[1];
                await message.channel.send('GachaBot prefix has been set to ' +\
                    wordList[1])
            else:
                await message.channel.send('Invalid format. The correct format ' +\
                    'is ' + prefix + 'defprefix [new prefix].')
        else:
            await message.channel.send('Only the server owner can change GachaBot\'s' +\
                ' prefix.')
    else:
        await message.channel.send('Invalid command. Type ' + prefix + 'help ' +\
            'for help.')

def random_card():
    id_list = json.load(urlopen('http://schoolido.lu/api/cardids/'))
    rnd_id = random.randint(1, len(id_list))
    rnd_card = json.load(urlopen('http://schoolido.lu/api/cards/' + str(rnd_id) + '/'))
    rnd_idol = rnd_card.get('idol')

    cardstr = '**ID:** ' + str(rnd_card.get('id')) + '\n**Name:** ' +\
        rnd_idol.get('name') + '\n**Main Unit:** ' + rnd_idol.get('main_unit') +\
        '\n**Sub Unit:** ' + rnd_idol.get('sub_unit') + '\n**Rarity:** ' +\
        rnd_card.get('rarity') + '\n**Attribute:** ' + str(rnd_card.get('attribute'))

    return cardstr


def command_help(cmd):
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

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(status=discord.Status.online,
        activity=discord.Game(name='' + prefix + 'help'))

client.run(TOKEN)
