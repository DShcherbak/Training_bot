import telebot
import multiprocessing
import json
from User import *
from Exercise import *
from databases import *

# TODO: New exer with old name = update

FIFTEEN = 15 * 60
bot = telebot.TeleBot(config.token, threaded=False)
admin_bot = telebot.TeleBot(config.admin_token, threaded=False)
user_database = config.user_database
admin_id = config.admin_id
users = {}
exercises = []
changed_exercise = []


# #####################################

def merge_libraries(new_json):
    global users
    admin_users = {}
    admin_exercise = {}
    empty_ar = []
    for user in users:
        empty_ar.append((user, users[user]))
    admin_users.update(empty_ar)  # admin_users == users
    with open(new_json, "r") as read_file:
        encoded_users = json.load(read_file)
    for encoded_user in encoded_users:
        user_id = int(encoded_user["id"])
        if int(encoded_user["id"]) in admin_users.keys():
            for tr in range(16):
                for ex in range(int(encoded_user["train|" + str(tr) + "|size"])):
                    while tr not in range(len(admin_users[user_id].trainings)):
                        admin_users[user_id].trainings.append(Training())
                    exer_mask = "train|" + str(tr) + "|exer|" + str(ex + 1) + "|"
                    if ex not in range(len(admin_users[user_id].trainings[tr].exercises)):
                        new_ex = Exercise(admin_exercise[encoded_user[exer_mask + "name"]])
                        admin_users[user_id].trainings[tr].exercises.append(new_ex)
                    admin_users[user_id].trainings[tr].exercises[ex].name = encoded_user[exer_mask + "name"]
                    admin_users[user_id].trainings[tr].exercises[ex].repeat = int(encoded_user[exer_mask + "repe"])
                    admin_users[user_id].trainings[tr].exercises[ex].temp = encoded_user[exer_mask + "temp"]
    save_plans_into_database(db_file, admin_users)
    read_plans_from_database(db_file, users)


@admin_bot.message_handler(commands=['reload'])
def reload(message):
    global users
    if str(message.from_user.id) in admin_id:
        read_users_from_database(db_file, users)
        admin_bot.send_message(message.from_user.id, "Successfully reloaded")
    else:
        admin_bot.send_message(message.from_user.id, "You don't have admin rights" + message.from_user.id)
        print(message.from_user.id)


@admin_bot.message_handler(commands=['get'])
def send_data(message):
    global users
    if str(message.from_user.id) == admin_id:
        admin_bot.send_message(message.from_user.id, "Your database:")
        encoded_users = []
        for user in users:
            encoded_users.append(users[user].encode_to_json())
        with open(user_database, "w") as write_file:
            json.dump(encoded_users, write_file)
        admin_bot.send_message(message.from_user.id, "Take this")
        doc = open(user_database, "rb")
        admin_bot.send_document(message.from_user.id, doc)
        doc.close()
    else:
        admin_bot.send_message(message.from_user.id, "You don't have admin rights" + message.from_user.id)
        print(message.from_user.id)


@admin_bot.message_handler(content_types=['document'])
def get_text_messages(message):
    print(message.from_user.id)
# TODO : finish this function


@admin_bot.message_handler(commands=['new_exercise'])
def new_exercise(message):
    global exercises
    if str(message.from_user.id) in admin_id:
        admin_bot.send_message(message.from_user.id, 'Название упражнения: ')
        new_exercise_id = create_exercise(db_file, ("no name", "no link", "no description"))
        exercise = ExercisePattern(new_exercise_id)
        exercises.update([(new_exercise_id, exercise)])
        admin_bot.register_next_step_handler(message, get_exercise_name)
    else:
        pass


def get_exercise_name(message):
    admin_bot.send_message(message.from_user.id, "Описание упражнения: ")
    admin_exercise = []
    last_id = len(admin_exercise) - 1
    admin_exercise[last_id].name = message.text
    admin_exercise[last_id].id = last_id
    admin_bot.register_next_step_handler(message, get_exercise_desc)


def get_exercise_desc(message):
    admin_bot.send_message(message.from_user.id, "Ссьілка на пример упражнения: ")
    admin_exercise = []
    last_id = len(admin_exercise) - 1
    admin_exercise[last_id].desc = message.text
    save_exercises_into_database()  # TODO: Is it necessary
    admin_bot.register_next_step_handler(message, get_link)


def get_link(message):
    admin_bot.send_message(message.from_user.id, "OK, вот шаблон упражения")
    admin_exercise = {}
    last_id = len(admin_exercise) - 1
    admin_exercise[last_id].link = message.text
    save_exercises_into_database()
    admin_bot.send_message(message.from_user.id, admin_exercise[id].to_message())


#########################################


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
    global users
    bot.send_message(message.from_user.id, talking.see_you)
    user_id = message.from_user.id
    users[user_id].nickname = message.text
    users[user_id].trainings = []
    create_user(db_file, users[user_id])


@bot.message_handler(commands=['train'])
def send_hello(message):
    global users
    user_id = message.from_user.id
    if user_id not in users.keys():
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
            # TODO: update_this_user (changed_users.append(('upd', user_id)))
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
        time.sleep(20 * 60)  # 15*60

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
        # description = user.get_exercise()
        user.current_exercise += 1


if __name__ == "__main__":
    db_file = "bot.db"
    read_exercises_from_database(db_file, exercises)
    read_users_from_database(db_file, users)
    for key in users:
        print(users[key])
    admin_polling = multiprocessing.Process(target=admin_bot.polling)
    print("Hi")
    admin_polling.start()
    print("there")
'''
    changed_users = []
    exercises[1].name = "a"
    save_exercises_into_database(connection,exercises,[1])
    #select_all_exercises(connection)
    read_exercises_from_database(connection, exercises)
    read_users_from_database(connection, users)
    print(users)
    print("Polling")
    bot_polling = multiprocessing.Process(target=bot.polling)
    #server_check = multiprocessing.Process(target=how_are_you)
    bot_polling.start()
    print("Polling")
    bot.send_message(admin_id, "Hello, admin")
    bot.send_message(admin_id, bot.get_me().id)
    #server_check.start()
    #admin_polling.start()
'''
