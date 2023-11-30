import os
import json
from datetime import datetime

CONVERSATIONS_DIR = 'conversations'

def get_conversations():
    """Retrieve a list of past conversations."""
    if not os.path.exists(CONVERSATIONS_DIR):
        os.makedirs(CONVERSATIONS_DIR)
    
    return [f for f in os.listdir(CONVERSATIONS_DIR) if f.endswith('.md')]

def get_conversation(filename):
    """Retrieve a conversation by filename."""
    with open(os.path.join(CONVERSATIONS_DIR, filename), 'r') as file:
        return file.read()

def start_conversation():
    """Start a new conversation and return its filename."""
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    filename = f'{timestamp}.md'
    
    with open(os.path.join(CONVERSATIONS_DIR, filename), 'w') as file:
        file.write('')
    
    return filename

def add_message(filename, name, message):
    """Add a message to a conversation."""
    with open(os.path.join(CONVERSATIONS_DIR, filename), 'a') as file:
        file.write(f'**{name}**: {message}\n')
