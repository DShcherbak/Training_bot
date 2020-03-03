import sqlite3
import User
import Exercise
from sqlite3 import Error

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


def update_exercise(connection, user):

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
    sql = 'DELETE FROM tasks WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()


def main2():
    connection = create_connection(database)
    with connection:
        update_task(connection, (2, '2015-01-04', '2015-01-06', 2))


def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")

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
    cur.execute("SELECT * FROM tasks WHERE priority=?", (priority,))

    rows = cur.fetchall()

    for row in rows:
        print(row)


def main():

    # create a database connection
    conn = create_connection(database)
    with conn:
        print("1. Query task by priority:")
        select_task_by_priority(conn, 1)

        print("2. Query all tasks")
        select_all_tasks(conn)


if __name__ == '__main__':
    main()