import mysql.connector
import configparser
import os
from flask import request

socketio = None
def register_socketio(sio):
    global socketio
    socketio = sio

def set_config():
    if os.path.isfile(conf):
        config.read(conf)
    else:
        config["DEFAULT"] = {
            "port": 5000,
            "ngrok": True,
            "login": 2026,
            "pin": 2026,
            "---------------": "--",
            "host": "localhost",
            "user": "py",
            "password": "py!!",
            "database": "schule"
        }
    with open(conf, "w") as f:
        config.write(f)


def get_connection():
    return mysql.connector.connect(
        host=get_conf("host"),
        user=get_conf("user"),
        password=get_conf("password"),
        database=get_conf("database")
    )


config = configparser.ConfigParser()
conf = "config.ini"



def get_conf(option, fallback=None):
    return config["DEFAULT"].get(option, fallback)


def log(name, wert, action):
    conn = get_connection()
    cursor = conn.cursor()
    user_ip = request.remote_addr
    cursor.execute(
        "INSERT INTO log (ip, name, wert, action) VALUES (%s, %s, %s, %s)",
        (user_ip, name, wert, action)
    )
    conn.commit()
    cursor.close()
    conn.close()




def background_updater():
    while True:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, wert FROM daten ORDER BY id DESC LIMIT 1")
        latest = cursor.fetchone()

        cursor.execute("SELECT id, name, wert FROM daten ORDER BY id DESC")
        alle = cursor.fetchall()

        cursor.execute("SELECT name, wert FROM daten ORDER BY wert DESC")
        rang = cursor.fetchall()

        cursor.execute("SELECT id, name, wert FROM daten ORDER BY id DESC")
        admin = cursor.fetchall()

        cursor.close()
        conn.close()

        if latest:
            id, name, wert = latest
        else:
            id, name, wert = None, None, None

        socketio.emit("update", {
            "id": id, "name": name, "wert": wert
        })

        socketio.emit("tabelle_update", {
            "daten": [{"id": r[0], "name": r[1], "wert": r[2]} for r in alle]
        })

        socketio.emit("rang_update", {
            "daten": [{"name": r[0], "wert": r[1]} for r in rang]
        })

        socketio.emit("admin_update", {
            "daten": [{"id": r[0], "name": r[1], "wert": r[2]} for r in admin]
        })

        socketio.sleep(1)
