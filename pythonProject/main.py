import requests
import telebot
import urllib3
import json
import psycopg2
import os


BOT_TOKEN = '2016564802--:AAF7vk3qFn5hkoLrYZuiecAyNvlAGafmOB8'

bot = telebot.TeleBot(BOT_TOKEN)
T_API = 'https://api.telegram.org/bot' + BOT_TOKEN + '/'
user_dict = {}


class Help:
    def __init__(self, file_path=0):
        self.file_path = file_path

    def setFilePath(self, file_path):
        self.file_path = file_path


Help = Help(0)


@bot.message_handler(commands=['add_schedule'])
def downloadDoc(message):
    chat_id = message.chat.id
    #f = json.open('schledule (5).json')
    bot.send_message(chat_id, 'Send me json-format of your schedule')
    bot.register_next_step_handler(message, add_user_schedule)


@bot.message_handler(commands=['schedule_compare'])
def compareSchedule(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Send me username you want to compare with")
    bot.register_next_step_handler(message, compareUserSchedules)


def compareUserSchedules(message):
    username = message.text
    chat_id = message.chat.id
    common_lessons_temp = []
    common_lessons = []
    psql_get_user_lessons = (
        """
        SELECT lessons FROM users WHERE username = (%s);
        """
    )
    psql_select_lessons_by_id = (
        """
        SELECT name, day, time_str, time_end  FROM lessons WHERE id = (%s);
        """
    )
    conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
    cur = conn.cursor()
    cur.execute(psql_get_user_lessons, (message.chat.username,))
    schedule_main = cur.fetchone()
    schedule_main = schedule_main[0]
    cur.execute(psql_get_user_lessons, (username,))
    schedule_compare = cur.fetchone()
    schedule_compare = schedule_compare[0]
    for item in schedule_main:
        for sub_item in schedule_compare:
            if item == sub_item:
                common_lessons_temp.append(item)

    for lesson in common_lessons_temp:
        cur.execute(psql_select_lessons_by_id, (lesson,))
        common_lessons.append(cur.fetchone())
    common_lessons = divide(common_lessons)
    cur.close()
    conn.commit()
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        string = ''
        for lesson in common_lessons[day]:
            temp_string = '[' + str(lesson[0]) + ']    ' + str(lesson[2]) + ' do ' + str(lesson[3])
            string = str(string) + '\n' + str(temp_string)
        bot.send_message(message.chat.id, '[' + str(day) + ']\n' +
                         str(string)
                         )


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
    ??ommand = (
        """
        DROP TABLE IF EXISTS user_lessons;
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS lessons;
        """
    )
    try:
        conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
        cur = conn.cursor()
        if message.chat.id == 455277222:
            cur.execute(??ommand)
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


@bot.message_handler(commands=['show_user'])
def showUserInfo(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "What user do you want me to show?")
    bot.register_next_step_handler(message, getUserInfo)



@bot.message_handler(commands=['add_user'])
def createUser(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     "Send me your name (and optional surname)(separate your inputs by space in format NAME SURNAME)")
    bot.send_message(chat_id, "Example: \n Bob \n Bob Gray")
    bot.register_next_step_handler(message, get_user_data)


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
                        time_str INTEGER NOT NULL,
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
            CONSTRAINT fk_users FOREIGN KEY(user_id) REFERENCES users(id),
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

    chat_id = message.chat.id


def get_user_data(message):
    chat_id = message.chat.id
    userData = transformUserData(message)
    try:
        os.mkdir(os.path.join('users/',  message.chat.username))
        os.chmod('users/' + message.chat.username, 0o0777)
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
                print(userData)
                cur.execute(command, (chat_id, message.chat.username, userData))
            elif len(userData) == 2:
                print(userData)
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
    select = (
        """
        SELECT * FROM users WHERE username = (%s);
        """
    )
    selector = (
        """
        SELECT name, day, time_str, time_end  FROM lessons WHERE id = (%s);
        """
    )
    try:
        result = 0
        conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
        cur = conn.cursor()
        if checkIfTablesExists(conn, cur):
            cur.execute(select, (message.text, ))
            result = cur.fetchone()
            result = list(result)
            element = []
            for item in result[4]:
                cur.execute(selector, (item,))
                element.append(cur.fetchone())
            result.append(element)
            result[5] = divide(result[5])
        else:
            bot.send_message(message.chat.id, "Tables are not exist")
        cur.close()
        conn.commit()
        if not result[3]:
            result[3] = ' '
        bot.send_message(message.chat.id,
                         "Chat ID  " + str(result[0]) +
                         "\nUsername  " + result[1] +
                         "\nName  " + result[2] +
                         "\nLast Name  " + result[3] +
                         "\nLessons: " + str(result[4])
                         )

        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            string = ''
            for lesson in result[5][day]:
                temp_string = '[' + str(lesson[0]) + ']    ' + str(lesson[2]) + ' do ' + str(lesson[3])
                string = str(string) + '\n' + str(temp_string)
            bot.send_message(message.chat.id, '[' + str(day) + ']\n' +
                             str(string)
                             )
    except (Exception, psycopg2.DatabaseError) as error:
        bot.send_message(message.chat.id, "Error: ")
        bot.send_message(message.chat.id, error)
    finally:
        if conn is not None:
            conn.close()


def add_user_schedule(message):
    chat_id = message.chat.id
    directory = 'users'
    username_dir = message.chat.username
    schedule = saveFile(message, directory, username_dir)
    command = (
        """
        UPDATE users set lessons = (%s) WHERE id = (%s);
        """
    )
    try:
        conn = psycopg2.connect(dbname='testtable', user='remar', password='REmark0712', host='localhost', port='5432')
        cur = conn.cursor()
        if checkIfTablesExists(conn, cur):
            bd_schedule_array = []
            for item in schedule['indexes']:
                for z in ['0|', '1|', '2|', '3|', '4|']:
                    item = item.replace(z, '')
                bd_schedule_array.append(int(item))
            cur.execute(command, (bd_schedule_array, chat_id))
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
    if file_name == 'schedule.json':
        open(dir + '/' + file_name, 'wb').write(response.content)
        with open(dir + '/' + file_name) as file:
            schedule = json.loads(file.read())
    elif file_name == message.chat.username:
        open(dir + '/' + message.chat.username + '/' + message.chat.username + '.json', 'wb').write(response.content)
        with open(dir + '/' + message.chat.username + '/' + message.chat.username + '.json') as file:
            schedule = json.loads(file.read())
    return schedule


def divide(lessons):
    sorted_day = {'Monday': '', 'Tuesday': '', 'Wednesday': '', 'Thursday': '', 'Friday': ''}
    for week_day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        concrete_day = []
        for lesson in lessons:
            if week_day == lesson[1]:
                concrete_day.append(lesson)
        sorted_day[week_day] = concrete_day
        sorted_day[week_day].sort(key=getIndex)
    return sorted_day


def getIndex(arr):
    return arr[2]


bot.infinity_polling()