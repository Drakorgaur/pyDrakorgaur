import requests
import telebot
import urllib3
import psycopg2

BOT_TOKEN = '2016564802:AAEln-7Je6d0pc_abFREDypJBu9UpS4lS6M'

bot = telebot.TeleBot(BOT_TOKEN)

user_dict = {}


class User:
    def __init__(self, userId):
        self.userId = userId

    def setId(self, userId):
        self.userId = userId


user = User(0)


@bot.message_handler(commands=['db_status'])
def getTable(message):
    chat_id = message.chat.id
    conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
    cur = conn.cursor()
    if checkIfTablesExists(conn, cur):
        bot.send_message(message.chat.id, "Tables exist")
    else:
        bot.send_message(message.chat.id, "Tables don't exist")


@bot.message_handler(commands=['db_create'])
def tableCreation(message):
    chat_id = message.chat.id
    checkAccess(message)


@bot.message_handler(commands=['db_drop'])
def dropTables(message):
    сommand = (
        """
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS lessons;
        """
    )
    try:
        conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
        cur = conn.cursor()
        if message.chat.id == 455277222:
            cur.execute(сommand)
        else:
            bot.send_message(message.chat.id, "You dont have permission for this action")
        cur.close()
        conn.commit()
        bot.send_message(message.chat.id, "Tables was successfully deleted")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error was: ")
        print(error)
    finally:
        if conn is not None:
            conn.close()


@bot.message_handler(commands=['add_user'])
def createUser(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     "Send me your name (and optional surname)(separate your inputs by space in format NAME SURNAME)")
    bot.send_message(chat_id, "Example: \n Bob \n Bob Gray")
    bot.register_next_step_handler(message, get_user_data)


@bot.message_handler(commands=['show_user'])
def showUserInfo(message):
    chat_id = message.chat.id
    if chat_id == 455277222:
        bot.send_message(chat_id, "You have permission for this action")
        getUserInfo(message)
    else:
        bot.send_message(chat_id, "You dont have permission for this action")


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


@bot.message_handler(content_types=['text'])
def handler_text(message):
    text = message.text
    print(text)


def get_user_info(message):
    chat_id = message.chat.id
    print(message.text)
    response = requests.get('http://barzali.com/api/user/' + message.text + '/')
    resp = response.json()
    bot.send_message(chat_id, 'there')
    bot.send_message(chat_id, 'Username:   ' + str(resp['username']) + '\n'
                                                                       'Groups:        ' + str(resp['groups']) + '\n'
                                                                                                                 'First Name: ' + str(
        resp['first_name']) + '\n'
                              'Last Name: ' + str(resp['last_name']) + '\n'
                                                                       'email:           ' + str(resp['email']) + '\n')


def checkAccess(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, chat_id)
    if message.chat.id == 455277222:
        createTable(message)
    else:
        bot.send_message(chat_id, "You dont have permission for this action")


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
            name VARCHAR(255) NOT NULL,
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
            bot.send_message(message.chat.id, "Tables already exist")
        else:
            for command in commands:
                cur.execute(command)
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
            WHERE    table_name   = 'users'
            );
        """)
    try:
        cur.execute(command)
        boolean = cur.fetchone()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error was: ")
        print(error)

    return boolean[0]


def get_user_data(message):
    global user
    chat_id = message.chat.id
    user.setId(chat_id)
    userData = transformUserData(message)
    if len(userData) == 2:
        command = (
            """
            INSERT INTO users (id, name) values (user.setId, userData)
            """
        )
    elif len(userData) == 1:
        command = (
            """
            INSERT INTO users (id, name, last_name) values (user.userId, userData[0], userData[1])
            """
        )
    else:
        bot.send_message(message.chat.id, "Wrong input")
    try:
        conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
        cur = conn.cursor()
        if checkIfTablesExists(conn, cur):
            cur.execute(command)
        else:
            bot.send_message(message.chat.id, "Tables are not exist")
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        bot.send_message(message.chat.id, "Error: ")
        bot.send_message(message.chat.id, error)
    finally:
        if conn is not None:
            conn.close()


def transformUserData(message):
    data = message.text
    return data.strip().split(" ")


def getUserInfo(message):
    command = (
        """
        SELECT * FROM users WHERE name = 'Mark'
        """
    )
    try:
        result = 0
        conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
        cur = conn.cursor()
        if checkIfTablesExists(conn, cur):
            cur.execute(command)
            result = cur.fetchone()
        else:
            bot.send_message(message.chat.id, "Tables are not exist")
        cur.close()
        conn.commit()
        print(result)
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        bot.send_message(message.chat.id, "Error: " + error)
    finally:
        if conn is not None:
            conn.close()


bot.polling()
