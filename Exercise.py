class ExercisePattern:
    id = -1
    name = ""
    link = ""
    desc = ""

    def encode_to_json(self):
        return {"id": {0: self.id}, "name" : {0: self.name}, "link": {0: self.link}, "desc": {0: self.desc}}

    def decode_from_json(self, json_group):
        self.id = int(json_group["id"]["0"])
        self.name = json_group["name"]["0"]
        self.link = json_group["link"]["0"]
        self.desc = json_group["desc"]["0"]

    def to_message(self):
        result = ""
        result += "Упражнение: " + self.name + "\n\n"
        result += "Количество повторов: " + "\n\n"
        result += "Темп: " + "\n\n"
        result += "Описание: " + self.desc + "\n\n"
        result += "Пример: " + self.link
        return result


class Exercise:
    id = -1
    name = ""
    link = ""
    desc = ""
    repeat = 0
    temp = 0

    def __init__(self):
        pass

    def __init__(self, pattern):
        self.id = pattern.id
        self.name = pattern.name
        self.link = pattern.link
        self.desc = pattern.desc

    def set_repeat(self, _repeat):
        self.repeat = _repeat

    def set_temp(self, _temp):
        self.temp = _temp

    def to_message(self):
        return str(self.id) + "\n"


class Training:
    id = -1
    started = False
    finished = False
    exes = []  # list of exercises

    def encode_to_json(self):
        finish_code = self.started*1 + self.finished*1
        encoded_exes = []
        for ex in self.exes:
            encoded_exes.append(ex.encode_to_json())
        return {"id": {0: self.id}, "finish_code": {0: finish_code}, "exes" : encoded_exes}

    def decode_from_json(self, json_group):
        self.id = int(json_group["id"]["0"])
        finish_state = int(json_group["finish_code"]["0"])
        self.started = finish_state > 0
        self.finished = finish_state > 1
        encoded_exes = json_group["finish_code"]["0"]
        for encoded_ex in encoded_exes:
            new_ex = Exercise()
            new_ex.decode_from_json(encoded_ex)
            self.exes.append(new_ex)
