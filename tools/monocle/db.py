# db.py
import sqlite3

def get_db_connection(db_file):
    conn = sqlite3.connect(db_file, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, title TEXT, content TEXT)''')
    return conn
