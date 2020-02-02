from Exercise import *
class User:
    id = -1
    current_training = 0
    current_exercise = 0
    full_name = ""
    nickname = ""
    trainings = []

    def encode_to_json(self):
        encoded_trainings = []
        i = 0
        for train in self.trainings:
            encoded_train = train.encode_to_json()
            encoded_trainings.append(encoded_train)
        return {"id": str(self.id), "current_training":  str(self.current_training),
                "current_exercise": str(self.current_exercise), "full_name": self.full_name,
                "nickname": self.nickname, "trainings": encoded_trainings}

    def decode_from_json(self, json_group):
        self.id = int(json_group["id"])
        self.current_training = int(json_group["current_training"])
        self.full_name = json_group["full_name"]
        self.nickname = json_group["nickname"]
        encoded_trainings = json_group["trainings"]
        for encoded_train in encoded_trainings:
            new_train = Training()
            new_train.decode_from_json(encoded_train)
            self.trainings.append(new_train)
        self.trainings = encoded_trainings

    def get_exercise(self):
        if self.current_exercise >= len(self.trainings):
            return "Це була остання вправа, можна відпочивати!"
        else:
            return "Вправа номер " + str(self.current_training) + self.trainings[self.current_training].to_message()
