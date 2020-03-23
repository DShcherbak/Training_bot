import telebot
import json
from User import *
from databases import *

# TODO: New exer with old name = update

admin_bot = telebot.TeleBot(config.admin_token, threaded=False)
user_database = config.user_database
admin_id = config.admin_id
db_file = "bot.db"

# #####################################


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
    print("New_plans: ",plans_to_update)
    for plan in plans_to_update:
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
    test = False
    if test:
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
        admin_bot.reply_to(message, "Фото добавлено")
        merge_libraries(src)


@admin_bot.message_handler(commands=['new_exercise'])
def new_exercise(message):
    user_id = message.from_user.id
    if str(user_id) in admin_id:
        admin_bot.send_message(user_id, 'Название упражнения: ')
        create_exercise(db_file, ("no name", "no link", "no description"))
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

admin_bot.polling()