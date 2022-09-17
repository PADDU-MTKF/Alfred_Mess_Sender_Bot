from ast import BoolOp
from calendar import timegm
from dotenv import load_dotenv
import requests as req

from tkinter import NO
from MyDb import *
import os
import telebot
import time
import datetime
import pytz
from datetime import datetime as dt
from datetime import timedelta
from dateutil import relativedelta
import threading
TZ = pytz.timezone("Canada/Pacific")


load_dotenv()

API_KEY = os.getenv('API_KEY')
CID = os.getenv('CID')

bot = telebot.TeleBot(API_KEY)


# tables :- pool_log,gp_list,task,status_sched

POLL_LIST = {1: ["Which task do you want to perform ?", ['View message that is been sent',
                                                         'Stop sending messages',
                                                         'Start sending messages',
                                                         'Set-Up']],
             2: "Select the Groups that you want to Use ...",
             3: ["Interval of message..", ['Weekly', 'Monthly']],
             4: ["Select days to send message", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
             }


def check_and_send():
    while True:
        try:
            time.sleep(10)
            sh_data = get_all(CID, "status_sched")
            if (str(type(sh_data)) == "<class 'sqlite3.OperationalError'>"):
                time.sleep(10)
                continue

            tday = dt.now(TZ)
            for group in sh_data:
                # print('here')
                # print(group[6])
                # print(dt.fromisoformat(group[6]))
                if group[1] == 1 and dt.fromisoformat(group[6]) <= tday:
                    given_hour = group[2]
                    given_minute = group[3]
                    given_date = group[4]
                    given_days = group[5]
                    #print(given_date, given_days, given_hour, given_minute)

                    if given_date != 'NULL':
                        next_date_time = tday + relativedelta.relativedelta(day=given_date,
                                                                            months=1, hour=given_hour, minute=given_minute)

                    else:
                        given_days = eval(given_days)
                        for i in range(1, 8):
                            next_date_time = tday + \
                                relativedelta.relativedelta(
                                    hour=given_hour, minute=given_minute, days=i)
                            if next_date_time.strftime('%A') in given_days and next_date_time > tday:
                                break

                    if tday <= dt.fromisoformat(group[6])+timedelta(minutes=10):
                        ms = group[7]
                        ms = ms.replace(" <br>", '\n')
                        img = group[8]
                        id = group[0]

                        if img == "NULL":
                            bot.send_message(id, ms)

                        # try *******************************************************
                        else:
                            with open('sendimgtemp.png', 'wb') as fil:
                                fil.write(img)

                            with open('sendimgtemp.png', 'rb') as fil:
                                try:
                                    if ms == "NULL":
                                        bot.send_photo(id, photo=fil)
                                    else:
                                        bot.send_photo(
                                            id, photo=fil, caption=ms)
                                except Exception as e:
                                    print(e)

                            os.remove('sendimgtemp.png')

                    a = update(
                        CID, "status_sched", f"next_date_time='{str(next_date_time)}'", f"gid={group[0]}")

                    #print(a, next_date_time)

        except:
            pass


# *****************************************************************************************************************************************************************


def permission(message):
    if str(message.chat.id) == CID:
        return True
    return False


def log_poll(res):
    Db = str(res.chat.id)

    DATA_LIST = [
        (res.id, 0)
    ]

    check = add_data(Db, "poll_log", DATA_LIST)

    if check != True:

        COL_LIST = [
            # extra is full command
            {'col_name': 'poll_id', 'col_type': 'int',
                'extra': 'primary key not null'},
            {'col_name': 'temp', 'col_type': 'int'}
        ]
        check = create_table(Db, "poll_log", COL_LIST)
        check = add_data(Db, "poll_log", DATA_LIST)


def get_poll_log():
    Db = str(CID)

    result = get_all(Db, "poll_log", "poll_id")

    if result == [] or result == False:
        return False
    return result


def delete_poll_log(mid=0):
    delete(CID, "poll_log")
    if mid == 0:
        return

    bot.delete_message(CID, mid)
    #bot.delete_message(CID, mid[0][0]-1)


def insert_task(val):
    Db = CID
    DATA_LIST = [
        (str(val), 0)
    ]

    check = add_data(Db, "task", DATA_LIST)

    if check != True:

        COL_LIST = [
            # extra is full command
            {'col_name': 'value', 'col_type': 'str'},
            {'col_name': 'temp', 'col_type': 'int'}
        ]
        check = create_table(Db, "task", COL_LIST)
        check = add_data(Db, "task", DATA_LIST)


def clear_task():
    delete(CID, 'task')


def send_my_poll(ques, opt, all=False):
    if not all:
        res = bot.send_poll(
            CID, ques, opt)
    else:
        res = bot.send_poll(CID, ques, opt, allows_multiple_answers=True)

    log_poll(res)


def get_gp():
    result = get_all(CID, 'gp_list')
    if 'no such table' in str(result):
        result = []
    return result


def check_mess(message, result, time_date):
    gpl = eval(result[1][0])

    if message.photo == None:
        send_text = message.text
        im = 'NULL'
    else:
        file_id = message.photo[-1].file_id
        if message.caption != None:
            send_text = message.caption
        else:
            send_text = 'NULL'

        file = bot.get_file(file_id)
        # print(file.file_path)

        link = 'https://api.telegram.org/file/bot'+API_KEY+'/'+file.file_path
        r = req.get(link, allow_redirects=True)
        file_name = "temp_will_delete.png"
        with open(file_name, 'wb') as f:
            f.write(r.content)

        with open(file_name, 'rb') as f:
            im = f.read()
        os.remove(file_name)

    try:
        send_text = send_text.replace('\n', " <br>")
    except:
        pass

    gid = []
    for each in gpl:
        gid.append(get_one(CID, "gp_list", f"title='{each}'", "gid")[0][0])

    # print(time_date)

    Db = CID
    for each in gid:

        DATA_LIST = [
            (each, 1, time_date['hour'], time_date['minute'], time_date['date'],
             str(time_date['days']), str(time_date['next_date_time']), send_text, im)
        ]

        delete(CID, 'status_sched', f"gid={each}")
        check = add_data(Db, "status_sched", DATA_LIST, flag=1)
        # print(check)

        if check != True:

            COL_LIST = [
                # extra is full command
                {'col_name': 'gid', 'col_type': 'str',
                    'extra': 'primary key not null'},
                {'col_name': 'status', 'col_type': 'int', 'extra': 'default 1'},
                {'col_name': 'hour', 'col_type': 'int'},
                {'col_name': 'minute', 'col_type': 'int'},
                {'col_name': 'date', 'col_type': 'int', 'extra': 'default None'},
                {'col_name': 'days', 'col_type': 'str', 'extra': 'default None'},
                {'col_name': 'next_date_time', 'col_type': 'TIMESTAMP'},
                {'col_name': 'messg', 'col_type': 'text', 'extra': 'default None'},
                {'col_name': 'img', 'col_type': 'BLOP', 'extra': 'default None'}
            ]
            check = create_table(Db, "status_sched", COL_LIST)
            check = add_data(Db, "status_sched", DATA_LIST, flag=1)

    clear_task()
    bot.send_message(CID, "Set-Up  Complete .....")


def check_day(message, interval, result):
    given_time = message.text
    today = dt.now(TZ)

    if interval == 'm':
        try:
            given_time = given_time.split()

            given_date = int(given_time[0])
            given_hour = int(given_time[1].split(':')[0])
            given_minute = int(given_time[1].split(':')[1])

            next_date_time = today + relativedelta.relativedelta(day=given_date,
                                                                 months=0, hour=given_hour, minute=given_minute)
            # print(type(next_date_time))
            # print(type(today))

            if next_date_time < today:
                next_date_time = today + relativedelta.relativedelta(day=given_date,
                                                                     months=1, hour=given_hour, minute=given_minute)

            time_data = {'formate': 'm', 'days': 'NULL', 'date': given_date,
                         'hour': given_hour, 'minute': given_minute, 'next_date_time': next_date_time}
            # print(nextmonth)

        except Exception as e:
            msg = bot.send_message(CID, "Try again with proper format ...")
            bot.register_next_step_handler(msg, check_day, 'm', result)
            return
            # print(e)

    elif interval == 'w':
        try:
            given_hour = int(given_time.split(':')[0])
            given_minute = int(given_time.split(':')[1])
            given_days = eval(result[3][0])

            for i in range(0, 8):
                next_date_time = today + \
                    relativedelta.relativedelta(
                        hour=given_hour, minute=given_minute, days=i)
                if next_date_time.strftime('%A') in given_days and next_date_time > today:
                    break

            time_data = {'formate': 'w', 'days': given_days, 'date': 'NULL',
                         'hour': given_hour, 'minute': given_minute, 'next_date_time': next_date_time}

        except Exception as e:
            msg = bot.send_message(CID, "Try again with proper format ...")
            bot.register_next_step_handler(msg, check_day, 'w', result)
            return

    msg = bot.send_message(CID, "Send the message that you want to Send ...")
    bot.register_next_step_handler(msg, check_mess, result, time_data)


# ********************************************************************************** VIEW img*******************************************

def next_task(op=1):
    result = get_all(CID, 'task')
    if 'no such table' in str(result) or result == []:
        return
    task = result[0][0]
    groups = eval(result[1][0])
    # print(result)
    if op == 2:
        try:
            interval = result[2][0]
            if interval == POLL_LIST[3][1][0]:
                send_my_poll(POLL_LIST[4][0], POLL_LIST[4][1], True)

            elif interval == POLL_LIST[3][1][1]:
                text = '''On which date and on what time do you want to send the message?\n\n( date HH:MM ) use 24 hr format \nEg. 27 19:35\n\n( to send on every 27th of the month at 19:35 ) \n\nmake sure not to give extra spaces between date and time'''

                msg = bot.send_message(CID, text)
                bot.register_next_step_handler(msg, check_day, 'm', result)

        except:
            pass

    elif op == 3:
        text = '''At what time do you want to send the message ?\n\n( HH:MM ) use 24 hr format \nEg. 19:35'''

        msg = bot.send_message(CID, text)
        bot.register_next_step_handler(msg, check_day, 'w', result)

    elif task == 'Set-Up':
        send_my_poll(POLL_LIST[3][0], POLL_LIST[3][1])

    else:
        for each in groups:
            gid = get_one(CID, "gp_list", f"title='{each}'", "gid")[0][0]
            check = get_all(CID, "status_sched", 'gid')

            #print(type(check) == "<class 'sqlite3.OperationalError'>")
            if check == [] or (str(type(check)) == "<class 'sqlite3.OperationalError'>"):
                clear_task()
                bot.send_message(CID, f"{each} is not yet Set up ......")
                continue
            temp = []
            for l in check:
                temp.append(l[0])

            if gid not in temp:
                clear_task()
                bot.send_message(CID, f"{each} is not yet Set up ......")
                continue

            if task == 'View':

                res = get_one(
                    CID, "status_sched", f"gid='{gid}'", "status,hour,minute,date,days,messg,img")[0]

                if res[0] == 1:
                    status = 'ACTIVE'
                else:
                    status = 'NOT ACTIVE'

                tim = f"{res[1]}:{res[2]}"

                dat = res[3]
                days = res[4]
                mssg = str(res[5])
                mssg = mssg.replace(" <br>", '\n')
                img = res[6]

                if dat != 'NULL':
                    ss = f"{dat} of every Month at {tim}"
                else:
                    days = eval(days)

                    d = ""
                    for i in range(len(days)):

                        d += days[i]
                        if i != len(days)-1:
                            d += ','

                    ss = f"{d} at {tim}"

                tex = f"GROUP  :- {each}\nSTATUS :- {status}\n\nSCHEDULE ON ...\n\n\t\t\t {ss}\n\n\n Message Sent is below ..."

                bot.send_message(CID, tex)

                if img == "NULL":
                    bot.send_message(CID, mssg)

                # try *******************************************************
                else:
                    with open('sendimgtemp.png', 'wb') as fil:
                        fil.write(img)

                    with open('sendimgtemp.png', 'rb') as fil:
                        if mssg == "NULL":
                            bot.send_photo(CID, photo=fil)
                        else:
                            bot.send_photo(CID, photo=fil, caption=mssg)

                    os.remove('sendimgtemp.png')

                clear_task()

            elif task == 'Stop':
                update(CID, 'status_sched', "status=0", f"gid={gid}")
                bot.send_message(CID, "Done ....")
                clear_task()

            elif task == 'Start':
                update(CID, 'status_sched', "status=1", f"gid={gid}")
                bot.send_message(CID, "Done ....")
                clear_task()

    return


def gp_poll():
    r = get_gp()
    if r == []:
        bot.send_message(CID, "The bot is not in any group ...")
        clear_task()
    elif len(r) == 1:
        task = []
        task.append(r[0][1])
        insert_task(task)
        next_task()

    else:
        options = []
        for each in r:
            gname = each[1]
            options.append(gname)
        send_my_poll(POLL_LIST[2], options, True)

    return


# *********************************************************************************************************************************************************************

@bot.message_handler(commands=['cancel'], func=permission)
def cancle(message):
    clear_task()
    delete_poll_log()
    bot.send_message(message.chat.id, 'Done ..')


@bot.message_handler(commands=['mytime'], func=permission)
def givetime(message):
    t = dt.now(TZ)
    text = f"Date : {t.date()}\nDay  : {t.strftime('%A')}\nTime : {t.time()}"
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['help', 'start'], func=permission)
def help(message):
    text = "To see available options and perform tasks , start a chat with the bot by sending anything ...\n\n If by any chance you are unable to get the options , then Try using /cancel \n\n use /mytime to verify your time \n\n You can always contact the developer for any help :)"
    bot.send_message(message.chat.id, text)


@bot.poll_handler(func=lambda pollAnswer: True)
def answer(pollAnswer):
    if(pollAnswer.is_closed):
        return
    ques = pollAnswer.question

    if ques == POLL_LIST[1][0]:
        task = None
        for each in pollAnswer.options:
            if each.voter_count == 1:
                task = each.text
                break

        if task != None and task in POLL_LIST[1][1]:
            mid = get_poll_log()
            # print(mid)
            try:
                bot.stop_poll(CID, mid)
                delete_poll_log(mid)
                task = task.split()[0]
                insert_task(task)
                # print(task)
                gp_poll()
                return
            except:
                pass

    elif ques == POLL_LIST[2]:
        task = []
        for each in pollAnswer.options:
            if each.voter_count == 1:
                task.append(each.text)
        if task != []:
            mid = get_poll_log()
            # print(mid)
            try:
                bot.stop_poll(CID, mid)
                delete_poll_log(mid)
                insert_task(task)
                next_task()
                return
            except:
                pass

    elif ques == POLL_LIST[3][0]:
        task = None
        for each in pollAnswer.options:
            if each.voter_count == 1:
                task = each.text
                break

        if task != None and task in POLL_LIST[3][1]:
            mid = get_poll_log()
            # print(mid)
            try:
                bot.stop_poll(CID, mid)
                delete_poll_log(mid)
                insert_task(task)
                # print(task)
                next_task(2)
                return
            except:
                pass

    elif ques == POLL_LIST[4][0]:
        task = []
        for each in pollAnswer.options:
            if each.voter_count == 1:
                task.append(each.text)
        if task != []:
            mid = get_poll_log()
            # print(mid)
            try:
                bot.stop_poll(CID, mid)
                delete_poll_log(mid)
                insert_task(task)
                next_task(3)
                return
            except:
                pass

    delete(CID, "poll_log")


@bot.message_handler(func=permission, content_types=['photo', 'text'])
def echo_all(message):

    result = get_all(CID, "poll_log")
    if result != [] and result != False and 'no such table' not in str(result):
        return
    options = POLL_LIST[1][1]
    res = bot.send_poll(
        message.chat.id, POLL_LIST[1][0], options)
    log_poll(res)


@bot.my_chat_member_handler(func=lambda msg: True)
def join(message):
    gid = message.chat.id
    g_title = message.chat.title
    status = message.new_chat_member.status

    if status in ['kicked', 'left']:
        delete(CID, 'gp_list', f"gid={gid}")
        delete(CID, 'status_sched', f"gid={gid}")

    else:
        Db = CID
        DATA_LIST = [
            (gid, g_title)
        ]

        check = add_data(Db, "gp_list", DATA_LIST)

        if check != True:

            COL_LIST = [
                # extra is full command
                {'col_name': 'gid', 'col_type': 'str',
                    'extra': 'primary key not null'},
                {'col_name': 'title', 'col_type': 'str'}
            ]
            check = create_table(Db, "gp_list", COL_LIST)
            check = add_data(Db, "gp_list", DATA_LIST)


# clear_task()
# delete_poll_log()
# bot.polling()

th0 = threading.Thread(target=check_and_send)
th0.start()

while True:
    time.sleep(0.002)
    try:
        clear_task()
        delete_poll_log()
        print("The Bot is running ......\n\n")
        bot.polling()
    except:
        print('Retrying .....\n\n')
        time.sleep(5)
