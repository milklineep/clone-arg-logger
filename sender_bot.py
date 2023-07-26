import os, sys

import discord
from discord import app_commands
from secrets import game_url, bot_token, chat_login, chat_password
import socketio

sio = socketio.Client()

def login():
    assert(chat_login is not None)
    assert(chat_password is not None)
    user = {
        'username': chat_login,
        'password': chat_password
    }
    sio.emit('login', data=user)

@sio.event
def connect():
    print("I'm connected!")
    try:
        login()
    except:
        sio.disconnect()
        sys.exit(-1)

@sio.event
def connect_error(data):
    print("The connection failed!", data)

@sio.event
def disconnect():
    print("I'm disconnected!")


MY_GUILD = discord.Object(id=876874507258847274)

TOKEN = bot_token

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()

client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

# The rename decorator allows us to change the display of the parameter on Discord.
# In this example, even though we use `text_to_send` in the code, the client will use `text` instead.
# Note that other decorators will still refer to it as `text_to_send` in the code.
@client.tree.command()
@app_commands.rename(text_to_send='text')
@app_commands.describe(text_to_send='Text to send to the chat')
async def send(interaction: discord.Interaction, text_to_send: str):
    """Sends the text into the current channel."""
    # await interaction.response.send_message(text_to_send)
    # return

    if len(text_to_send) < 1: return

    if len(text_to_send) > 500: text_to_send = text_to_send[:500]

    data = {"username": chat_login, "message": text_to_send}

    sio.emit('chat', data)

    await interaction.response.send_message("Message sent as {}.".format(chat_login))

@client.tree.command()
@app_commands.rename(text_to_send='text')
@app_commands.describe(text_to_send='Text to send to the chat')
async def send(interaction: discord.Interaction, text_to_send: str):
    """Sends the text into the current channel."""
    # await interaction.response.send_message(text_to_send)
    # return

    if len(text_to_send) < 1: return

    if len(text_to_send) > 500: text_to_send = text_to_send[:500]

    data = {"username": chat_login, "message": text_to_send}

    sio.emit('chat', data)

    await interaction.response.send_message("Message sent as {}.".format(chat_login))

def main():
    sio.connect(game_url, namespaces='/')
    client.run(TOKEN)

if __name__ == '__main__':
    main()