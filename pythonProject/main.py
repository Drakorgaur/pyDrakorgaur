import requests
import telebot
import urllib3

BOT_TOKEN = '2016564802:AAEH1HNmHoJ2d4DBOP5FFAEdkEPfNJ4R3yw'

bot = telebot.TeleBot(BOT_TOKEN)

user_dict = {}


class User:
    def __init__(self, name):
        self.name = name


@bot.message_handler(commands=['status'])
def status_handler(message):
    chat_id = message.chat.id
    try:
        resp = requests.get('http://barzali.com/index')
        resp.raise_for_status()
        bot.send_message(chat_id, str(resp.status_code))
    except (requests.exceptions.HTTPError, ConnectionRefusedError,
            urllib3.exceptions.NewConnectionError, urllib3.exceptions.MaxRetryError,
            requests.exceptions.ConnectionError) as e:
        bot.send_message(chat_id, 'Site is not responsible')
        bot.send_message(chat_id, 'Error: ' + str(e))
    bot.send_message(chat_id, "I'm living to serve")


@bot.message_handler(commands=['user.info'])
def user_info_handler(message):
    chat_id = message.chat.id
    print(message.text)
    bot.send_message(chat_id, "Enter what username do you want to check:")
    bot.register_next_step_handler(message, get_user_info)


def get_user_info(message):
    chat_id = message.chat.id
    print(message.text)
    response = requests.get('http://barzali.com/api/user/' + message.text + '/')
    resp = response.json()
    bot.send_message(chat_id, 'there')
    bot.send_message(chat_id,   'Username:   ' + str(resp['username']) + '\n'
                                'Groups:        ' + str(resp['groups']) + '\n'
                                'First Name: ' + str(resp['first_name']) + '\n'
                                'Last Name: ' + str(resp['last_name']) + '\n'
                                'email:           ' + str(resp['email']) + '\n'
    )


@bot.message_handler(content_types=['text'])
def handler_text(message):
    text = message.text
    print(text)


bot.polling()
