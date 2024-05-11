# from openai import OpenAI
from groq import Groq
import os
from dotenv import load_dotenv
import json
# import re

load_dotenv()

# client = OpenAI(base_url=os.getenv("LLM_API_URL"), api_key=os.getenv("LLM_API_KEY"))
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
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

    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    for query_text, response_text in message_history:
        messages.append({"role": "user", "content": query_text})
        messages.append({"role": "assistant", "content": response_text})
    
    messages.append({"role": "user", "content": query})
    
    completion = client.chat.completions.create(
        # model=os.getenv("LLM_MODEL"),
        model=os.getenv("GROQ_MODEL"),
        messages=messages,
        temperature=float(os.getenv("LLM_TEMP")),
        max_tokens=1000,
        response_format={"type": "json_object"}, #experimental
    )
    response_text = completion.choices[0].message

    # Extract the text content from the response
    if hasattr(response_text, "content"):
        response_content = response_text.content
    else:
        response_content = str(response_text)

    print(f"\n\nResponse:\n\n{response_content}\n\n")
            
    return response_content