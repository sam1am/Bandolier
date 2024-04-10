import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

# Load text string from text.txt
with open('text_cleaned.txt', 'r') as file:
    text = file.read().replace('\n', '')

# Tokenize the text
tokens = num_tokens_from_string(text, "cl100k_base")

# Print the number of tokens
print("Number of tokens:", tokens)
