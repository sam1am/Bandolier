import os

SYSTEM_MESSAGES_DIR = 'system_messages'

def get_system_messages():
    """Retrieve a list of system messages."""
    if not os.path.exists(SYSTEM_MESSAGES_DIR):
        os.makedirs(SYSTEM_MESSAGES_DIR)
    
    return [f for f in os.listdir(SYSTEM_MESSAGES_DIR) if f.endswith('.md')]

def get_system_message(filename):
    """Retrieve a system message by filename."""
    with open(os.path.join(SYSTEM_MESSAGES_DIR, filename), 'r') as file:
        return file.read()
