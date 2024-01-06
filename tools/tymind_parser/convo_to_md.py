import json
import sys
import os

# usage: python export_convo_to_md.py 'path_to_json.json' 'desired_uuid'


# Function to sanitize chatTitle to a valid filename
def sanitize_filename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c == ' ']).rstrip()

# Function to export conversation as markdown
def export_conversation_to_markdown(json_filepath, input_uuid):
    try:
        with open(json_filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Find the conversation with the given UUID
        conversation_found = False
        for chat in data['data']['chats']:
            for message in chat['messages']:
                if 'uuid' in message and message['uuid'] == input_uuid:
                    conversation_found = True
                    chat_title = sanitize_filename(chat['chatTitle'])
                    markdown_filename = f"{chat_title}.md"
                    
                    # Export the conversation to a markdown file
                    with open(markdown_filename, 'w', encoding='utf-8') as md_file:
                        md_file.write(f"# {chat_title}\n\n")  # Markdown title
                        for msg in chat['messages']:
                            # Ensure 'createdAt', 'role', and 'content' are present in msg
                            if all(k in msg for k in ('createdAt', 'role', 'content')):
                                timestamp = msg['createdAt']
                                role = msg.get('role', 'N/A').capitalize()
                                content = msg.get('content', 'No content provided.')
                                md_file.write(f"**{timestamp} {role}:** {content}\n\n")
                            else:
                                # Handle case where message is missing expected keys
                                print(f"Warning: Message is missing required keys and has been skipped. Message data: {msg}")

                    print(f"Conversation with UUID '{input_uuid}' has been exported to '{markdown_filename}'.")
                    break
        
        if not conversation_found:
            print(f"No conversation found with UUID '{input_uuid}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python export_convo_to_md.py <json_file_path> <uuid>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    uuid_to_export = sys.argv[2]
    
    if not os.path.exists(json_file_path):
        print(f"The file {json_file_path} does not exist.")
        sys.exit(1)

    export_conversation_to_markdown(json_file_path, uuid_to_export)
