from Exercise import *
import time
class User:
    id = -1
    current_training = 0
    current_exercise = 0
    full_name = ""
    nickname = ""
    check_time = 0.0
    status = ""
    trainings = []

    def encode_to_json(self):
        encoded_trainings = []
        for train in self.trainings:
            encoded_train = train.encode_to_json()
            encoded_trainings.append(encoded_train)
        return {"id": str(self.id), "current_training":  str(self.current_training),
                "current_exercise": str(self.current_exercise), "full_name": self.full_name,
                "nickname": self.nickname, "check_time": str(self.check_time),
                "status": self.status, "trainings": encoded_trainings}

    def decode_from_json(self, json_group):
        self.id = int(json_group["id"])
        self.current_training = int(json_group["current_training"])
        self.full_name = json_group["full_name"]
        self.nickname = json_group["nickname"]
        self.check_time =  float(json_group["check_time"])
        self.status = json_group["status"]
        
        encoded_trainings = json_group["trainings"]
        for encoded_train in encoded_trainings:
            new_train = Training()
            new_train.decode_from_json(encoded_train)
            self.trainings.append(new_train)

    def timeout(self):
        return (self.check_time < time.time())

    def finished(self):
        return self.current_training >= len(self.trainings)

    def get_exercise(self):
        if self.current_exercise >= len(self.trainings[self.current_training].exercises):
            return "Це була остання вправа, можна відпочивати!"
        else:
            return "Вправа номер " + str(self.current_training) + self.trainings[self.current_training].exercises[self.current_exercise].to_message()
