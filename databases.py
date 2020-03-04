import sqlite3
from User import User
from Exercise import ExercisePattern
from sqlite3 import Error

hash_code = 100


database = "bot.db"


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def create_user(conn, user):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO Users (telegram_id, 
    full_name,
    nickname, 
    current_exercise, 
    current_training,
    status,
    check_time)
              VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    encoded_user = (
        user.id,
        user.full_name,
        user.nickname,
        user.current_exercise,
        user.current_training,
        user.status,
        user.check_time)
    cur.execute(sql, encoded_user)
    return cur.lastrowid

def create_exercise(conn, exercise_pattern):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """

    sql = ''' INSERT INTO Exercises (name, link, description)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    encoded_exercise = (
        exercise_pattern.name,
        exercise_pattern.link,
        exercise_pattern.desc
    )
    cur.execute(sql, encoded_exercise)
    return cur.lastrowid

def update_user(connection, user):

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

def delete_task(conn, id):
    """
    Delete a task by task id
    :param conn:  Connection to the SQLite database
    :param id: id of the task
    :return:
    """
    sql = 'DELETE FROM Users WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()

def main2():
    connection = create_connection(database)
    with connection:
        pass # update_task(connection, (2, '2015-01-04', '2015-01-06', 2))

def select_all_exercises(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM Exercises")

    rows = cur.fetchall()

    for row in rows:
        print(row)

def select_task_by_priority(conn, priority):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM Exercises WHERE id=?", (priority,))

    rows = cur.fetchall()

    for row in rows:
        print(row)

def read_exercises_from_database(connection, exercises):
    cur = connection.cursor()
    cur.execute("SELECT * FROM Exercises")
    rows = cur.fetchall()
    some_array = []
    for row in rows:
        print(row)
        ex = ExercisePattern(row[0],row[1],row[2],row[3])
        some_array.append((row[0], ex))
    exercises.update(some_array)

def save_exercises_into_database(connection, exercises, changed):
    cur = connection.cursor()
    sql = ''' UPDATE Exercises
                 SET   name = ?,
                       link = ?, 
                       description = ? 
                 WHERE id = ?'''
    for key in changed:
        ex = exercises[key]
        encoded_exercise = (
            ex.name,
            ex.link,
            ex.desc,
            ex.id)
    cur.execute(sql, encoded_exercise)
    connection.commit()

def read_users_from_database(connection, exercises):
    cur = connection.cursor()
    cur.execute("SELECT * FROM Users")
    rows = cur.fetchall()
    some_array = []
    for row in rows:
        print(row)
        ex = User(row[0],row[1],row[2],row[3], row[4], row[5], row[6], row[7])
        some_array.append((row[1], ex)) # I use row[1], telegram_id, as key in main program
    exercises.update(some_array)


def save_users_into_database(connection, users, changed):
    cur = connection.cursor()
    sql = ''' UPDATE Users
                 SET    telegram_id = ?, 
                        full_name = ?,
                        nickname = ?, 
                        current_exercise = ?, 
                        current_training = ?,
                        status = ?,
                        check_time = ?
                 WHERE id = ?'''
    for key in changed:
        us = users[key]
        cur.execute(sql, (us.id, us.full_name, us.nickname, us.current_exercise, us.current_training, us.status, us.check_time,us.primary_id))
    connection.commit()

def hash(tuple7):
    return tuple7[1]*(hash_code**2) + tuple7[2]*(hash_code) + tuple7[3]

def hash(a,b,c):
    return a*(hash_code**2) + b*(hash_code) + c

def update_plan(connection, plan):
    sql = ''' UPDATE Plans
                 SET   exercise_id = ?,
                       temp = ?, 
                       repeat = ?
                 WHERE user_id = ? AND 
                       train_number = ? AND 
                       exercise_number = ?                      
                       '''

    cur = connection.cursor()
    encoded_plan = (
                     #(base_plan[0], user.id, i, j, exercise.id, exercise.temp, exercise.repeat)
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

def insert_plan(connection, plan):
    sql = ''' INSERT INTO Plans(user_id, train_number, exercise_number, exercise_id, temp, repeat)
                VALUES 
                (?, ?, ?, ?, ?, ?)  
                       '''
    # (user.id, i, j, exercise.id, exercise.temp, exercise.repeat)
    cur = connection.cursor()
    cur.execute(sql, plan)
    return cur.lastrowid

def update_plans(connection, users):
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
        some_array.append((hash(row), row))
    plans.update(some_array)
    for user in users:
        i = 1
        for training in user.trainings:
            i = i + 1
            j = 1
            for exercise in training.exercises:
                j = j + 1
                key = hash(user.primary_id, i, j)
                new_plan = (user.id, i, j, exercise.id, exercise.temp, exercise.repeat)
                if not key in plans.keys():
                    plans_to_insert.append(new_plan) # INSERT INTO Plans
                else:
                    base_plan = plans[key]
                    new_plan = (base_plan[0], user.id, i, j, exercise.id, exercise.temp, exercise.repeat)
                    if base_plan == new_plan:
                        print("YEAH!")
                        counter = counter + 1
                    else:
                        plans_to_update.append(new_plan) # UPDATE Plans
    for plan in plans_to_update:
        update_plan(connection,plan)
    for plan in plans_to_insert:
        insert_plan(connection, plan)



def main():

    # create a database connection
    conn = create_connection(database)
    with conn:
        print("1. Query task by priority:")
        select_task_by_priority(conn, 1)

        print("2. Query all tasks")
        select_all_exercises(conn)


if __name__ == '__main__':
    main()