import os
import json
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key

# openai.base_url = "https://..."

def generate_message(messages):
    """Generate a message using the OpenAI API."""
    response = openai.chat.completions.create(
        model="gpt-4", 
        messages=messages,
    )

    message = response.choices[0].message.content
    handle_json_response(response)
    
    return message


def handle_json_response(response):
    """Handle JSON response from OpenAI API."""
    if 'choices' in response:
        print(response['choices'])
