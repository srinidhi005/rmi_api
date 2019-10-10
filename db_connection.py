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
            cursor = connection.cursor()
            cursor.execute("show tables")
            record = cursor.fetchall()
            print("Your connected to database: ", record)
            return connection
    except Error as e:
        print("Error reading data from MySQL table", e)
        return connection

if __name__ == '__main__':
    db_connect()
