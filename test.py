# Work with Python 3.6
import discord

TOKEN = 'NTcwNjY3NjkzNzA3ODg2NjE0.XMCh4Q.VN0fqVjv7mpnKvxl9M2LL0wISYs'

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content == "Hello":
        await client.send_message(message.channel, "World")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(status=discord.Status.idle, activity=discord.Game(name="Testing"))

client.run(TOKEN)
