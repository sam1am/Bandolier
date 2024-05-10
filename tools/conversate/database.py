import sqlite3

db_connection = sqlite3.connect("history.db")
db_cursor = db_connection.cursor()
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
db_connection.commit()

def log_interaction(query, response):
    db_cursor.execute("""
        INSERT INTO interactions (query, response)
        VALUES (?, ?)
    """, (query, response))
    db_connection.commit()

def close_connection():
    db_connection.close()
