import sys
import tiktoken


def count_tokens(filename, model):
    # Load the encoding for the specified model
    encoding = tiktoken.encoding_for_model(model)

    # Read the file
    with open(filename, "r") as file:
        text = file.read()

    # Encode the text to tokens
    tokens = encoding.encode(text)

    # Count tokens
    token_count = len(tokens)

    return token_count


if __name__ == "__main__":
    filename = sys.argv[1]
    model = sys.argv[2]   # pass the model name as an argument
    token_count = count_tokens(filename, model)
    print(f"The file {filename} contains {token_count} tokens.")
