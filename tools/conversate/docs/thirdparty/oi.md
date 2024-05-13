Basic Usage
​
Interactive Chat
To start an interactive chat in your terminal, either run interpreter from the command line:


interpreter
Or interpreter.chat() from a .py file:


interpreter.chat()
​
Programmatic Chat
For more precise control, you can pass messages directly to .chat(message) in Python:


interpreter.chat("Add subtitles to all videos in /videos.")

# ... Displays output in your terminal, completes task ...

interpreter.chat("These look great but can you make the subtitles bigger?")

# ...
​
Start a New Chat
In your terminal, Open Interpreter behaves like ChatGPT and will not remember previous conversations. Simply run interpreter to start a new chat:


interpreter
In Python, Open Interpreter remembers conversation history. If you want to start fresh, you can reset it:


interpreter.messages = []
​
Save and Restore Chats
In your terminal, Open Interpreter will save previous conversations to <your application directory>/Open Interpreter/conversations/.

You can resume any of them by running --conversations. Use your arrow keys to select one , then press ENTER to resume it.


interpreter --conversations
In Python, interpreter.chat() returns a List of messages, which can be used to resume a conversation with interpreter.messages = messages:


# Save messages to 'messages'
messages = interpreter.chat("My name is Killian.")

# Reset interpreter ("Killian" will be forgotten)
interpreter.messages = []

# Resume chat from 'messages' ("Killian" will be remembered)
interpreter.messages = messages
​
Configure Default Settings
We save default settings to the default.yaml profile which can be opened and edited by running the following command:


interpreter --profiles
You can use this to set your default language model, system message (custom instructions), max budget, etc.

Note: The Python library will also inherit settings from the default profile file. You can change it by running interpreter --profiles and editing default.yaml.

​
Customize System Message
In your terminal, modify the system message by editing your configuration file as described here.

In Python, you can inspect and configure Open Interpreter’s system message to extend its functionality, modify permissions, or give it more context.


interpreter.system_message += """
Run shell commands with -y so the user doesn't have to confirm them.
"""
print(interpreter.system_message)
​
Change your Language Model
Open Interpreter uses LiteLLM to connect to language models.

You can change the model by setting the model parameter:


Copy
interpreter --model gpt-3.5-turbo
interpreter --model claude-2
interpreter --model command-nightly
In Python, set the model on the object:


interpreter.llm.model = "gpt-3.5-turbo"
Find the appropriate “model” string for your language model here.


# Multiple Instances
To create multiple instances, use the base class, OpenInterpreter:


from interpreter import OpenInterpreter

agent_1 = OpenInterpreter()
agent_1.system_message = "This is a seperate instance."

agent_2 = OpenInterpreter()
agent_2.system_message = "This is yet another instance."
For fun, you could make these instances talk to eachother:


def swap_roles(messages):
    for message in messages:
        if message['role'] == 'user':
            message['role'] = 'assistant'
        elif message['role'] == 'assistant':
            message['role'] = 'user'
    return messages

agents = [agent_1, agent_2]

# Kick off the conversation
messages = [{"role": "user", "message": "Hello!"}]

while True:
    for agent in agents:
        messages = agent.chat(messages)
        messages = swap_roles(messages)