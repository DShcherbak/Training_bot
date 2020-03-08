import sqlite3
from User import User
from Exercise import ExercisePattern, Exercise
from sqlite3 import Error

hash_code = 100

database = "bot.db"


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return connection


def create_user(db_file, user):
    connection = create_connection(db_file)
    with connection:
        print("addding user")
        sql = ''' INSERT INTO Users (telegram_id, 
        full_name,
        nickname, 
        current_exercise, 
        current_training,
        status,
        check_time)
        VALUES(?,?,?,?,?,?,?) '''
        cur = connection.cursor()
        encoded_user = (
            user.id,
            user.full_name,
            user.nickname,
            user.current_exercise,
            user.current_training,
            user.status,
            user.check_time)
        print("adding...")
        cur.execute(sql, encoded_user)
        print("added!")
        connection.commit()
        return cur.lastrowid


def create_exercise(db_file, exercise_pattern):
    connection = create_connection(db_file)
    with connection:
        sql = ''' INSERT INTO Exercises (name, link, description)
                  VALUES(?,?,?) '''
        cur = connection.cursor()
        encoded_exercise = (
            exercise_pattern.name,
            exercise_pattern.link,
            exercise_pattern.desc
        )
        cur.execute(sql, encoded_exercise)
        return cur.lastrowid


def create_plan(db_file, plan):
    connection = create_connection(db_file)
    with connection:
        sql = ''' INSERT INTO Plans(user_id, train_number, exercise_number, exercise_id, temp, repeat)
                    VALUES 
                    (?, ?, ?, ?, ?, ?)  
                           '''
        # (user.id, i, j, exercise.id, exercise.temp, exercise.repeat)
        cur = connection.cursor()
        cur.execute(sql, plan)
        return cur.lastrowid


def update_user(db_file, user):
    connection = create_connection(db_file)
    with connection:
        sql = ''' UPDATE Users
                  SET   full_name = ?,
                        nickname = ?, 
                        current_exercise = ?, 
                        current_training = ?,
                        status = ?,
                        check_time = ?
                  WHERE telegram_id = ?'''

        cur = connection.cursor()
        encoded_user = (
            user.id,
            user.full_name,
            user.nickname,
            user.current_exercise,
            user.current_training,
            user.status,
            user.check_time)
        cur.execute(sql, encoded_user)
        connection.commit()


def read_users_from_database(db_file, exercises):
    connection = create_connection(db_file)
    with connection:
        cur = connection.cursor()
        cur.execute("SELECT * FROM Users")
        rows = cur.fetchall()
        some_array = []
        for row in rows:
            print(row)
            ex = User(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            some_array.append((row[1], ex))  # I use row[1], telegram_id, as key in main program
        exercises.update(some_array)


def read_exercises_from_database(db_file, exercises):
    connection = create_connection(db_file)
    with connection:
        cur = connection.cursor()
        cur.execute("SELECT * FROM Exercises")
        rows = cur.fetchall()
        for row in rows:
            print(row)
            ex = ExercisePattern(row[0], row[1], row[2], row[3])
            exercises.append(ex)


def read_plans_from_database(db_file, users):
    connection = create_connection(db_file)
    with connection:
        cur = connection.cursor()
        cur.execute("SELECT * FROM Plans WHERE changed = TRUE")
        rows = cur.fetchall()
        some_array = []
        for row in rows:
            print(row)
            user_id = row[1]
            train_num = row[2]
            exer_num = row[3]
            users[user_id].trainings[train_num].exercises[exer_num] = Exercise()
            ex = User(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            some_array.append((row[1], ex))  # I use row[1], telegram_id, as key in main program
            users[user_id].trainings[train_num].exercises[exer_num] = ex


def save_exercises_into_database(db_file, exercises, changed):
    connection = create_connection(db_file)
    with connection:
        cur = connection.cursor()
        sql = ''' UPDATE Exercises
                     SET   name = ?,
                           link = ?, 
                           description = ? 
                     WHERE id = ?'''
        encoded_exercise = ()
        for key in changed:
            ex = exercises[key]
            encoded_exercise = (
                ex.name,
                ex.link,
                ex.desc,
                ex.id)
        cur.execute(sql, encoded_exercise)
        connection.commit()


def save_users_into_database(db_file, users, changed):
    for key in changed:
        us = users[key]
        update_user(db_file, us)
        # TODO : maybe should have one connection for this very function and pass as a parameter


def save_plans_into_database(db_file, users):
    connection = create_connection(db_file)
    with connection:
        cur = connection.cursor()
        cur.execute("SELECT * FROM Exercises")

        rows = cur.fetchall()
        plans_to_update = []
        plans_to_insert = []

        plans = {}
        some_array = []
        counter = 0
        for row in rows:
            print(row)
            some_array.append((hash7(row), row))
        plans.update(some_array)
        for user in users:
            i = 1
            for training in user.trainings:
                i = i + 1
                j = 1
                for exercise in training.exercises:
                    j = j + 1
                    key = hash3(user.primary_id, i, j)
                    new_plan = (user.id, i, j, exercise.id, exercise.temp, exercise.repeat, True)
                    if key not in plans.keys():
                        plans_to_insert.append(new_plan)  # INSERT INTO Plans
                    else:
                        base_plan = plans[key]
                        new_plan = (base_plan[0], user.id, i, j, exercise.id, exercise.temp, exercise.repeat, True)
                        if base_plan == new_plan:
                            print("YEAH!")
                            counter = counter + 1
                        else:
                            plans_to_update.append(new_plan)  # UPDATE Plans
        for plan in plans_to_update:
            update_current_plan(connection, plan)
        for plan in plans_to_insert:
            create_plan(connection, plan)


def update_current_plan(db_file, plan):
    connection = create_connection(db_file)
    with connection:
        sql = ''' UPDATE Plans
                     SET   exercise_id = ?,
                           temp = ?, 
                           repeat = ?,
                           changed = true
                     WHERE user_id = ? AND 
                           train_number = ? AND 
                           exercise_number = ?                      
                           '''

        cur = connection.cursor()
        encoded_plan = (
            # (base_plan[0], user.id, i, j, exercise.id, exercise.temp, exercise.repeat)
            #  [0]             [1]  [2][3]   [4]            [5]             [6]
            plan[4],
            plan[5],
            plan[6],
            plan[1],
            plan[2],
            plan[3]
        )
        cur.execute(sql, encoded_plan)
        connection.commit()


def hash7(tuple7):
    return tuple7[1] * (hash_code ** 2) + tuple7[2] * hash_code + tuple7[3]


def hash3(a, b, c):
    return a * (hash_code ** 2) + b * hash_code + c


def select_all_exercises(db_file):
    """
    Query all rows in the tasks table
    :param connection: the Connection object
    :return:
    """
    connection = create_connection(db_file)
    with connection:
        cur = connection.cursor()
        cur.execute("SELECT * FROM Exercises")

        rows = cur.fetchall()

        for row in rows:
            print(row)


def select_task_by_priority(db_file, priority):
    """
    Query tasks by priority
    :param connection: the Connection object
    :param priority:
    :return:
    """
    connection = create_connection(db_file)
    with connection:
        cur = connection.cursor()
        cur.execute("SELECT * FROM Exercises WHERE id=?", (priority,))

        rows = cur.fetchall()

        for row in rows:
            print(row)


def main():
    # create a database connection
    connection = create_connection(database)
    with connection:
        print("1. Query task by priority:")
        select_task_by_priority(connection, 1)

        print("2. Query all tasks")
        select_all_exercises(connection)


if __name__ == '__main__':
    main()
