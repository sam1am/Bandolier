import json
import os
import sys
import shutil

# Function to sanitize a folder name to remove invalid characters
def sanitize_folder_name(folder_name):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        folder_name = folder_name.replace(char, "")
    return folder_name[:255]

# Function to create a dictionary mapping folder IDs to their titles
def create_folder_title_map(folders):
    return {folder['id']: folder['title'] for folder in folders}

# Function to export all conversations in a json file to markdown files
def export_json_to_markdown(json_filepath):
    with open(json_filepath, 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)

    if 'data' not in json_data or 'chats' not in json_data['data'] or 'folders' not in json_data['data']:
        print("The JSON file is missing required 'data', 'chats', or 'folders' keys.")
        return

    # Create a map of folder IDs to folder titles
    folder_title_map = create_folder_title_map(json_data['data']['folders'])

    # Determine the export directory name based on the JSON file name
    json_filename = os.path.basename(json_filepath)
    export_dir_name = os.path.splitext(json_filename)[0]
    parent_export_dir = os.path.join(os.path.dirname(json_filepath), sanitize_folder_name(export_dir_name))
    if os.path.exists(parent_export_dir):
        shutil.rmtree(parent_export_dir)
    os.makedirs(parent_export_dir)
    
    total_chats = 0

    # Loop over each chat
    for chat in json_data['data']['chats']:
        chat_id = chat.get('chatID')
        if chat_id is None:
            continue  # Skip chats without an ID
        
        # Determine the folder name using the folder ID to title map; fall back to "No Folder" if not found
        folder_name = sanitize_folder_name(folder_title_map.get(chat.get('folderID'), "No Folder"))
        chat_title = chat.get('chatTitle', chat_id)

        # Create a folder for the chats if it doesn't already exist
        folder_path = os.path.join(parent_export_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # Use chatTitle for the markdown filename, and sanitize it
        sanitized_chat_title = sanitize_folder_name(chat_title)
        conversation_filepath = os.path.join(folder_path, f"{sanitized_chat_title}.md")
        with open(conversation_filepath, 'w', encoding='utf-8') as conversation_file:
            conversation_file.write(f"# {sanitized_chat_title}\n\n")

            # Check for 'messages' in chat and print error if not found
            if 'messages' not in chat:
                print(f"Chat data does not contain 'messages' key for chat: {chat_id}")
                continue

            for message in chat['messages']:
                timestamp = message.get('createdAt', 'Unknown timestamp')
                role = message.get('role', 'N/A').capitalize()
                content = message.get('content', 'No content provided.')
                conversation_file.write(f"**{timestamp} {role}:** {content}\n\n")

        total_chats += 1

    print(f"All conversations have been processed. Total: {total_chats}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the JSON file as an argument.")
        sys.exit(1)

    json_file_path = sys.argv[1]

    try:
        export_json_to_markdown(json_file_path)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
