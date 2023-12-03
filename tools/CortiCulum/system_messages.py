import os

TEAM_DIR = 'Team'

def get_system_messages():
    """Retrieve a list of system messages."""
    if not os.path.exists(TEAM_DIR):
        os.makedirs(TEAM_DIR)
    
    return [f for f in os.listdir(TEAM_DIR) if f.endswith('.md')]

def get_system_message(filename):
    """Retrieve a system message by filename."""
    with open(os.path.join(TEAM_DIR, filename), 'r') as file:
        return file.read()
