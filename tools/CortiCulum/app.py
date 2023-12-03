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

run_chat()