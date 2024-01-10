DEFAULT_ASSISTANT_NAME = 'assistant'

assistants = []

def add_assistant(name=DEFAULT_ASSISTANT_NAME):
    """Add a new AI assistant."""
    assistants.append({
        'name': name,
        'history': [],
    })

def remove_assistant(name):
    """Remove an AI assistant by name."""
    global assistants
    assistants = [assistant for assistant in assistants if assistant['name'] != name]

def get_assistant(name):
    """Get an AI assistant by name."""
    for assistant in assistants:
        print("assistant: ", assistant)
        if assistant['name'] == name:
            return assistant
    # Handle case when there's no assistant with the given name
    print(f"No assistant with the name {name} found.")
    return None


def add_to_history(name, role, message):
    """Add a message to an assistant's history."""
    assistant = get_assistant(name)
    if assistant:
        assistant['history'].append({
            'role': role,
            'content': message
        })
