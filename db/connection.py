# db/connection.py

import pymysql
import sqlite3
from config import MYSQL_PASSWORD

def get_connection():
    return sqlite3.connect("/path/to/festantonio.db")

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
