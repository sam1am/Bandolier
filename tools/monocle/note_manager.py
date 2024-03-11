# note_manager.py
from datetime import datetime
from db import get_db_connection

class NoteManager:
    def __init__(self, db_file):
        self.conn = get_db_connection(db_file)
    
    def fetch_note(self, current_note_id, direction):
        with self.conn:
            c = self.conn.cursor()
            if current_note_id is None:
                c.execute("SELECT id, title, content FROM notes ORDER BY id DESC LIMIT 1")
            else:
                if direction == 'previous':
                    c.execute("SELECT id, title, content FROM notes WHERE id < ? ORDER BY id DESC LIMIT 1", (current_note_id,))
                else:  # direction == 'next'
                    c.execute("SELECT id, title, content FROM notes WHERE id > ? ORDER BY id ASC LIMIT 1", (current_note_id,))
            return c.fetchone()
    
    def save_note(self, current_note_id, title, content):
        with self.conn:
            c = self.conn.cursor()
            if current_note_id is None:
                c.execute("INSERT INTO notes (timestamp, title, content) VALUES (?, ?, ?)", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), title, content))
            else:
                c.execute("UPDATE notes SET title = ?, content = ? WHERE id = ?", (title, content, current_note_id))
    
    def close(self):
        self.conn.close()
