import socketio
from discord_webhook import DiscordWebhook, DiscordEmbed
from secrets import webhook_url, game_url, leaderboard_webhook_url, player_count_webhook_url
import datetime
# import pytz

f = open('message.log', 'a', encoding='utf-8')

last_leaderboard_update = datetime.datetime.now(datetime.timezone.utc)
LEADERBOARD_UPDATE_DELTA = datetime.timedelta(minutes=1)

# standard Python
sio = socketio.Client()

@sio.on('chat')
def on_message(data):
    dt = datetime.datetime.now(datetime.timezone.utc)
    isotime = dt.isoformat()
    print('chat', isotime, data)
    chat_compact = "{}: {}\n".format(isotime, data)
    try:
        f.write(chat_compact)
        f.flush()
    except UnicodeEncodeError:
        pass

    hex_color = data['badgeColor']
    if hex_color == 'red': hex_color = 'ff0000'
    else: hex_color = hex_color[1:]
    author = data['sender']
    text = data['message']

    # if rate_limit_retry is True then in the event that you are being rate 
    # limited by Discord your webhook will automatically be sent once the 
    # rate limit has been lifted
    webhook = DiscordWebhook(url=webhook_url, rate_limit_retry=True, content=chat_compact, allowed_mentions={"parse": []})

    embed = DiscordEmbed(title='', description=text, color=hex_color)
    embed.set_author(name=author)
    embed.set_timestamp(dt)

    webhook.add_embed(embed)

    response = webhook.execute()

@sio.on('leaderboardUpdate')
def leaderboard(data):
    dt = datetime.datetime.now(datetime.timezone.utc)
    isotime = dt.isoformat()

    skip = False

    global last_leaderboard_update

    if dt - last_leaderboard_update <= LEADERBOARD_UPDATE_DELTA:
        skip = True

    print('leaderboard{}'.format(' (skipping)' if skip else ''), isotime, data)
    chat_compact = "leaderboard: {}: {}\n".format(isotime, data)
    try:
        f.write(chat_compact)
        f.flush()
    except UnicodeEncodeError:
        pass

    if skip: return

    last_leaderboard_update = dt

    # if rate_limit_retry is True then in the event that you are being rate 
    # limited by Discord your webhook will automatically be sent once the 
    # rate limit has been lifted

    leaderboard_url = leaderboard_webhook_url if leaderboard_webhook_url is not None else webhook_url

    webhook = DiscordWebhook(url=leaderboard_url, rate_limit_retry=True, content=chat_compact)

    embed = DiscordEmbed(title='Leaderboard', color='00ff00')

    rank = 0

    for player in data:
        field_name = '{}: {}'.format(rank+1, player['username'])

        money = int(player['money'])
        money_string = '${:,}'.format(money)

        embed.add_embed_field(name=field_name, value=money_string)

        rank += 1

    embed.set_timestamp(dt)

    webhook.add_embed(embed)

    response = webhook.execute()

@sio.on('PlayerCount')
def player_count(data):
    dt = datetime.datetime.now(datetime.timezone.utc)
    isotime = dt.isoformat()

    player_count = len(data)
    data = sorted(data)
    print('PlayerCount', isotime, player_count, data)
    chat_compact = "PlayerCount: {}: {}: {}\n".format(isotime, player_count, data)

    try:
        f.write(chat_compact)
        f.flush()
    except UnicodeEncodeError:
        pass

    player_count_url = player_count_webhook_url if player_count_webhook_url is not None else webhook_url

    webhook = DiscordWebhook(url=player_count_url, rate_limit_retry=True, content=chat_compact)

    description = "The following players are online:\n"
    for player in data:
        description += "* {}\n".format(player)

    embed = DiscordEmbed(title='{} players online'.format(player_count), description=description, color='0000ff')

    embed.set_timestamp(dt)

    webhook.add_embed(embed)

    response = webhook.execute()

# def login():
#     if chat_login is not None and chat_password is not None:
#         user = {
#             'username': chat_login,
#             'password': chat_password
#         }

@sio.event
def connect():
    print("I'm connected!")
    # try:
    #     login()
    # except:
    #     sio.disconnect()

@sio.event
def connect_error(data):
    print("The connection failed!", data)

@sio.event
def disconnect():
    print("I'm disconnected!")
    global f
    f.close()
    f = open('message.log', 'a')


sio.connect(game_url)

print('my sid is', sio.sid)



