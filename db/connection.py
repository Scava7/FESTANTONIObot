# db/connection.py

import pymysql
from config import MYSQL_PASSWORD

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
