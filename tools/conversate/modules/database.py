import sqlite3

db_connection = sqlite3.connect("./workspace/history.db")
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

def log_interaction(query_uuid, query_audio_file, query_text, response_text, response_audio_file):
    db_cursor.execute("""
        INSERT INTO interactions (query_uuid, query_audio_file, query_text, response_text, response_audio_file)
        VALUES (?, ?, ?, ?, ?)
    """, (query_uuid, query_audio_file, query_text, response_text, response_audio_file))
    db_connection.commit()

def get_last_messages(num_messages):
    db_cursor.execute("""
        SELECT query_text, response_text
        FROM interactions
        ORDER BY timestamp DESC
        LIMIT ?
    """, (num_messages,))
    return db_cursor.fetchall()

def close_connection():
    db_connection.close()