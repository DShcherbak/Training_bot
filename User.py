class User:
    id = -1
    current_training = 0
    current_exercise = 0
    full_name = ""
    nickname = ""
    trainings = []

    def encode_to_json(self):
        encoded_debts = []
        return {"id": {0: self.id}, "current_training": {0: self.current_training},
                "current_exercise": {0: self.current_exercise}, "full_name": {0: self.full_name},
                "nickname": {0: self.nickname}, "trainings": dict(self.trainings)}

    def decode_from_json(self, json_group):
        self.id = int(json_group["id"]["0"])
        self.current_training = int(json_group["current_training"]["0"])
        self.full_name = json_group["full_name"]["0"]
        self.nickname = json_group["nickname"]["0"]
        self.trainings = list(json_group["trainings"])

    def get_exercise(self):
        return "abbaba"
