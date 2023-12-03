import os
import json
import hashlib
from pathlib import Path
from ItsPrompt.prompt import Prompt
import openai
import subprocess
import pathspec
from dotenv import load_dotenv  # Added this line

IGNORE_LIST = [".git", "venv"]


# Allows users to select files from the current directory and create a code summary in markdown format.
# The selected files are saved in a json file so that the user can easily select the same files again.

#Instructoins: 
# 1. Run the script
# 2. Use arrow keys to select/deselect files, press ENTER to continue.
# 3. The code summary will be saved in the current directory as code_summary.md

# Load .env file
load_dotenv()  # Added this line

# Fetch the API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Modified this line


# Creates a hidden directory to store the summary files
def create_hidden_directory():
    hidden_directory = Path(".summary_files")
    if not hidden_directory.exists():
        hidden_directory.mkdir()

def get_tree_output():
    def walk_directory_tree(directory, level, gitignore_specs):
        output = ""
        for entry in sorted(os.listdir(directory)):
            entry_path = os.path.join(directory, entry)
            relative_entry_path = os.path.relpath(entry_path, ".")

            # Check if the entry is not in the IGNORE_LIST
            if not any(ignore_item in entry_path for ignore_item in IGNORE_LIST):
                if gitignore_specs is None or not gitignore_specs.match_file(relative_entry_path):
                    if os.path.isfile(entry_path):
                        output += f"{' ' * (4 * level)}|-- {entry}\n"
                    elif os.path.isdir(entry_path):
                        output += f"{' ' * (4 * level)}|-- {entry}\n"
                        output += walk_directory_tree(entry_path, level + 1, gitignore_specs)
        return output

    gitignore_specs = parse_gitignore()
    tree_output = walk_directory_tree(".", 0, gitignore_specs)
    return tree_output


def generate_summary(file_content):
    print("Waiting for summary. This may take a few minutes...")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a code documenter. Your purpose is to provide useful summaries for inclusion"
             " as reference for future prompts. Provide a concise summary of the given code and any notes that will be useful for other ChatBots to understand how it works."
             " Include specific documentation about each function, class, and relevant parameters."},
            {"role": "user", "content": file_content}
        ],
        max_tokens=2500,  # Adjust the token length as needed
    )
    return response['choices'][0]['message']['content']

def generate_readme(compressed_summary):
    print("Generating updated README.md file...")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a code documenter. Your task is to create an updated README.md file for a project using the compressed code summary provided. Make it look nice, use emoji, and include the following sections: Project Description, Installation, and Usage. You can also include a section for Acknowledgements and a section for License."},
            {"role": "user", "content": compressed_summary}
        ],
        max_tokens=1500,  # Adjust the token length as needed
    )
    readme_content = response['choices'][0]['message']['content']
    return readme_content


def create_compressed_summary(selected_files):
    summary_directory = Path(".summary_files")
    compressed_summary_file = summary_directory / "compressed_code_summary.md"
    if compressed_summary_file.exists():
        compressed_summary_file.unlink()

    with open(compressed_summary_file, "a") as summary:
        # Include the output of the tree command at the beginning
        tree_output = get_tree_output()
        summary.write(f"Output of tree command:\n```\n{tree_output}\n```\n\n---\n")

        for file in selected_files:

            file_path = Path(file)
            relative_path = file_path.relative_to(".")
            metadata_directory = summary_directory / relative_path.parent
            metadata_directory.mkdir(parents=True, exist_ok=True)
            metadata_path = metadata_directory / f"{file_path.name}_metadata.json"


            if file == "main.py":
                summary.write(f"\n{file}\n```\n")
                with open(file, "r") as f:
                    file_content = f.read()
                    summary.write(file_content)
                summary.write("```\n---\n")
            else:
                if metadata_path.exists():
                    print(f"File {file} has been summarized before. Checking if it has been modified...")
                    with open(metadata_path, "r") as metadata_file:
                        metadata = json.load(metadata_file)
                    saved_hash = metadata["hash"]

                    with open(file, "r") as f:
                        file_content = f.read()
                    current_hash = hashlib.md5(file_content.encode("utf-8")).hexdigest()

                    if saved_hash == current_hash:
                        print(f"File {file} has not been modified. Using saved summary...")
                        file_summary = metadata["summary"]
                    else:
                        print(f"File {file} has been modified. Generating new summary...")
                        file_summary = generate_summary(file_content)
                        metadata = {"hash": current_hash, "summary": file_summary}
                        with open(metadata_path, "w") as metadata_file:
                            json.dump(metadata, metadata_file)
                else:
                    print(f"File {file} has not been summarized before. Generating summary...")
                    with open(file, "r") as f:
                        file_content = f.read()
                    file_summary = generate_summary(file_content)
                    current_hash = hashlib.md5(file_content.encode("utf-8")).hexdigest()
                    metadata = {"hash": current_hash, "summary": file_summary}
                    with open(metadata_path, "w") as metadata_file:
                        json.dump(metadata, metadata_file)

                print(f"Saving summary for {file}...")

                summary.write(f"\n{file}\n```\n")
                summary.write(file_summary)
                summary.write("```\n---\n")

                print("-----------------------------------")


def parse_gitignore():
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            gitignore_content = f.read()
        gitignore_specs = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, gitignore_content.splitlines())
    else:
        gitignore_specs = None
    return gitignore_specs

def display_files():
    print("List of files in the current directory and its subdirectories:")
    files = []
    gitignore_specs = parse_gitignore()
    for root, _, filenames in os.walk("."):

        # Check if the root directory is in the IGNORE_LIST
        if not any(ignore_item in root for ignore_item in IGNORE_LIST):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if gitignore_specs is None or not gitignore_specs.match_file(file_path):
                    files.append(file_path)
    return files



def select_files(files, previous_selection):
    gitignore_specs = parse_gitignore()
    filtered_files = [file for file in files if gitignore_specs is None or not gitignore_specs.match_file(file)]

    print("\nUse arrow keys and spacebar to select/deselect files, press ENTER to continue.")
    selected_files = Prompt.checkbox(
        question="Select files",
        options=[(file, file) for file in filtered_files],
        pointer_at=0,
        default_checked=[file for file in previous_selection if file in filtered_files],
        min_selections=0,
    )
    return selected_files


def create_code_summary(selected_files):
    summary_directory = Path(".summary_files")
    summary_file = summary_directory / "code_summary.md"
    if summary_file.exists():
        summary_file.unlink()
    with open(summary_file, "a") as summary:
        # Include the output of the tree command at the beginning
        tree_output = get_tree_output()
        summary.write(f"Output of tree command:\n```\n{tree_output}\n```\n\n---\n")

        for file_path in selected_files:
            summary.write(f"\n{file_path}\n```\n")
            with open(file_path, "r") as f:
                summary.write(f.read())
            summary.write("```\n---\n")




def read_previous_selection():
    hidden_directory = Path(".summary_files") 
    selection_file = hidden_directory / "previous_selection.json" 
    if selection_file.exists():
        with open(selection_file, "r") as f: 
            previous_selection = json.load(f)
        return previous_selection
    else:
        return []

def write_previous_selection(selected_files):
    hidden_directory = Path(".summary_files")  
    with open(hidden_directory / "previous_selection.json", "w") as f: 
        json.dump(selected_files, f)

def main():
    create_hidden_directory() 
    files = display_files()
    filtered_files = [file for file in files if not file.startswith('./.')]  
    previous_selection = read_previous_selection()
    selected_files = select_files(filtered_files, previous_selection) 
    write_previous_selection(selected_files)
    create_code_summary(selected_files)
    create_compressed_summary(selected_files)
    print("\nCode summary successfully created in '.summary_files/code_summary.md'.")
    print("\nCompressed code summary successfully created in '.summary_files/compressed_code_summary.md'.")
    # Load compressed code summary
    summary_directory = Path(".summary_files")
    compressed_summary_file = summary_directory / "compressed_code_summary.md"
    with open(compressed_summary_file, "r") as f:
        compressed_summary = f.read()

    # Generate updated README.md file using GPT-4
    # readme_content = generate_readme(compressed_summary)

    # Save the updated README.md file
    # readme_file = Path("README.md")
    # if readme_file.exists():
        
    # with open(readme_file, "w") as f:
    #     f.write(readme_content)

    # print("\nUpdated README.md file successfully generated in 'README.md'.")

if __name__ == "__main__":
    main()


