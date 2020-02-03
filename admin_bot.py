import telebot
import json
from User import *
from Exercise import *
admin_bot = telebot.TeleBot('1030110837:AAHoq-myzsZ3j06ZRGiv49Sd2TsCe63c2ZE')
user_database = "user_database.json"
exercise_database = "exercise_database.json"
users = {}
exercises = []
admin_id = "378669057"

def read_from_database():
    global users, exercises, number_exercises
    with open(user_database, "r") as read_file:
        encoded_users = json.load(read_file)
    for encoded_user in encoded_users:
        user = User()
        user.decode_from_json(encoded_user)
        users.update([{user.id, user}])
    with open(exercise_database, "r") as read_file:
        encoded_exercises = json.load(read_file)
    for encoded_exercise in encoded_exercises:
        exercise = ExercisePattern()
        exercise.decode_from_json(encoded_exercise)
        exercises.append(exercise)
    number_exercises = len(exercises)


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
    for exercise in exercises:
        encoded_exercises.append(exercise.encode_to_json())
    with open(exercise_database, "w") as write_file:
        json.dump(encoded_exercises, write_file)



@admin_bot.message_handler(commands=['reload'])
def reload(message):
    if str(message.from_user.id) == admin_id:
        read_from_database()
        admin_bot.send_message(message.from_user.id, "Successfully reloaded")
    else:
        admin_bot.send_message(message.from_user.id, "You don't have admin rights")


@admin_bot.message_handler(commands=['new_exercise'])
def new_exercise(message):
    if str(message.from_user.id) == admin_id:
        read_from_database()
        admin_bot.send_message(message.from_user.id, 'Название упражнения: ')
        exercise = ExercisePattern()
        exercises.append(exercise)
        admin_bot.register_next_step_handler(message, get_exercise_name)
        save_exercises()
    else:
        admin_bot.send_message(message.from_user.id, "You don't have admin rights")


@admin_bot.message_handler(content_types=['document'])
def get_text_messages(message):
    print(message.document.file_id)
    admin_bot.send_message(message.from_user.id, "hello")
    file_info = admin_bot.get_file(message.document.file_id)
    downloaded_file = admin_bot.download_file(file_info.file_path)

    with open('uploaded_database.json', 'wb') as new_file:
        new_file.write(downloaded_file)
    #TODO: Merge uploaded and current database



def get_exercise_name(message):
    admin_bot.send_message(message.from_user.id, "Описание упражнения: ")
    global exercises
    id = len(exercises)-1
    exercises[id].name = message.text
    exercises[id].id = id
    save_exercises()
    admin_bot.register_next_step_handler(message, get_exercise_desc)


def get_exercise_desc(message):
    admin_bot.send_message(message.from_user.id, "Ссьілка на пример упражнения: ")
    global exercises
    id = len(exercises)-1
    exercises[id].desc = message.text
    save_exercises()
    admin_bot.register_next_step_handler(message, get_link)


def get_link(message):
    admin_bot.send_message(message.from_user.id, "OK, вот шаблон упражения")
    global users
    id = len(exercises)-1
    exercises[id].link = message.text
    save_exercises()
    admin_bot.send_message(message.from_user.id, exercises[id].to_message())


