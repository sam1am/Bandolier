import streamlit as st
from conversations import get_conversations, get_conversation, start_conversation, add_message
from assistants import add_assistant, remove_assistant, get_assistant, add_to_history
from system_messages import get_system_messages, get_system_message
from user import set_user_name, get_user_name
from api import generate_message

def run_chat():
    """Run the chat application."""
    st.title('CortiCulum')

    # Initialize session state for current conversation
    if 'conversation' not in st.session_state:
        st.session_state.conversation = None

    # Initialize session state for Send button status
    if 'sending' not in st.session_state:
        st.session_state.sending = False

    # Create Settings panel
    name = st.text_input('What is your name?', value=get_user_name(), max_chars=20)
    set_user_name(name)

    assistants = get_system_messages()  # system_messages and assistants are now the same
    selected_system_message = st.selectbox('Select a System Message / Assistant', assistants)

    # Get list of past conversation files
    past_conversations = get_conversations()

    selected_conversation = "Start a new conversation"

    # Create Conversations panel
    col1, col2 = st.columns([1,3])

    with col1:
        st.subheader("Conversations")
        for convo in past_conversations:
            if st.button(f"Load {convo}"):
                st.session_state.conversation = convo

    # Create Messages panel
    with col2:
        st.subheader("Messages")
        message_display = st.empty()  # placeholder for the message display

        with st.form(key='message_form'):
            user_message = st.text_input('Your message', key='user_message')
            submit_button = st.form_submit_button(label='Send', disabled=st.session_state.sending)

        # Start a new conversation if there's none
        if st.session_state.conversation is None:
            st.session_state.conversation = start_conversation()
            for assistant_name in [selected_system_message]:
                add_assistant(assistant_name)
                add_to_history(assistant_name, 'system', get_system_message(selected_system_message))

        # Add user message and generate assistant response
        if submit_button and user_message:
            st.session_state.sending = True
            add_message(st.session_state.conversation, name, user_message)
            add_to_history(selected_system_message, 'user', user_message)
            assistant_message = generate_message(get_assistant(selected_system_message)['history'])
            add_message(st.session_state.conversation, selected_system_message, assistant_message)
            add_to_history(selected_system_message, 'assistant', assistant_message)

            # Here we clear the form and enable the Send button
            st.session_state.sending = False
            st.rerun()

        # Update the message displays
        message_display.markdown(get_conversation(st.session_state.conversation))

run_chat()
