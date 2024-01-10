import os

TEAM_DIR = './team'

def get_system_messages():
    """Retrieve a list of system messages."""
    if not os.path.exists(TEAM_DIR):
        os.makedirs(TEAM_DIR)
    
    return [os.path.splitext(f)[0] for f in os.listdir(TEAM_DIR) if f.endswith('.md')]

def get_system_message(filename):
    print("getting system message for filename: ", filename + ".md")
    """Retrieve a system message by filename."""
    with open(os.path.join(TEAM_DIR, filename), 'r') as file:
        return file.read()
