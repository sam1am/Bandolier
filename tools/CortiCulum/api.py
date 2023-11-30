import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_KEY')

def generate_message(prompt):
    """Generate a message using the OpenAI API."""
    response = openai.ChatCompletion.create(
        model="gpt-4", 
        messages=prompt,
    )

    message = response['choices'][0]['message']['content']
    
    return message
