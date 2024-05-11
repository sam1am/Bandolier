# from openai import OpenAI
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# client = OpenAI(base_url=os.getenv("LLM_API_URL"), api_key=os.getenv("LLM_API_KEY"))
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def process_query(query, message_history):
    messages = [
        {"role": "system", "content": "You are a helpful named Wilford. Do your best to help your user, Sam, and answer his queries."}
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
