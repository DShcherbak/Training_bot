from Exercise import *
class User:
    id = -1
    current_training = 0
    current_exercise = 0
    full_name = ""
    nickname = ""
    trainings = []

    def encode_to_json(self):
        encoded_trainings = {}
        i = 0
        for train in self.trainings:
            encoded_train = train.encode_to_json()
            encoded_trainings.update([{i,encoded_train}])
        return {"id": {0: self.id}, "current_training": {0: self.current_training},
                "current_exercise": {0: self.current_exercise}, "full_name": {0: self.full_name},
                "nickname": {0: self.nickname}, "trainings": encoded_trainings}

    def decode_from_json(self, json_group):
        self.id = int(json_group["id"]["0"])
        self.current_training = int(json_group["current_training"]["0"])
        self.full_name = json_group["full_name"]["0"]
        self.nickname = json_group["nickname"]["0"]
        encoded_trainings = json_group["trainings"]
        for encoded_train in encoded_trainings:
            new_train = Training()
            new_train.decode_from_json(encoded_train)
            self.trainings.append(new_train)
        self.trainings = list(json_group["trainings"])

    def get_exercise(self):
        if self.current_exercise >= len(self.trainings):
            return "Це була остання вправа, можна відпочивати!"
        else:
            return "Вправа номер " + str(self.current_training) + self.trainings[self.current_training].to_message()
