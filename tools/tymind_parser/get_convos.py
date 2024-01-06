import json
import sys

def extract_chats_by_title_and_uuid(json_filepath):
    # Open and load the JSON file
    with open(json_filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Initialize a list to hold chats with titles and UUIDs
    chats_with_titles_and_uuids = []

    # Loop through each chat in the JSON data
    for chat in data['data']['chats']:
        # Extract the chat title
        title = chat.get('chatTitle', 'Unknown Title')
        # Use the UUID of the first message in the chat as the chat UUID
        uuid = chat['messages'][0]['uuid'] if chat['messages'] else 'No UUID'
        chats_with_titles_and_uuids.append((title, uuid))

    return chats_with_titles_and_uuids


if __name__ == "__main__":
    # Check if the file path was provided as the first argument
    if len(sys.argv) < 2:
        print("Please provide the JSON file as an argument.")
        sys.exit(1)

    # Get the JSON file path from the first argument
    json_file_path = sys.argv[1]

    try:
        chats = extract_chats_by_title_and_uuid(json_file_path)
        # Print the results
        for title, uuid in chats:
            print(f"Title: {title}, UUID: {uuid}")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
