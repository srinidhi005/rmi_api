import mysql.connector
from mysql.connector import Error

def db_connect():
    connection = None
    try:
        connection = mysql.connector.connect(host='35.225.71.54',
                                             database='finance',
                                             user='investor',
                                             password='investor')
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            return connection
    except Error as e:
        print("Error connecting MySQL DB", e)
        return connection

def local_db_connect():
    connection = None
    try:
        connection = mysql.connector.connect(host='127.0.0.1',
                                             database='rmi',
                                             user='root',
                                             password='root')
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            return connection
    except Error as e:
        print("Error connecting Local MySQL DB", e)
        return connection


if __name__ == '__main__':
    db_connect()
    local_db_connect()
