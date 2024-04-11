import os
import sys

from langchain_community.llms import Ollama

# Subconcious LLMS
llm_subconcious_sanity = Ollama(model="mistrallite")

# load prompt from ./tests/prompts/sanity_check.md
try:
    with open(os.path.join(os.path.dirname(__file__), "./tests/prompts/sanity_check.md")) as f:
        sanity_check = f.read()
except FileNotFoundError:
    sanity_check = ""
    print("Failed to load prompt from ./tests/prompts/sanity_check.md")

# Initialize conversation history
conversation_history = []

while True:
    user_input = input("User: ")
    
    if user_input.lower() == "exit":
        break
    
    # Add user input to conversation history
    conversation_history.append(f"User: {user_input}")
    
    # Concatenate conversation history with the sanity check prompt
    prompt = sanity_check + "\n" + "\n".join(conversation_history)
    
    result = llm_subconcious_sanity.invoke(prompt)
    
    # Add assistant response to conversation history
    conversation_history.append(f"Assistant: {result}")
    
    print(f"Assistant: {result}")