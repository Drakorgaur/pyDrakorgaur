import requests
import telebot
import urllib3
import psycopg2

BOT_TOKEN = '2016564802:AAEln-7Je6d0pc_abFREDypJBu9UpS4lS6M'

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
                                'email:           ' + str(resp['email']) + '\n')


@bot.message_handler(commands=['DB'])
def getTable(message):
    chat_id = message.chat.id
    conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
    bot.send_message(chat_id, "Enter what username do you want to check:")
    bot.register_next_step_handler(message, get_user_info)
    cursor = conn.cursor()


@bot.message_handler(commands=['db_create'])
def tableCreation(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Enter pass:")
    bot.register_next_step_handler(message, checkAccess)


def checkAccess(message):
    chat_id = message.chat.id
    print(message.text)
    if message.text == 'asi23oa5nuiSU(NDSax':
        bot.send_message(chat_id, "Enter table name:")
        bot.register_next_step_handler(message, createTable)
    else:
        bot.send_message(chat_id, "Not correct pass:")


def createTable(message):
    commands = (
        """
        CREATE TABLE LESSONS (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        time_str VARCHAR(255) NOT NULL,
                        time_end VARCHAR(255) NOT NULL
                        )
        """,
        """
         CREATE TABLE USERS (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255) NULL,
            last_name VARCHAR(255) NULL,
            lessons INTEGER
            REFERENCES LESSONS (id)
            ON UPDATE CASCADE ON DELETE SET NULL
        )
        """)
    try:
        conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
        cur = conn.cursor()
        if checkIfTablesExists(conn, cur):
            for command in commands:
                cur.execute(command)
        else:
            print("Tables already exist")
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error was: ")
        print(error)
    finally:
        if conn is not None:
            conn.close()


def checkIfTablesExists(conn, cur):
    command = (
        """
        SELECT EXISTS (
            SELECT *
            FROM information_schema.tables 
            WHERE  table_schema = 'schema_name'
            AND    table_name   = 'table_name'
            );
        """)
    try:
        cur.execute(command)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error was: ")
        print(error)
    finally:
        if conn is not None:
            conn.close()



@bot.message_handler(content_types=['text'])
def handler_text(message):
    text = message.text
    print(text)


bot.polling()
