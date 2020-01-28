import telebot
import json
from User import *
from Exercise import *


bot = telebot.TeleBot('1054698181:AAEmAqgJ_pc6P7Hbd6XWN2Bb-MJzxS4os1U')
user_database = "user_database.json"
exercise_database = "exercise_database.json"
url_training = ""
users = {}
exercises = {}


def read_from_database():
    global users
    with open(user_database, "r") as read_file:
        encoded_users = json.load(read_file)
    for encoded_user in encoded_users:
        user = User()
        user.decode_from_json(encoded_user)
        users.update([{user.id, user}])


def save_users():
    global users
    encoded_users = []
    for user in users:
        encoded_users.append(users[user].encode_to_json())
    with open(user_database, "w") as write_file:
        json.dump(encoded_users, write_file)


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
    pre_training = 'Починаємо тренування!\n Не забудь зробити розминку, щоб уникнути травм! Приклад розминки:'
    pre_training += url_training
    bot.send_message(user_id, pre_training)
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_go = telebot.types.InlineKeyboardButton(text = 'Почати тренування', callback_data='go')
    key_cancel = telebot.types.InlineKeyboardButton(text='Скасувати тренування', callback_data='cancel')
    keyboard.add(key_go)
    keyboard.add(key_cancel)
    bot.send_message(user_id, text=pre_training, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def next_exercise(call):
    global users

    user_id = call.from_user.id
    bot.delete_message(call.from_user.id, call.message.message_id)
    if call.data == 'cancel':
        bot.send_message(user_id, 'Добре, займаємось іншим разом')
    else:
        user = users[user_id]
        description = user.get_exercise()
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_next = telebot.types.InlineKeyboardButton(text='Наступна вправа', callback_data='next')
        key_cancel = telebot.types.InlineKeyboardButton(text='Припинити тренування', callback_data='cancel')
        keyboard.add(key_next)
        keyboard.add(key_cancel)
        bot.send_message(user_id, text=description, reply_markup=keyboard)


bot.polling(none_stop=True, interval=0)
