import socketio
from discord_webhook import DiscordWebhook
from secrets_logger import webhook_url, game_url
import datetime

f = open('message.log', 'a')

# standard Python
sio = socketio.Client()

@sio.on('chat')
def on_message(data):
    isotime = datetime.datetime.now(datetime.timezone.utc).isoformat()
    print('chat', isotime, data)
    chat_compact = "{}: {}\n".format(isotime, data)
    f.write(chat_compact)
    f.flush()
    # if rate_limit_retry is True then in the event that you are being rate 
    # limited by Discord your webhook will automatically be sent once the 
    # rate limit has been lifted
    webhook = DiscordWebhook(url=webhook_url, rate_limit_retry=True, content=chat_compact)
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



