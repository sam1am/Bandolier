from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(base_url=os.getenv("LLM_API_URL"), api_key=os.getenv("LLM_API_KEY"))

def process_query(query):
    completion = client.chat.completions.create(
        model="QuantFactory/Meta-Llama-3-8B-Instruct-GGUF",
        messages=[
            {"role": "user", "content": query}
        ],
        temperature=0.7,
    )
    response_text = completion.choices[0].message
    
    # Extract the text content from the response
    if hasattr(response_text, "content"):
        response_content = response_text.content
    else:
        response_content = str(response_text)
    
    return response_content