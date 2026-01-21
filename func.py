import mysql.connector

import configparser
import os

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="py",
        password="py!!",
        database="schule"
    )





config = configparser.ConfigParser()
conf = "config.ini"

def set_config():
    if os.path.isfile(conf):
        config.read(conf)
    else:
        config["DEFAULT"] = {
            "port": 5000,
            "ngrok": True,
            "login": 2026,
            "pin": 2026
        }
    with open(conf, "w") as f:
        config.write(f)





def get_conf(option, fallback=None):
    return config["DEFAULT"].get(option, fallback)

