from Exercise import *

from git_ignore import config
import talking
import time


class User:
    primary_id = -1
    id = -1
    current_training = 0
    current_exercise = 0
    last_message_id = -1
    full_name = ""
    nickname = ""
    check_time = 0.0
    status = ""
    trainings = []

    def __init__(self, _tuple=(), _primary_id=-1, _id=-1, _full_name="", _nickname="", _current_training=0,
                 _current_exercise=0, _status="Sleeping", _check_time=0, _last_message_id = -1):
        if _tuple:
            self.primary_id = _tuple[0]
            self.id = _tuple[1]
            self.full_name = _tuple[2]
            self.nickname = _tuple[3]
            self.current_training = _tuple[4]
            self.current_exercise = _tuple[5]
            self.status = _tuple[6]
            self.check_time = _tuple[7]
            self.last_message_id = _tuple[8]
        else:
            self.primary_id = _primary_id
            self.id = _id
            self.full_name = _full_name
            self.nickname = _nickname
            self.current_training = _current_training
            self.current_exercise = _current_exercise
            self.status = _status
            self.check_time = _check_time
            self.last_message_id = _last_message_id

    def encode_to_json(self):
        encoded_trainings = []
        for train in self.trainings:
            encoded_train = train.encode_to_json()
            encoded_trainings.append(encoded_train)
        return {"id": str(self.id), "current_training": str(self.current_training),
                "current_exercise": str(self.current_exercise), "full_name": self.full_name,
                "nickname": self.nickname, "check_time": str(self.check_time),
                "status": self.status, "trainings": encoded_trainings,
                "last_message_id": self.last_message_id}

    def decode_from_json(self, json_group):
        self.id = int(json_group["id"])
        self.current_training = int(json_group["current_training"])
        self.full_name = json_group["full_name"]
        self.nickname = json_group["nickname"]
        self.check_time = float(json_group["check_time"])
        self.status = json_group["status"]
        self.last_message_id = json_group["last_message_id"]

        encoded_trainings = json_group["trainings"]
        for encoded_train in encoded_trainings:
            new_train = Training()
            new_train.decode_from_json(encoded_train)
            self.trainings.append(new_train)

    def timeout(self):
        return ((not self.status == "Waiting") and float(self.check_time) < time.time())

    def finished(self):
        return self.current_training >= len(self.trainings)

    def get_exercise(self):
        if self.current_exercise >= len(self.trainings[self.current_training].exercises):
            return talking.last_exercise
        else:
            return self.trainings[self.current_training].exercises[self.current_exercise].to_message()

    def let_go(self):
        self.status = "Sleeping"
        self.check_time = time.time() + config.TWO_DAYS
        self.current_exercise = 0