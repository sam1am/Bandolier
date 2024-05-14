import os
from dotenv import load_dotenv
import json
import yaml
import tiktoken

# from .database import log_side_conversation

import uuid
from interpreter import OpenInterpreter
import threading

load_dotenv()

def load_file_contents(file_path):
    with open(file_path, "r") as file:
        return file.read()

def process_query(query, message_history, is_journal_update=False, config_name="deep_reason"):
    # Load the configuration file
    with open("./entities/self/mind_models.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)

    # Get the specified configuration
    client_config = config[config_name]

    # Load the client based on the provider
    if client_config["provider"] == "openai":
        from openai import OpenAI
        client = OpenAI(base_url=os.getenv("LLM_API_URL"), api_key=os.getenv("LLM_API_KEY"))
        print("Going local")
    elif client_config["provider"] == "groq":
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        print("Requesting Groq")
    elif client_config["provider"] == "anthropic":
        import anthropic
        client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
        print("Requesting Anthropic")
    else:
        raise ValueError(f"Unsupported provider: {client_config['provider']}")

    system_prompt = load_file_contents("./entities/self/prompts/default.md").format(
        self_yaml=load_file_contents("./entities/self/self.yaml"),
        user_yaml=load_file_contents("./entities/user/user.yaml"),
        response_json=load_file_contents("./entities/self/prompts/response.json"),
        actions_md=load_file_contents("./entities/self/prompts/actions.md"),
    )

    messages = []

    if is_journal_update:
        messages = [{"role": "user", "content": message[0] + "\n" + message[1]} for message in message_history]
        messages.append({"role": "user", "content": query})
    else:
        # Add historical messages to the beginning of the messages list
        for query_text, response_text in message_history:
            if query_text.strip():
                messages.append({"role": "user", "content": query_text})
            if response_text.strip():
                messages.append({"role": "assistant", "content": response_text})

        # Append the current query to the messages list
        if query.strip():
            messages.append({"role": "user", "content": query})

    # get the token count of our system prompt
    print(f"System prompt tokens: {num_tokens_from_string(system_prompt)}")
    

    if client_config["provider"] == "anthropic":
        completion = client.messages.create(
            model=client_config["model"],
            system=system_prompt,
            messages=messages,
            temperature=client_config["temperature"],
            max_tokens=client_config["max_tokens"],
        )
        response_text = completion.content
        if isinstance(response_text, list) and len(response_text) > 0 and hasattr(response_text[0], "text"):
            response_content = response_text[0].text
        else:
            response_content = str(response_text)

    else:
        completion = client.chat.completions.create(
            model=client_config["model"],
            messages=messages,
            temperature=client_config["temperature"],
            max_tokens=client_config["max_tokens"],
        )
        response_text = completion.choices[0].message
        if isinstance(response_text, dict) and "content" in response_text:
            response_content = response_text["content"]
        elif hasattr(response_text, "content"):
            response_content = response_text.content
        else:
            response_content = str(response_text)

    # Check if the response contains a side conversation request
    if "[[side_conversation]]" in response_content:
        # Extract the side conversation prompt
        side_conversation_prompt = response_content.split("[[side_conversation]]")[1].strip()

        # Create a new thread for the side conversation
        side_conversation_thread = threading.Thread(target=conduct_side_conversation, args=(side_conversation_prompt,))
        side_conversation_thread.start()

        # Remove the side conversation request from the response
        response_content = response_content.split("[[side_conversation]]")[0].strip()

    print(f"\n\nResponse:\n\n{response_content}\n\n")

    return response_content

def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens

def conduct_side_conversation(side_conversation_prompt):
    # Create two OpenInterpreter instances for the side conversation
    agent_1 = OpenInterpreter()
    agent_1.system_message = "You are Agent 1 in the side conversation."

    agent_2 = OpenInterpreter()
    agent_2.system_message = "You are Agent 2 in the side conversation."

    def swap_roles(messages):
        for message in messages:
            if message['role'] == 'user':
                message['role'] = 'assistant'
            elif message['role'] == 'assistant':
                message['role'] = 'user'
        return messages

    agents = [agent_1, agent_2]

    # Generate a unique UUID for the side conversation
    side_conversation_uuid = str(uuid.uuid4())

    # Kick off the side conversation
    messages = [{"role": "user", "content": side_conversation_prompt}]

    while True:
        for agent in agents:
            messages = agent.chat(messages)
            messages = swap_roles(messages)

            # Log each message in the side conversation
            for message in messages:
                # log_side_conversation(side_conversation_uuid, message["role"], message["content"])
                print(message)

            # Check if the side conversation has ended
            if any("[[end_side_conversation]]" in message["content"] for message in messages):
                return
