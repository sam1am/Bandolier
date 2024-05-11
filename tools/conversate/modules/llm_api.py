from openai import OpenAI
import os
from dotenv import load_dotenv
import yaml

load_dotenv()

client = OpenAI(base_url=os.getenv("LLM_API_URL"), api_key=os.getenv("LLM_API_KEY"))

def load_file_contents(file_path):
    with open(file_path, "r") as file:
        return file.read()

def process_query(query, message_history):
    default_prompt = load_file_contents("./prompts/default.md")
    penny_yaml = load_file_contents("./prompts/penny.yaml")
    user_yaml = load_file_contents("./prompts/user.yaml")
    response_yaml = load_file_contents("./prompts/response.yaml")

    system_prompt = default_prompt.format(
        penny_yaml=penny_yaml,
        user_yaml=user_yaml,
        response_yaml=response_yaml
    )

    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    for query_text, response_text in message_history:
        messages.append({"role": "user", "content": query_text})
        messages.append({"role": "assistant", "content": response_text})
    
    messages.append({"role": "user", "content": query})
    
    completion = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=messages,
        temperature=0.7,
    )
    response_text = completion.choices[0].message
    
    # Extract the text content from the response
    if hasattr(response_text, "content"):
        response_content = response_text.content
    else:
        response_content = str(response_text)
    
    return response_content