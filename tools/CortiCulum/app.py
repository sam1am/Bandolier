import streamlit as st
from conversations import get_conversations, get_conversation, start_conversation, add_message
from assistants import add_assistant, remove_assistant, get_assistant, add_to_history
from system_messages import get_system_messages, get_system_message
from user import set_user_name, get_user_name
from api import generate_message

def run_chat():
    """Run the chat application."""
    st.title('CortiCulum')

    conversations = get_conversations()
    selected_conversation = st.selectbox('Select a conversation', ['New conversation'] + conversations)

    if selected_conversation == 'New conversation':
        selected_conversation = start_conversation()

    conversation = get_conversation(selected_conversation)

    st.markdown(conversation)

run_chat()
