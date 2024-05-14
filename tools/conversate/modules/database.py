import sqlite3
from datetime import datetime
from .llm_api import process_query
import os
import json

os.environ['TZ'] = 'MST'

def get_db_connection():
    return sqlite3.connect("./workspace/history.db")

def create_interactions_table():
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT (datetime('now', 'localtime')),
            query_uuid TEXT,
            query_audio_file TEXT,
            query_text TEXT,
            response_text TEXT,
            response_audio_file TEXT
        )
    """)
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS side_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT,
            role TEXT,
            content TEXT
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
        today = datetime.now().date()
        db_cursor.execute("""
            SELECT query_text, response_text
            FROM interactions
            WHERE DATE(timestamp) = ?
            ORDER BY rowid ASC
            LIMIT ?
        """, (today, num_messages))
    except sqlite3.OperationalError:
        print("Could not fetch messages from database.")
        return []
    messages = db_cursor.fetchall()
    db_connection.close()
    
    if not messages:
        return []
    
    return messages

def get_distinct_dates():
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    db_cursor.execute("""
        SELECT DISTINCT DATE(timestamp) AS date
        FROM interactions
        ORDER BY date
    """)
    dates = db_cursor.fetchall()
    db_connection.close()
    return [date[0] for date in dates]

def get_messages_by_date(date):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    db_cursor.execute("""
        SELECT query_text, response_text
        FROM interactions
        WHERE DATE(timestamp) = ?
        ORDER BY rowid ASC
    """, (date,))
    messages = db_cursor.fetchall()
    db_connection.close()
    return messages

def check_missing_journal_entries():
    
    journal_folder = "./workspace/journal"
    os.makedirs(journal_folder, exist_ok=True)

    distinct_dates = get_distinct_dates()
    today = datetime.now().date()

    for date in distinct_dates:
        if date == today:
            continue

        journal_file = os.path.join(journal_folder, f"{date}.md")
        if not os.path.exists(journal_file):
            print(f"Journaling for {date}...")
            messages = get_messages_by_date(date)
            journal_prompt = load_file_contents("./entities/self/prompts/journal.md")
            journal_entry = process_query(journal_prompt, messages)

            # if journal_entry can be loaded as a json object, get short_answer
            try:
                journal_entry = json.loads(journal_entry)
                if "short_answer" in journal_entry:
                    journal_entry = journal_entry["short_answer"]
            except json.JSONDecodeError:
                journal_entry = journal_entry

            with open(journal_file, "w") as file:
                file.write(journal_entry)

            print("Done!")

def load_file_contents(filename):
    with open(filename, "r") as file:
        return file.read()

def log_side_conversation(side_conversation_uuid, side_conversation_messages):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    for message in side_conversation_messages:
        db_cursor.execute("""
            INSERT INTO side_conversations (uuid, role, content)
            VALUES (?, ?, ?)
        """, (side_conversation_uuid, message["role"], message["content"]))
    db_connection.commit()
    db_connection.close()