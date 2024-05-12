# from openai import OpenAI
from groq import Groq
import anthropic
import os
from dotenv import load_dotenv
import json
# import re

load_dotenv()

# client = OpenAI(base_url=os.getenv("LLM_API_URL"), api_key=os.getenv("LLM_API_KEY"))
# client = Groq(
#     api_key=os.getenv("GROQ_API_KEY")
# )
client = anthropic.Client(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

def load_file_contents(file_path):
    with open(file_path, "r") as file:
        return file.read()

def process_query(query, message_history):
    default_prompt = load_file_contents("./prompts/default.md")
    penny_yaml = load_file_contents("./prompts/penny.yaml")
    user_yaml = load_file_contents("./prompts/user.yaml")
    response_json = load_file_contents("./prompts/response.json")

    system_prompt = default_prompt.format(
        penny_yaml=penny_yaml,
        user_yaml=user_yaml,
        response_json=response_json
    )

    messages = []

    # Add historical messages to the beginning of the messages list
    for query_text, response_text in message_history:
        if query_text.strip():
            messages.append({"role": "user", "content": query_text})            
        if response_text.strip():
            messages.append({"role": "assistant", "content": response_text})
            
    # Append the current query to the messages list
    if query.strip():
        messages.append({"role": "user", "content": query})
        # print(f"\n\nQuery:\n\n{query}\n\n")
    # messages.append({"role": "user", "content": query})
    
    # completion = client.chat.completions.create( # groq/openai
    completion = client.messages.create(
        # model=os.getenv("LLM_MODEL"),
        # model=os.getenv("GROQ_MODEL"),
        model=os.getenv("ANTHROPIC_MODEL"),
        system=system_prompt,        
        messages=messages,
        # temperature=float(os.getenv("LLM_TEMP")),
        max_tokens=1000,
        # response_format={"type": "json_object"}, #experimental
    )
    # response_text = completion.choices[0].message
    # print(completion.content)
    response_text = completion.content

    # Extract the text content from the response
    if isinstance(response_text, list) and len(response_text) > 0 and hasattr(response_text[0], "text"):
        response_content = response_text[0].text
    else:
        response_content = str(response_text)

    print(f"\n\nResponse:\n\n{response_content}\n\n")
            
    return response_content