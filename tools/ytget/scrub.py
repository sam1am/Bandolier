import json

def main():
    # Load data from JSON file
    with open('output_scrubbed.json', 'r') as f:
        data = json.load(f)

    # Create a new list that only includes videos where is_dialogue is 'TRUE'
    new_data = [video for video in data if video['is_dialogue'] == 'TRUE']

    # Write the new list back to the JSON file
    with open('output_scrubbed.json', 'w') as f:
        json.dump(new_data, f, indent=4)

if __name__ == "__main__":
    main()
