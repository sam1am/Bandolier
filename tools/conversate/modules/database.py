import sqlite3
import time

def get_db_connection():
    return sqlite3.connect("./workspace/history.db")

def create_interactions_table():
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            query_uuid TEXT,
            query_audio_file TEXT,
            query_text TEXT,
            response_text TEXT,
            response_audio_file TEXT
        )
    """)
    db_connection.commit()
    db_connection.close()

def log_interaction(query_uuid, query_audio_file, query_text, response_text, response_audio_file):
    # print(f"{query_uuid} logged.")
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    db_cursor.execute("""
        INSERT INTO interactions (query_uuid, query_audio_file, query_text, response_text, response_audio_file)
        VALUES (?, ?, ?, ?, ?)
    """, (query_uuid, query_audio_file, query_text, response_text, response_audio_file))
    db_connection.commit()
    db_connection.close()

def get_last_messages(num_messages):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    try:
        db_cursor.execute("""
            SELECT query_text, response_text
            FROM interactions
            ORDER BY rowid ASC
            LIMIT ?
        """, (num_messages,))
    except sqlite3.OperationalError:
        print("Could not fetch messages from database.")
        return []
    messages = db_cursor.fetchall()
    db_connection.close()
    
    if not messages:
        return []
    
    return messages