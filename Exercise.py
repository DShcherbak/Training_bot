class ExercisePattern:
    name = ""
    link = ""
    desc = ""


    def encode_to_json(self):
        return {"name" : self.name, "link": self.link, "desc": self.desc}

    def decode_from_json(self, json_group):
        self.name = json_group["name"]
        self.link = json_group["link"]
        self.desc = json_group["desc"]

    def to_message(self):
        result = ""
        result += "Упражнение: " + self.name + "\n\n"
        result += "Количество повторов: " + "\n\n"
        result += "Темп: " + "\n\n"
        result += "Описание: " + self.desc + "\n\n"
        result += "Пример: " + self.link
        return result


class Exercise:
    name = ""
    link = ""
    desc = ""
    repeat = 0
    temp = ""

    def __init__(self, pattern=None):
        if not pattern == None:
            self.name = pattern.name
            self.link = pattern.link
            self.desc = pattern.desc


    def set_repeat(self, _repeat):
        self.repeat = _repeat

    def set_temp(self, _temp):
        self.temp = _temp

    def encode_to_json(self):
        return {"name" : self.name, "link": self.link, "desc": self.desc,
                "repeat": str(self.repeat), "temp": self.temp}

    def decode_from_json(self, json_group):
        self.name = json_group["name"]
        self.link = json_group["link"]
        self.desc = json_group["desc"]
        self.repeat = int(json_group["repeat"])
        self.temp = json_group["temp"]

    def to_message(self):
        result = ""
        result += "Упражнение: " + self.name + "\n\n"
        result += "Количество повторов: " + str(self.repeat) + "\n\n"
        result += "Темп: " + self.temp + "\n\n"
        result += "Описание: " + self.desc + "\n\n"
        result += "Пример: " + self.link
        return result


class Training:
    started = False
    finished = False
    exercises = []  # list of exercises

    def __init__(self):
        self.started = False
        self.finished = False
        self.exercises = []  # list of exercises

    def encode_to_json(self):
        finish_code = self.started*1 + self.finished*1
        encoded_exes = []
        for ex in self.exercises:
            new_ex = ex.encode_to_json()
            encoded_exes.append(new_ex)
        return {"finish_code": str(finish_code), "exercises" : encoded_exes}

    def decode_from_json(self, json_group):
        finish_state = int(json_group["finish_code"])
        self.started = finish_state > 0
        self.finished = finish_state > 1
        encoded_exes = json_group["exercises"]
        for encoded_ex in encoded_exes:
            new_ex = Exercise()
            new_ex.decode_from_json(encoded_ex)
            self.exercises.append(new_ex)