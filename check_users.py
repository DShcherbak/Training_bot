from bot import bot
import json

if __name__ == "__main__":
    with open("waiting_database.json", "r") as read_file:
        users = json.load(read_file)
    for user_key in users:
        user = users[user_key]
        if True:
            bot.send_message(user, "Yeah, baby!")