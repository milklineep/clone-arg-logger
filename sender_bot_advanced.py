# Licence: MIT

import os, sys

import discord
from discord import app_commands
from secrets import game_url, bot_token, guild_id, log_channel_id, priviliged_users_ids_list
import socketio
import datetime
import asyncio

logins = {}

MY_GUILD = discord.Object(id=guild_id)

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

def prepare_message(temp_buffer):
    s = 'In the past 2 secs, received these messages in the categories chat, suspended, loggedIn:\n'
    for msg in temp_buffer:
        s += "{}\n".format(msg)
    return s

# The rename decorator allows us to change the display of the parameter on Discord.
# In this example, even though we use `text_to_send` in the code, the client will use `text` instead.
# Note that other decorators will still refer to it as `text_to_send` in the code.
@client.tree.command()
@app_commands.rename(text_to_send='text')
@app_commands.describe(text_to_send='Text to send to the chat')
async def send(interaction: discord.Interaction, text_to_send: str):
    """Sends the text to the game."""
    # await interaction.response.send_message(text_to_send)
    # return

    if interaction.user.id not in logins:
        await interaction.response.send_message("Not logged in.")
        return

    temp_buffer = []
    login_error = {'data': False}

    user_login = logins[interaction.user.id]['username']
    user_password = logins[interaction.user.id]['password']

    sio = socketio.Client()

    def login():
        assert(user_login is not None)
        assert(user_password is not None)
        user = {
            'username': user_login,
            'password': user_password
        }
        sio.emit('login', data=user)

    @sio.event
    def connect():
        print("I'm connected!")
        try:
            login()
        except:
            sio.disconnect()

    @sio.event
    def connect_error(data):
        print("The connection failed!", data)

    @sio.event
    def disconnect():
        print("I'm disconnected!")


    @sio.on('chat')
    def temp_buffer_append_chat(data):
        dt = datetime.datetime.now(datetime.timezone.utc)
        isotime = dt.isoformat()
        log_str = '**chat:** {}: {}'.format(isotime, data)

        temp_buffer.append(log_str)

    @sio.on('suspended')
    def temp_buffer_append_suspended(data):
        dt = datetime.datetime.now(datetime.timezone.utc)
        isotime = dt.isoformat()
        log_str = '**suspended:** {}: {}'.format(isotime, data)

        temp_buffer.append(log_str)
    
    @sio.on('loggedIn')
    def temp_buffer_append_loggedIn(data):
        dt = datetime.datetime.now(datetime.timezone.utc)
        isotime = dt.isoformat()
        log_str = '**loggedIn:** {}: {}'.format(isotime, data)

        temp_buffer.append(log_str)

        error = data.get('error', True)

        if error:
            global login_error
            login_error['data'] = True
            login_error['message'] = data.get('message', '')


    if len(text_to_send) < 1: 
        await interaction.response.send_message("Text too short.")
        return

    if len(text_to_send) > 500: text_to_send = text_to_send[:500]

    data = {"username": user_login, "message": text_to_send}

    await interaction.response.defer(thinking=True, ephemeral=True)

    sio.connect(game_url, namespaces='/')

    sio.emit('chat', data)

    await asyncio.sleep(2)

    sio.disconnect()

    log_message = prepare_message(temp_buffer)

    await interaction.followup.send("Message sent as {}.{}\n{}".format(user_login, " Error detected. Error: {}".format(login_error.get('message', '')) if login_error['data'] else "", log_message), ephemeral=True)

    log_channel = interaction.guild.get_channel(log_channel_id)

    await log_channel.send("<@{}> tried sending message as {}{}".format(interaction.user.id, user_login, " (error)" if login_error['data'] else ""), allowed_mentions=discord.AllowedMentions.none())

@client.tree.command()
@app_commands.rename(user_login='login')
@app_commands.rename(user_password='password')
@app_commands.describe(user_login='Login for game')
@app_commands.describe(user_password='Password for game')
async def login(interaction: discord.Interaction, user_login: str, user_password: str):
    """Saves login and password and tries to connect."""
    # await interaction.response.send_message(text_to_send)
    # return

    temp_buffer = []
    login_error = {'data': False}

    sio = socketio.Client()

    def login():
        assert(user_login is not None)
        assert(user_password is not None)
        user = {
            'username': user_login,
            'password': user_password
        }
        sio.emit('login', data=user)

    @sio.event
    def connect():
        print("I'm connected!")
        try:
            login()
        except:
            sio.disconnect()

    @sio.event
    def connect_error(data):
        print("The connection failed!", data)

    @sio.event
    def disconnect():
        print("I'm disconnected!")


    @sio.on('chat')
    def temp_buffer_append_chat(data):
        dt = datetime.datetime.now(datetime.timezone.utc)
        isotime = dt.isoformat()
        log_str = '**chat:** {}: {}'.format(isotime, data)

        temp_buffer.append(log_str)

    @sio.on('suspended')
    def temp_buffer_append_suspended(data):
        dt = datetime.datetime.now(datetime.timezone.utc)
        isotime = dt.isoformat()
        log_str = '**suspended:** {}: {}'.format(isotime, data)

        temp_buffer.append(log_str)
    
    @sio.on('loggedIn')
    def temp_buffer_append_loggedIn(data):
        dt = datetime.datetime.now(datetime.timezone.utc)
        isotime = dt.isoformat()
        log_str = '**loggedIn:** {}: {}'.format(isotime, data)

        temp_buffer.append(log_str)

        error = data.get('error', True)

        print("error", repr(error))

        if error:
            login_error['data'] = True
            login_error['message'] = data.get('message', '')


    await interaction.response.defer(thinking=True, ephemeral=True)

    sio.connect(game_url, namespaces='/')

    await asyncio.sleep(2)

    sio.disconnect()

    print("login_error", repr(login_error['data']))

    if not login_error['data']:
        logins[interaction.user.id] = {'username': user_login, 'password': user_password}

    log_message = prepare_message(temp_buffer)

    await interaction.followup.send("Tried logging in as {}.{}\n{}".format(user_login, " Detected error - credentials not saved. Error: {}".format(login_error.get('message', '')) if login_error['data'] else "", log_message), ephemeral=True)

    log_channel = interaction.guild.get_channel(log_channel_id)

    await log_channel.send("<@{}> tried logging in as {}{}".format(interaction.user.id, user_login, " (error)" if login_error['data'] else ""), allowed_mentions=discord.AllowedMentions.none())


@client.tree.command()
async def view_login(interaction: discord.Interaction):
    """Show your credentials only to you."""
    if interaction.user.id not in logins:
        await interaction.response.send_message("Not logged in.", ephemeral=True)
        return
    
    user_login = logins[interaction.user.id]['username']
    user_password = logins[interaction.user.id]['password']

    await interaction.response.send_message("Your credentials are:\n{}\n{}".format(user_login, user_password), ephemeral=True)

@client.tree.command()
async def logout(interaction: discord.Interaction):
    """Delete your credentials from the bot."""
    if interaction.user.id not in logins:
        await interaction.response.send_message("Not logged in.")
        return
    
    user_login = logins[interaction.user.id]['username']

    del logins[interaction.user.id]

    await interaction.response.send_message("Deleted credentials for {}.".format(user_login))


@client.tree.command()
async def users(interaction: discord.Interaction):
    """View the list of logged in users. Privileged users only."""
    if interaction.user.id not in priviliged_users_ids_list:
        await interaction.response.send_message("Not allowed.", ephemeral=True)
        return
    
    s = 'Logged in users: '

    first = True

    for obj in logins.items():
        if first:
            first = False
        else:
            s += ', '
        
        user_discord_id = obj[0]
        user_login = obj[1]['username']

        u = '<@{}> as {}'.format(user_discord_id, user_login)
        s += u

    if first:
        s += '(no users logged in)'

    await interaction.response.send_message(s, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

@client.tree.command()
@app_commands.describe(confirm='Yes to confirm, spelled exactly with the capital letter')
async def shutdown(interaction: discord.Interaction, confirm: str):
    """Turn off this instance of the bot. Privileged users only."""
    if interaction.user.id not in priviliged_users_ids_list:
        await interaction.response.send_message("Not allowed.")
        return
    
    await interaction.response.defer(thinking=True)

    testing = True

    if confirm == "Yes":
        testing = False

    log_channel = interaction.guild.get_channel(log_channel_id)

    await log_channel.send("<@{}> requested shutdown{}".format(interaction.user.id, ' (test)' if testing else ''), allowed_mentions=discord.AllowedMentions.none())

    await interaction.followup.send('Exiting as requested{}'.format(' (dry-run)' if testing else ''))

    if not testing:
        raise KeyboardInterrupt
        sys.exit(0)

def main():
    client.run(TOKEN)

if __name__ == '__main__':
    main()