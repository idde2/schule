import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="py",
        password="py!!",
        database="schule"
    )