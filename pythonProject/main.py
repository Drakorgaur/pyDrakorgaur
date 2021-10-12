import requests
import telebot
import urllib3
import json
import psycopg2
import os


BOT_TOKEN = '2016564802:AAEln-7Je6d0pc_abFREDypJBu9UpS4lS6M'

bot = telebot.TeleBot(BOT_TOKEN)
T_API = 'https://api.telegram.org/bot' + BOT_TOKEN + '/'
user_dict = {}


class Help:
    def __init__(self, file_path=0):
        self.file_path = file_path

    def setFilePath(self, file_path):
        self.file_path = file_path


Help = Help('0')


@bot.message_handler(commands=['add_schedule'])
def downloadDoc(message):
    chat_id = message.chat.id
    #f = json.open('schledule (5).json')
    bot.send_message(chat_id, 'Send me json-format of your schedule')
    bot.register_next_step_handler(message, add_user_schedule)


@bot.message_handler(commands=['db_set'])
def setLessonTable(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Send me json file")
    bot.register_next_step_handler(message, setLessonDatabase)


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
        bot.send_message(chat_id, "What user do you want me to show?")
        bot.register_next_step_handler(message, getUserInfo)
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
    bot.send_message(chat_id, "Enter what username do you want to check:")
    bot.register_next_step_handler(message, get_user_info)


@bot.message_handler(content_types=['text'])
def handler_text(message):
    text = message.text
    print(text)


def get_user_info(message):
    chat_id = message.chat.id
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
    if message.chat.id == 455277222:
        createTable(message)
        bot.send_message(chat_id, "Tables was created")
    else:
        bot.send_message(chat_id, "You dont have permission for this action")


def createTable(message):
    commands = (
        """
        CREATE TABLE lessons (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        day VARCHAR(255) NOT NULL,
                        time_str VARCHAR(255) NOT NULL,
                        time_end VARCHAR(255) NOT NULL
                        );
        """,
        """
         CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NULL,
            lessons INTEGER[]
        );
        """,
        """
         CREATE TABLE user_lessons (
            user_id INTEGER,
            lessons_id INTEGER,
            PRIMARY KEY (user_id, lessons_id),
            CONSTRAINT fk_users FOREIGN KEY(user_id) REFERENCES user(id),
            CONSTRAINT fk_lessons FOREIGN KEY(lessons_id) REFERENCES lessons(id)
        );
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


def setLessonDatabase(message):
    # for (JSON.stringify(Object.assign({}, shedule)))
    dir = 'schedules'
    file_name = 'schedule.json'
    schedule = saveFile(message, dir, file_name)


    command = (
        """
        INSERT INTO lessons (day, time_str, time_end, name, id) values (%s, %s, %s, %s, %s);
        """
    )
    try:
        conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
        cur = conn.cursor()
        if checkIfTablesExists(conn, cur):
            for item in schedule:
                cur.execute(command, (schedule[item][0], schedule[item][1], schedule[item][2], schedule[item][3], schedule[item][4]))
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error was: ")
        if 'duplicate key value violates unique constraint "users_pkey"' in error:
            print("User with this ID already exists")
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
    chat_id = message.chat.id
    userData = transformUserData(message)
    try:
        os.mkdir(os.path.join('users/',  message.chat.username))
    except OSError as error:
        pass
    if len(userData) == 1:
        command = (
            """
            INSERT INTO users (id, username, name) VALUES (%s, %s, %s);
            """
        )
    elif len(userData) == 2:
        command = (
            """
            INSERT INTO users (id, username, name, last_name) VALUES (%s, %s, %s, %s);
            """
        )
    else:
        bot.send_message(message.chat.id, "Wrong input")
    try:
        conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
        cur = conn.cursor()
        if checkIfTablesExists(conn, cur):
            if len(userData) == 1:
                cur.execute(command, (chat_id, message.chat.username, userData))
            elif len(userData) == 2:
                cur.execute(command, (chat_id, message.chat.username, userData[0], userData[1]))
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
        SELECT * FROM USERS WHERE username = (%s);
        """
    )
    try:
        result = 0
        conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
        cur = conn.cursor()
        if checkIfTablesExists(conn, cur):
            cur.execute(command, (message.text, ))
            result = cur.fetchone()
        else:
            bot.send_message(message.chat.id, "Tables are not exist")
        cur.close()
        conn.commit()
        bot.send_message(message.chat.id,
                         "Chat ID  " + str(result[0]) +
                         "\nUsername  " + result[1] +
                         "\nName  " + result[2] +
                         "\nLast Name  " + result[3] +
                         "\nLessons ID  " + str(result[4])
                         )
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        bot.send_message(message.chat.id, "Error: ")
        bot.send_message(message.chat.id, error)
    finally:
        if conn is not None:
            conn.close()


def add_user_schedule(message):
    chat_id = message.chat.id
    directory = 'users'
    file_name = message.chat.username
    schedule = saveFile(message, directory, file_name)
    command = (
        """
        INSERT INTO users (lessons) values (%s);
        """
    )
    try:
        conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
        cur = conn.cursor()
        if checkIfTablesExists(conn, cur):
            schedule = ''
            for item in schedule['indexes']:
                for z in ['0|', '1|', '2|', '3|', '4|']:
                    item = item.replace(z, '')
                schedule = schedule + ', ' + item
            cur.execute(command, (schedule[:-2],))
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error was: ")
        print(error)
    finally:
        if conn is not None:
            conn.close()


def saveFile(message, dir, file_name):
    response = requests.get(T_API + 'getFile?file_id=' + message.document.file_id)
    resp = response.json()
    response = requests.get('https://api.telegram.org/file/bot' + BOT_TOKEN + '/' + resp['result']['file_path'],
                            allow_redirects=True)
    open(dir + '/' + file_name, 'wb').write(response.content)
    with open(dir + '/' + file_name) as file:
        schedule = json.loads(file.read())
    return schedule

bot.polling()
