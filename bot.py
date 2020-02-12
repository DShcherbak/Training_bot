import telebot
import time
import multiprocessing
import config
import json
from User import *
from Exercise import *


TWODAYS = 48 * 60 * 60
FIFTEEN = 15*60
bot = telebot.TeleBot(config.token,threaded=False)
user_database = config.user_database
exercise_database = config.exercise_database
url_training = ""
users = {}
exercises = {}
admin_id = config.admin_id

def read_from_database():
    global users, exercises, number_exercises
    with open(user_database, "r") as read_file:
        encoded_users = json.load(read_file)
    for encoded_user in encoded_users:
        user = User()
        user.decode_from_json(encoded_user)
        if user.id in users.keys():
            user.current_training = users[user.id].current_training
            user.current_exercise = users[user.id].current_exercise
        users.update([{user.id, user}])
    with open(exercise_database, "r") as read_file:
        encoded_exercises = json.load(read_file)
    for encoded_exercise in encoded_exercises:
        exercise = ExercisePattern()
        exercise.decode_from_json(encoded_exercise)
        exercises.update([{exercise.name, exercise}])
    number_exercises = len(exercises)
    print(bot.get_me())


def merge_JSON(old_JSON, new_JSON):
    global users
    with open(old_JSON, "r") as read_file:
        encoded_users = json.load(read_file)
    for encoded_user in encoded_users:
        user = User()
        user.decode_from_json(encoded_user)
        users.update([{user.id, user}])
    with open(new_JSON, "r") as read_file:
        encoded_users = json.load(read_file)
    for encoded_user in encoded_users:
        user_id = int(encoded_user["id"])
        if (int(encoded_user["id"]) in users.keys()):
            for tr in range(2):
                for ex in range(int(encoded_user["train|" + str(tr) + "|size"])):
                    while not tr in range(len(users[user_id].trainings)):
                        users[user_id].trainings.append(Training())
                    exer_mask = "train|" + str(tr) + "|exer|" + str(ex + 1) + "|"
                    if not ex in range(len(users[user_id].trainings[tr].exercises)):
                        users[user_id].trainings[tr].exercises.append(Exercise(exercises[encoded_user[exer_mask + "name"]]))
                    users[user_id].trainings[tr].exercises[ex].name = encoded_user[exer_mask + "name"]
                    users[user_id].trainings[tr].exercises[ex].repeat = int(encoded_user[exer_mask + "repe"])
                    users[user_id].trainings[tr].exercises[ex].temp = encoded_user[exer_mask +  "temp"]


def save_users():
    global users
    encoded_users = []
    for user in users:
        encoded_users.append(users[user].encode_to_json())
    with open(user_database, "w") as write_file:
        json.dump(encoded_users, write_file)


def save_exercises():
    global exercises
    encoded_exercises = []
    for exercise_id in exercises:
        encoded_exercises.append(exercises[exercise_id].encode_to_json())
    with open(exercise_database, "w") as write_file:
        json.dump(encoded_exercises, write_file)


@bot.message_handler(commands=['start'])
def send_hello(message):
    global users
    read_from_database()
    user_id = message.from_user.id
    if user_id in users:
        bot.send_message(user_id, 'Радий знову вас чути!')
    else:
        bot.send_message(message.from_user.id, 'Привіт, дякую що написали! Мене звати Kachalka Bot, радий знайомству!')
        bot.send_message(message.from_user.id, 'Як вас звати?')
        bot.register_next_step_handler(message, get_name)


def get_name(message):
    bot.send_message(message.from_user.id, "Класне ім'я! А як мені найкраще до вас звертатися?")
    global users
    user_id = message.from_user.id
    users[user_id] = User()
    users[user_id].full_name = message.text
    users[user_id].id = user_id
    save_users()
    bot.register_next_step_handler(message, get_nick)


def get_nick(message):
    bot.send_message(message.from_user.id, "Я запам'ятаю :)\nОчікуйте план занять незабаром")
    global users
    user_id = message.from_user.id
    users[user_id].nickname = message.text
    save_users()
#    bot.register_next_step_handler(message, get_nick)


@bot.message_handler(commands=['train'])
def send_hello(message):
    global users
    user_id = message.from_user.id
    if not user_id in users.keys():
        bot.send_message(user_id, "Будь ласка, напишіть /start")
        return
    if users[user_id].finished():
        bot.send_message(user_id, 'Це було останнє тренування! Вітаю!')
        return
    pre_training = 'Починаємо тренування!\n Не забудь зробити розминку, щоб уникнути травм! Приклад розминки:'
    pre_training += url_training
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_go = telebot.types.InlineKeyboardButton(text = 'Почати тренування', callback_data='.go')
    key_cancel = telebot.types.InlineKeyboardButton(text='Скасувати тренування', callback_data='.cancel')
    keyboard.add(key_go)
    keyboard.add(key_cancel)
    bot.send_message(user_id, text=pre_training, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data[0] == '.')
def next_exercise(call):
    global users
    user_id = call.from_user.id
    user = users[user_id]
    bot.delete_message(call.from_user.id, call.message.message_id)
    if call.data == '.cancel':
        bot.send_message(user_id, 'Добре, займаємось іншим разом')
        user.check_time = time.time() + TWODAYS
    elif user.finished():
        bot.send_message(user_id, 'Це було останнє тренування! Вітаю!')
    else:
        description = user.get_exercise()
        user.current_exercise += 1
        keyboard = telebot.types.InlineKeyboardMarkup()
        if description[0:2] == "Це":
            user.current_exercise = 0
            user.current_training += 1
            save_users()
        else:
            key_next = telebot.types.InlineKeyboardButton(text='Наступна вправа', callback_data='.next')
            key_cancel = telebot.types.InlineKeyboardButton(text='Припинити тренування', callback_data='.cancel')
            keyboard.add(key_next)
            keyboard.add(key_cancel)
        bot.send_message(user_id, text=description, reply_markup=keyboard)


def how_are_you():
    global users
    while True:
        time.sleep(1) # 15*60
        for user_key in users:
            user = users[user_key]
            if user.timeout():
                user.check_time += 5
                if user.status == "Sleeping":
                    bot.send_message(user.id, user.nickname + ", час позайматися після такої перерви!")
                    bot.send_message(admin_id, "Користувач " + user.full_name + "(" + user.nickname + ")" +
                                     "давно не займався!")
                else:
                    description = "Тренування продовжуєтсья?"
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    key_go = telebot.types.InlineKeyboardButton(text='Наступна вправа', callback_data='!next')
                    key_cancel = telebot.types.InlineKeyboardButton(text='Припинити тренування', callback_data='!cancel')
                    keyboard.add(key_go)
                    keyboard.add(key_cancel)
                    bot.send_message(user.id, text=description, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data[0] == '!')
def next_exercise(call):
    global users
    user_id = call.from_user.id
    user = users[user_id]
    bot.delete_message(call.from_user.id, call.message.message_id)
    if call.data == '!cancel':
        bot.send_message(user_id, 'Добре, займаємось іншим разом')
    else:
        description = user.get_exercise()
        user.current_exercise += 1
        keyboard = telebot.types.InlineKeyboardMarkup()
        if description[0:2] == "Це":
            user.current_exercise = 0
            user.current_training += 1
            save_users()
        else:
            key_next = telebot.types.InlineKeyboardButton(text='Наступна вправа', callback_data='.next')
            key_cancel = telebot.types.InlineKeyboardButton(text='Припинити тренування', callback_data='.cancel')
            keyboard.add(key_next)
            keyboard.add(key_cancel)
        bot.send_message(user_id, text=description, reply_markup=keyboard)



if __name__ == "__main__":
    read_from_database()
    for user_key in users:
        user = users[user_key]
        user.status = "Sleeping"
        user.check_time = time.time()
    save_users()
    how_are_you()
   # bot_polling = multiprocessing.Process(target=bot.polling, args=(True,))
   # server_check = multiprocessing.Process(target=how_are_you)
   # bot_polling.start()
   # server_check.start()

