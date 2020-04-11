import telebot
import multiprocessing
import json
from User import *
from databases import *

# TODO: New exer with old name = update

FIFTEEN = 15 * 60
TWO_DAYS = 60*6*24*2
bot = telebot.TeleBot(config.token, threaded=False)
admin_bot = telebot.TeleBot(config.admin_token, threaded=False)
user_database = config.user_database
admin_id = config.admin_id
db_file = "bot.db"
# users = {}
# exercises = {}
last_message = 0
test_mode = True


# ########################################
#
#
#
#
#
# ADMIN BOT BEGIN
#
#
#
#
#
# ########################################

@admin_bot.message_handler(commands=['stop'])
def reload(message):
    global test_mode, admin_id
    if str(message.from_user.id) in admin_id:
        test_mode = True
        admin_bot.send_message(message.from_user.id, "Successfully stopped")
    else:
        admin_bot.send_message(message.from_user.id, "You don't have admin rights" + message.from_user.id)
        print(message.from_user.id)


@admin_bot.message_handler(commands=['reload'])
def reload(message):
    global test_mode, admin_id
    if str(message.from_user.id) in admin_id:
        test_mode = False
        admin_bot.send_message(message.from_user.id, "Successfully reloaded")
    else:
        admin_bot.send_message(message.from_user.id, "You don't have admin rights" + message.from_user.id)
        print(message.from_user.id)


def merge_libraries(new_json):
    print("loading file...")
    # global users
    admin_users = {}
    empty_ar = []
    plans_to_update = []
    read_users_from_database(db_file, admin_users)
    admin_users.update(empty_ar)
    print(admin_users)  # admin_users == users
    with open(new_json, "r") as read_file:
        encoded_users = json.load(read_file)
    for lib in encoded_users:
        user_id = int(lib["id"])
        print("Processing" + str(user_id))
        if user_id in admin_users.keys():
            print("ongoing")
            user = admin_users[user_id]
            all_new = False
            for t in range(int(lib["trainings"])):
                one_new = False
                while len(user.trainings) <= t:
                    user.trainings.append(Training())
                    all_new = True
                for e in range(int(lib["train|" + str(t) + "|size"])):
                    while len(user.trainings[t].exercises) <= e:
                        user.trainings[t].exercises.append(Exercise())
                        one_new = True
                    ex = user.trainings[t].exercises[e]
                    hat = "train|" + str(t) + "|exer|" + str(e)
                    _name = lib[hat + "|name"]
                    _temp = lib[hat + "|temp"]
                    _repeat = lib[hat + "|repeat"]
                    if all_new or one_new or not ((ex.name == _name) and (ex.temp == _temp) and (ex.repeat == _repeat)):
                        exercise = get_exercise_from_database(db_file, _name=_name)
                        ex_id = exercise.id
                        plans_to_update.append((user_id, t, e, ex_id, _temp, _repeat, True))
    for plan in plans_to_update:
        print(plan)
        update_current_plan(db_file, plan)


'''@admin_bot.message_handler(commands=['reload'])
def reload(message):
    #global users, exercises
    if str(message.from_user.id) in admin_id:
        read_users_from_database(db_file, users)
        read_exercises_from_database(db_file, exercises)
        read_plans_from_database(db_file, users, exercises)
        admin_bot.send_message(message.from_user.id, "Successfully reloaded")
    else:
        admin_bot.send_message(message.from_user.id, "You don't have admin rights" + message.from_user.id)
        print(message.from_user.id)'''


@admin_bot.message_handler(commands=['get'])
def send_data(message):
    users = {}
    exercises = {}
    read_users_from_database(db_file, users)
    read_exercises_from_database(db_file, exercises)
    read_plans_from_database(db_file, users, exercises, True)
    if str(message.from_user.id) in admin_id:
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
        admin_bot.send_message(message.from_user.id, "You don't have admin rights" + str(message.from_user.id))
        print(message.from_user.id)


@admin_bot.message_handler(content_types=['document'])
def get_document_messages(message):
    global test_mode
    if test_mode:
        pass
    else:
        print(message.from_user.id)
        print(message.document.file_id)
        file_info = admin_bot.get_file(message.document.file_id)
        print(file_info)
        downloaded_file = admin_bot.download_file(file_info.file_path)
        src = 'uploaded_database.json'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        admin_bot.reply_to(message, "База обновлена")
        merge_libraries(src)


@admin_bot.message_handler(commands=['new_exercise'])
def new_exercise(message):
    user_id = message.from_user.id
    if str(user_id) in admin_id:
        admin_bot.send_message(user_id, 'Название упражнения: ')
        create_exercise(db_file, ("no name", "no link", "no desc"))
        admin_bot.register_next_step_handler(message, get_exercise_name)
    else:
        pass


def get_exercise_name(message):
    admin_bot.send_message(message.from_user.id, "Описание упражнения: ")
    # exercise = get_exercise_from_database(db_file, _name="no name")
    # exercise.name = message.text
    update_exercise(db_file, _name="no name", args=(message.text, ))
    admin_bot.register_next_step_handler(message, get_exercise_desc)


def get_exercise_desc(message):
    # global exercises
    admin_bot.send_message(message.from_user.id, "Ссьілка на пример упражнения: ")
    update_exercise(db_file, _desc="no desc", args=(message.text,))
    admin_bot.register_next_step_handler(message, get_link)


def get_link(message):
    # global exercises
    admin_bot.send_message(message.from_user.id, "OK, вот шаблон упражения")
    exercise = get_exercise_from_database(db_file, _link="no link")
    exercise.link = message.text
    update_exercise(db_file, _link="no link", args=(message.text, ))
    admin_bot.send_message(message.from_user.id, exercise.to_message())


# ########################################
#
#
#
#
#
# ADMIN BOT END
#
#
#
#
#
# ########################################



@bot.message_handler(commands=['start'])
def send_hello(message):
    user_id = message.from_user.id
    user = get_user_from_database(db_file, user_id)  # users[user_id]
    if user.id >= 0:
        bot.send_message(user_id, talking.greetings)
    else:
        new_user = User(_id=user_id)
        create_user(db_file, new_user)
        bot.send_message(message.from_user.id, talking.first_hello)
        bot.register_next_step_handler(message, get_name)


def get_name(message):
    bot.send_message(message.from_user.id, talking.nickname)
    user_id = message.from_user.id
    user = get_user_from_database(db_file, user_id)  # users[user_id]
    user.full_name = message.text
    user.id = user_id
    update_user(db_file, user)
    bot.register_next_step_handler(message, get_nick)


def get_nick(message):
    bot.send_message(message.from_user.id, talking.see_you)
    user_id = message.from_user.id
    user = get_user_from_database(db_file, user_id)  # users[user_id]
    user.nickname = message.text
    update_user(db_file, user)


@bot.message_handler(commands=['train'])
def send_hello(message):
    # global users
    user_id = message.from_user.id
    user = get_user_from_database(db_file, user_id)  # users[user_id]
    get_user_plans_from_database(db_file, user, user_id)
    if user.id < 0:  # not in users.keys():
        bot.send_message(user_id, talking.ask_start)
        return
    if user.finished():
        print(user.trainings)
        print(" < ")
        print(user.current_training)
        bot.send_message(user_id, talking.last_train)
        return
    pre_training = "Тренировка номер " + str(user.current_training+1) + "\n" + talking.start_train
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_go = telebot.types.InlineKeyboardButton(text=talking.button_start, callback_data='.go')
    key_cancel = telebot.types.InlineKeyboardButton(text=talking.button_cancel, callback_data='.cancel')
    keyboard.add(key_go)
    keyboard.add(key_cancel)
    bot.send_message(user_id, text=pre_training, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data[0] == '.')
def next_exercise(call):
    user_id = call.from_user.id
    user = get_user_from_database(db_file, user_id)
    print(user_id, user.status)
    user.status = "Training"
    user.check_time += 20
    update_user(db_file, user)
    bot.delete_message(call.from_user.id, call.message.message_id)
    if call.data == '.cancel':
        bot.send_message(user_id, talking.skip)
        user.let_go()
    else:
        description = user.get_exercise()
        if description == talking.last_exercise:
            user.current_exercise = 0
            user.current_training += 1
            description = "Тренировка номер " + str(user.current_training) + " завершена!\n" + description
            description += talking.chat
            bot.send_message(user_id, description)
            user_plus_train(db_file, user_id, user.current_exercise, user.current_training)
        elif user.current_exercise == len(user.trainings[user.current_training].exercises)-1:
            user.current_exercise += 1
            keyboard = telebot.types.InlineKeyboardMarkup()
            key_end = telebot.types.InlineKeyboardButton(text=talking.button_end, callback_data='.end')
            keyboard.add(key_end)
            bot.send_message(user_id, text=description, reply_markup=keyboard)
        else:
            user.current_exercise += 1
            keyboard = telebot.types.InlineKeyboardMarkup()

            key_next = telebot.types.InlineKeyboardButton(text=talking.button_next, callback_data='.next')
            key_cancel = telebot.types.InlineKeyboardButton(text=talking.button_cancel, callback_data='.cancel')
            keyboard.add(key_next)
            keyboard.add(key_cancel)
            bot.send_message(user_id, text=description, reply_markup=keyboard)
    update_user(db_file, user)


@bot.callback_query_handler(func=lambda call: call.data[0] == '!')
def next_exercise(call):
    # global users
    user_id = call.from_user.id
    user = get_user_from_database(db_file, user_id)
    user.status = "Training"
    user.check_time = time.time() + 20  # FIFTEEN
    bot.delete_message(call.from_user.id, call.message.message_id)
    if call.data == '!cancel':
        bot.send_message(user_id, talking.skip)
        user.let_go()
    else:
        description = user.get_exercise()
        if description == talking.last_exercise:
            user.current_exercise = 0
            user.current_training += 1
            bot.send_message(user_id, description)
            user_plus_train(db_file, user_id, user.current_exercise, user.current_training)
        else:
            user.current_exercise += 1
            keyboard = telebot.types.InlineKeyboardMarkup()

            key_next = telebot.types.InlineKeyboardButton(text=talking.button_next, callback_data='.next')
            key_cancel = telebot.types.InlineKeyboardButton(text=talking.button_cancel, callback_data='.cancel')
            keyboard.add(key_next)
            keyboard.add(key_cancel)
            bot.send_message(user_id, text=description, reply_markup=keyboard)
        update_user(db_file, user)


def how_are_you():
    users = {}
    exercises = {}
    read_users_from_database(db_file, users)
    read_exercises_from_database(db_file, exercises)
    read_plans_from_database(db_file, users, exercises, True)
    while True:
        time.sleep(10)  # 15*60+
        print("Scanning... (Data download)")
        read_users_from_database(db_file, users)
        read_plans_from_database(db_file, users, exercises, False)
        print("Scanning... (Start)")
        for user_id in users:
            print(user_id, users[user_id].status)
            user = users[user_id]
            if user.status != "Waiting" and user.check_time == -1:
                print(user.check_time)
                user.check_time = time.time()
                print(user.check_time)
                update_user(db_file, user)
            if user.timeout():
                if user.status == "Sleeping":
                    bot.send_message(user.id, user.nickname + talking.go_train)
                    bot.send_message(admin_id, "Пользователь " + user.full_name + " (" + user.nickname + ") " +
                                     "давно не занимался!")
                    user.check_time += 20  # 60 * 60 * 4

                elif user.status == "Training":
                    description = talking.continue_train
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    key_go = telebot.types.InlineKeyboardButton(text=talking.button_next, callback_data='!next')
                    key_cancel = telebot.types.InlineKeyboardButton(text=talking.button_cancel, callback_data='!cancel')
                    keyboard.add(key_go)
                    keyboard.add(key_cancel)
                    bot.send_message(user.id, text=description, reply_markup=keyboard)
                    user.check_time += 20  # 60 * 30
                    user.status = "Breaking"
                elif user.status == "Breaking":
                    bot.send_message(user.id, talking.skip)
                    user.let_go()
                update_user(db_file, user)
            else:
                print(user.check_time, " >= ", time.time())



if __name__ == "__main__":
    admin_polling = multiprocessing.Process(target=admin_bot.polling)
    admin_polling.start()

    bot_polling = multiprocessing.Process(target=bot.polling)
    bot_polling.start()
    bot.send_message(admin_id[0], "Hello, admin")

    # server_check = multiprocessing.Process(target=how_are_you)
    # server_check.start()
    # bot.send_message(admin_id, bot.get_me().id)
    # admin_polling.start()
    pass
