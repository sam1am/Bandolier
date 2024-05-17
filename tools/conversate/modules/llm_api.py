import os
from dotenv import load_dotenv
import json
import yaml
import tiktoken
import re
from .database import load_recent_summaries

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

    num_recent_summaries = 3  # Adjust the number of recent summaries to include
    recent_summaries = load_recent_summaries(num_recent_summaries)

    system_prompt = load_file_contents("./entities/self/prompts/default.md").format(
        self_yaml=load_file_contents("./entities/self/self.yaml"),
        user_yaml=load_file_contents("./entities/user/user.yaml"),
        response_json=load_file_contents("./entities/self/prompts/response.json"),
        actions_md=load_file_contents("./entities/self/prompts/actions.md"),
        recent_memories="\n".join(recent_summaries),
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

    max_retries = 3
    retry_count = 0
    response_content = None

    while retry_count < max_retries:
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

        response_json = None
        if response_content and isinstance(response_content, str):
            json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
            if json_match:
                json_string = json_match.group()
                
                try:
                    response_json = json.loads(json_string)
                    if "short_answer" in response_json:
                        short_answer = response_json["short_answer"]
                    else:
                        print("'short_answer' key not found in the JSON response. Falling back to full answer!")
                except json.JSONDecodeError:
                    print("Invalid JSON format. Falling back to full answer!")
        else:
            print("Empty or non-string response received. Skipping JSON parsing.")

        if response_json and all(key in response_json for key in ["internal_thought", "short_answer", "action"]):
            # Serialize the JSON object with escaped newlines
            response_content = json.dumps(response_json)
            break  # Exit the loop if the response matches the expected schema
        else:
            retry_count += 1
            print(f"Retry {retry_count}: Response does not match the expected schema.")

    print(f"\n\nResponse:\n\n{response_content}\n\n")

    return response_content

def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens