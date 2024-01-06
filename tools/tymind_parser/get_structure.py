import json
import sys

def print_json_structure(d, indent=0):
    for key, value in d.items():
        print('  ' * indent + str(key), end=': ')
        if isinstance(value, dict):
            print("{}")
            print_json_structure(value, indent+1)
        elif isinstance(value, list):
            print("[...]")
            # Check if the list is not empty and that the first element is a dict
            if value and isinstance(value[0], dict):
                print_json_structure(value[0], indent+1)
            else:
                print("[...]")
        else:
            print(type(value).__name__)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python json_structure.py <path_to_json_file>")
        sys.exit(1)

    json_file_path = sys.argv[1]

    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            if isinstance(data, dict):
                print_json_structure(data)
            else:
                print(f"Expected a JSON object at the root. Got {type(data).__name__}")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
