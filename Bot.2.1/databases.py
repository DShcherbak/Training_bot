import sqlite3
from User import User
from Exercise import ExercisePattern, Exercise, Training
from sqlite3 import Error

hash_code = 100

database = "bot.db"

# TODO: exercises id must be +1

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
            exercise_pattern[0],
            exercise_pattern[1],
            exercise_pattern[2]
        )
        cur.execute(sql, encoded_exercise)
        return cur.lastrowid


def create_plan(db_file, plan):
    connection = create_connection(db_file)
    with connection:
        sql = ''' INSERT INTO Plans(user_id, train_number, exercise_number, exercise_id, temp, repeat, changed)
                    VALUES 
                    (?, ?, ?, ?, ?, ?, ?)  
                           '''
        # (user.id, i, j, exercise.id, exercise.temp, exercise.repeat)
        cur = connection.cursor()
        cur.execute(sql, plan)
        return cur.lastrowid

def get_exercise_from_database(db_file, _id=0,_name="", _link="", _desc=""):
    if(_id < 0):
        ex = Exercise(_name="Круг " + str(-_id), _temp= ".", _repeat=0, _link = _link, _desc = _desc)
        return ex
    connection = create_connection(db_file)
    with connection:
        sql = ''' SELECT * FROM Exercises'''
        cnt = 0
        sql += " WHERE "
        if _id > 0:
             sql += 'id = "' + str(_id) + '"'
             cnt += 1
        if _name:
            if cnt > 0:
                sql += " AND "
            sql += 'name = "' + str(_name) + '"'
            cnt += 1
        if _desc:
            if cnt > 0:
                sql += " AND "
            sql += 'description = "' + str(_desc) + '"'
            cnt += 1
        if _link:
            if cnt > 0:
                sql += " AND "
            sql += 'link = "' + str(_link) + '"'
            cnt += 1
        print("Get exercise : " + sql)
        cur = connection.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        if rows:
            row = ExercisePattern(_tuple=rows[0])
        else:
            row = Exercise()
        return row

def get_user_from_database(db_file, _id=0):
    connection = create_connection(db_file)
    user = User()
    with connection:
        sql = ''' SELECT * FROM Users WHERE telegram_id = ''' + str(_id)
        cur = connection.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        if rows:
            user = User(_tuple=rows[0])
        else:
            user = User()
    get_user_plans_from_database(db_file, user, _id)
    return user


def get_user_plans_from_database(db_file, user, user_id):
    connection = create_connection(db_file)
    with connection:
        sql = ''' SELECT * FROM Plans WHERE user_id = ''' + str(user_id)
        cur = connection.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            tr_id = row[2]
            ex_id = row[3]
            while len(user.trainings) <= tr_id:
                user.trainings.append(Training())
            while len(user.trainings[tr_id].exercises) < ex_id:
                user.trainings[tr_id].exercises.adppend(Exercise())
            new_ex_pattern = get_exercise_from_database(db_file, _id=row[4])
            print(type(new_ex_pattern))
            new_ex = Exercise(pattern=new_ex_pattern, _temp=row[5], _repeat=row[6])
            if len(user.trainings[tr_id].exercises) == ex_id:
                user.trainings[tr_id].exercises.append(new_ex)
            else:
                user.trainings[tr_id].exercises[ex_id] = new_ex




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
            user.full_name,
            user.nickname,
            user.current_exercise,
            user.current_training,
            user.status,
            user.check_time,
            user.id
            )
        cur.execute(sql, encoded_user)
        connection.commit()


def update_exercise(db_file, _name = "", _desc="", _link="", args=()):
    connection = create_connection(db_file)
    with connection:
        cnt = 0
        sql = ''' UPDATE Exercises SET '''
        if _name:
             sql += 'name = "' + str(args[cnt]) + '"'
             cnt += 1
        if _desc:
            if cnt > 0:
                sql += ", "
            sql += 'description = "' + str(args[cnt]) + '"'
            cnt += 1
        if _link:
            if cnt > 0:
                sql += ", "
            sql += 'link = "' + str(args[cnt]) + '"'
            cnt += 1
        sql += " WHERE "
        cnt = 0
        if _name:
             sql += 'name = "' +  str(_name) + '"'
             cnt += 1
        if _desc:
            if cnt > 0:
                sql += " AND "
            sql += 'description = "' +  str(_desc) + '"'
            cnt += 1
        if _link:
            if cnt > 0:
                sql += " AND "
            sql += 'link = "' +  str(_link) + '"'
            cnt += 1
        print("Update ex : " + sql)
        cur = connection.cursor()

        cur.execute(sql)
        connection.commit()


def user_plus_train(db_file, user_id, ex, train):
    connection = create_connection(db_file)
    with connection:
        sql = ''' UPDATE Users
                      SET   current_exercise = ?, 
                            current_training = ?
                      WHERE telegram_id = ?'''

        cur = connection.cursor()
        encoded_user = (
            ex,
            train,
            user_id)
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
            ex = User(_tuple=row)
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
            ex = ExercisePattern(_tuple=row)
            exercises.update([(row[0], ex)])


def read_plans_from_database(db_file, users, exercises, all=False):
    connection = create_connection(db_file)
    with connection:
        cur = connection.cursor()
        sql = "SELECT * FROM Plans"
        if not all:
            sql += " WHERE changed = TRUE"
        cur.execute(sql)
        rows = cur.fetchall()
        some_array = []
        for row in rows:
            print(row)
            user_id = row[1]
            train_num = row[2]
            exer_num = row[3]
            if(row[4] < 0) :
                pattern = get_exercise_from_database(db_file, row[4])
            else:
                pattern = exercises[row[4] + 1]
            ex = Exercise(_name=pattern.name, _link=pattern.link, _desc=pattern.desc, _temp=row[5], _repeat=row[6])
            while len(users[user_id].trainings) <= train_num:
                users[user_id].trainings.append(Training())
            if len(users[user_id].trainings[train_num].exercises) <= exer_num:
                users[user_id].trainings[train_num].exercises.append(ex)
            else:
                users[user_id].trainings[train_num].exercises[exer_num] = ex
            new_sql = "UPDATE Plans SET changed = False WHERE id = " + str(row[0])
            cur.execute(new_sql)


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
        sql1 = '''SELECT * FROM Plans
                    Where user_id = ? AND
                            train_number = ? AND
                            exercise_number = ?'''
        cur = connection.cursor()
        cur.execute(sql1, (plan[0], plan[1], plan[2]))
        rows = cur.fetchall()
        if not rows:
            create_plan(db_file, plan)
        else:
            sql = ''' UPDATE Plans
                     SET   exercise_id = ?,
                           temp = ?, 
                           repeat = ?,
                           changed = true
                     WHERE user_id = ? AND 
                           train_number = ? AND 
                           exercise_number = ?                      
                           '''


            encoded_plan = (
                # (user.id, i, j, exercise.id, exercise.temp, exercise.repeat)
                # (user_id, t, e, ex_id, _temp, _repeat ,True)
                #  [0]     [1][2]   [3]   [4]    [5]     [6]
                plan[3],
                plan[4],
                plan[5],
                plan[0],
                plan[1],
                plan[2]
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
