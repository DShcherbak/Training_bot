import telebot
import multiprocessing
import json
from User import *
from Exercise import *
from databases import *
from git_ignore.admin_bot import *

# TODO: New exer with old name = update

FIFTEEN = 15 * 60
bot = telebot.TeleBot(config.token, threaded=False)
user_database = config.user_database
exercise_database = config.exercise_database
connection = None
users = {}
exercises = {}
changed_users = []
changed_exercise = []
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
                while not tr in range(len(users[user_id].trainings)):
                    users[user_id].trainings.append(Training())
                for ex in range(int(encoded_user["train|" + str(tr) + "|size"])):

                    exer_mask = "train|" + str(tr) + "|exer|" + str(ex + 1) + "|"
                    if not ex in range(len(users[user_id].trainings[tr].exercises)):
                        users[user_id].trainings[tr].exercises.append(
                            Exercise(exercises[encoded_user[exer_mask + "name"]]))
                    users[user_id].trainings[tr].exercises[ex].name = encoded_user[exer_mask + "name"]
                    users[user_id].trainings[tr].exercises[ex].repeat = int(encoded_user[exer_mask + "repe"])
                    users[user_id].trainings[tr].exercises[ex].temp = encoded_user[exer_mask + "temp"]


@bot.message_handler(commands=['start'])
def send_hello(message):
    global users
    user_id = message.from_user.id
    if user_id in users:
        bot.send_message(user_id, talking.greetings)
    else:
        bot.send_message(message.from_user.id, talking.first_hello)
        bot.register_next_step_handler(message, get_name)


def get_name(message):
    bot.send_message(message.from_user.id, talking.nickname)
    global users
    user_id = message.from_user.id
    users[user_id] = User()
    users[user_id].full_name = message.text
    users[user_id].id = user_id
    bot.register_next_step_handler(message, get_nick)


def get_nick(message):
    bot.send_message(message.from_user.id, talking.see_you)
    global users
    user_id = message.from_user.id
    users[user_id].nickname = message.text
    users[user_id].trainings = []
    changed_users.append(('new', user_id))


@bot.message_handler(commands=['train'])
def send_hello(message):
    global users
    user_id = message.from_user.id
    if not user_id in users.keys():
        bot.send_message(user_id, talking.ask_start)
        return
    if users[user_id].finished():
        bot.send_message(user_id, talking.last_train)
        return
    pre_training = talking.start_train
    pre_training += "@@@"
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_go = telebot.types.InlineKeyboardButton(text=talking.button_start, callback_data='.go')
    key_cancel = telebot.types.InlineKeyboardButton(text=talking.button_cancel, callback_data='.cancel')
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
        bot.send_message(user_id, talking.skip)
        user.let_go()
    else:
        description = user.get_exercise()
        if description == talking.last_exercise:
            user.current_exercise = 0
            user.current_training += 1
            changed_users.append(('upd', user_id))
        else:
            user.current_exercise += 1
        keyboard = telebot.types.InlineKeyboardMarkup()

        key_next = telebot.types.InlineKeyboardButton(text=talking.button_next, callback_data='.next')
        key_cancel = telebot.types.InlineKeyboardButton(text=talking.button_cancel, callback_data='.cancel')
        keyboard.add(key_next)
        keyboard.add(key_cancel)
        bot.send_message(user_id, text=description, reply_markup=keyboard)


def how_are_you():
    global users
    while True:
        time.sleep(5)  # 15*60
        # update users
        need_update = []
        print("hello")
        for p in changed_users:
            if p[0] == 'new':
                create_user(connection, user[p[1]])
            else:
                need_update.append(p[1])
        save_users_into_database(connection, users, need_update)


        #check users
        for user_key in users:
            user = users[user_key]
            if user.timeout():
                if not user.status == "Sleeping":
                    bot.send_message(user.id, user.nickname + talking.go_train)
                    bot.send_message(admin_id, "Пользователь " + user.full_name + " (" + user.nickname + ") " +
                                     "давно не занимался!")
                    user.check_time += 60 * 60 * 4
                elif user.status == "Training":
                    description = talking.continue_train
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    key_go = telebot.types.InlineKeyboardButton(text=talking.button_next, callback_data='!next')
                    key_cancel = telebot.types.InlineKeyboardButton(text=talking.button_cancel, callback_data='!cancel')
                    keyboard.add(key_go)
                    keyboard.add(key_cancel)
                    bot.send_message(user.id, text=description, reply_markup=keyboard)
                    user.check_time += 60 * 30
                    user.status = "Breaking"
                elif user.status == "Breaking":
                    bot.send_message(user.id, talking.skip)
                    user.let_go()


@bot.callback_query_handler(func=lambda call: call.data[0] == '!')
def next_exercise(call):
    global users
    user_id = call.from_user.id
    user = users[user_id]
    user.status = "Training"
    user.check_time = time.time() + FIFTEEN
    bot.delete_message(call.from_user.id, call.message.message_id)
    if call.data == '!cancel':
        bot.send_message(user_id, talking.skip)
        user.let_go()
    else:
        description = user.get_exercise()
        user.current_exercise += 1
        keyboard = telebot.types.InlineKeyboardMarkup()
        if description == talking.last_exercise:
            user.current_exercise = 0
            user.current_training += 1
            save_users()
        else:
            key_next = telebot.types.InlineKeyboardButton(text=talking.button_next, callback_data='.next')
            key_cancel = telebot.types.InlineKeyboardButton(text=talking.button_cancel, callback_data='.cancel')
            keyboard.add(key_next)
            keyboard.add(key_cancel)
        bot.send_message(user_id, text=description, reply_markup=keyboard)


if __name__ == "__main__":
    connection = create_connection("bot.db")
    read_exercises_from_database(connection, exercises)
    read_users_from_database(connection, users)

    exercises[1].name = "a"
    save_exercises_into_database(connection,exercises,[1])
    #select_all_exercises(connection)
    read_exercises_from_database(connection, exercises)
    print("Polling")
    bot_polling = multiprocessing.Process(target=bot.polling)
    server_check = multiprocessing.Process(target=how_are_you)
    #admin_polling = multiprocessing.Process(target=admin_bot.polling)
    bot_polling.start()
    print("Polling")
    bot.send_message(admin_id, "Hello, admin")
    bot.send_message(admin_id, bot.get_me().id)
    server_check.start()
    #admin_polling.start()

