# db/connection.py
import sqlite3
import os
import pymysql
from config import MYSQL_PASSWORD, DB_PATH

def get_connection():
     # Assicura che la cartella data/ esista
     os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
     return sqlite3.connect(DB_PATH)

def get_mysql_connection():
    return pymysql.connect(
        host="Scava7.mysql.pythonanywhere-services.com",
        user="Scava7",
        password=MYSQL_PASSWORD,
        database="Scava7$festantonio",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
