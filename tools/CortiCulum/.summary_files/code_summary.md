Output of tree command:
```
|-- .env
|-- .summary_files
    |-- code_summary.md
    |-- compressed_code_summary.md
    |-- previous_selection.json
|-- Team
    |-- default.md
|-- __pycache__
    |-- api.cpython-311.pyc
    |-- assistants.cpython-311.pyc
    |-- conversations.cpython-311.pyc
    |-- system_messages.cpython-311.pyc
    |-- user.cpython-311.pyc
|-- api.py
|-- app.py
|-- assistants.py
|-- conversations
    |-- 2023-12-02-21-48-33.md
    |-- 2023-12-02-21-53-23.md
|-- conversations.py
|-- requirements.txt
|-- system_messages.py
|-- user.py
|-- utils.py

```

---

./assistants.py
```
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
        if assistant['name'] == name:
            return assistant

def add_to_history(name, role, message):
    """Add a message to an assistant's history."""
    assistant = get_assistant(name)
    if assistant:
        assistant['history'].append({
            'role': role,
            'content': message
        })
```
---

./conversations.py
```
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
        file.write(f'**{name}**: {message}\n\n')  # added an extra newline

```
---

./utils.py
```
```
---

./api.py
```
import os
import json
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_KEY')
# openai.base_url = "https://..."

def generate_message(messages):
    """Generate a message using the OpenAI API."""
    response = openai.chat.completions.create(
        model="gpt-4", 
        messages=messages,
    )

    message = response.choices[0].message.content
    handle_json_response(response)
    
    return message


def handle_json_response(response):
    """Handle JSON response from OpenAI API."""
    if 'choices' in response:
        print(response['choices'])
```
---

./user.py
```
DEFAULT_USER_NAME = 'user'

user = {
    'name': DEFAULT_USER_NAME,
}

def set_user_name(name):
    """Set the user's name."""
    user['name'] = name

def get_user_name():
    """Get the user's name."""
    return user['name']
```
---

./system_messages.py
```
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
```
---

./app.py
```
import streamlit as st
from conversations import get_conversations, get_conversation, start_conversation, add_message
from assistants import add_assistant, remove_assistant, get_assistant, add_to_history
from system_messages import get_system_messages, get_system_message
from user import set_user_name, get_user_name
from api import generate_message

def run_chat():
    """Run the chat application."""
    st.title('CortiCulum')

    # Create Settings panel
    name = st.text_input('What is your name?', value=get_user_name(), max_chars=20)
    set_user_name(name)

    assistants = get_system_messages()  # system_messages and assistants are now the same
    selected_system_message = st.selectbox('Select a System Message / Assistant', assistants)

    # Get list of past conversation files
    past_conversations = get_conversations()

    # Add an option to start a new conversation
    past_conversations.append('Start a new conversation')

    # Let the user select from past conversations or start a new one
    selected_conversation = st.selectbox('Select a conversation', past_conversations)
    
    # Create Conversations panel
    col1, col2 = st.columns([1,3])
    
    with col1:
        st.subheader("Conversations")
        convo_list = st.empty()  # placeholder for the conversation list

    # Create Messages panel
    with col2:
        st.subheader("Messages")
        message_display = st.empty()  # placeholder for the message display
        user_message = st.text_input('Your message')
    
    # Only add system message when we start a new conversation
    if selected_conversation == 'Start a new conversation':
        selected_conversation = start_conversation()
        add_message(selected_conversation, "System", get_system_message(selected_system_message))
        # Initialize assistant with system message
        for assistant_name in [selected_system_message]:
            add_assistant(assistant_name)
            add_to_history(assistant_name, 'system', get_system_message(selected_system_message))
    
    # Add user message and generate assistant response
    if user_message:
        add_message(selected_conversation, name, user_message)
        add_to_history(selected_system_message, 'user', user_message)
        assistant_message = generate_message(get_assistant(selected_system_message)['history'])
        add_message(selected_conversation, selected_system_message, assistant_message)
        add_to_history(selected_system_message, 'assistant', assistant_message)

    # Update the conversation and message displays
    convo_list.markdown("\n".join(get_conversations()))
    message_display.markdown(get_conversation(selected_conversation))

run_chat()```
---

./Team/default.md
```
You are P, an expert personal AI assistant, tech genius, full stack developer, and friend of Sam Garfield. ```
---
