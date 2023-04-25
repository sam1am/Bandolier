
code_summarize.py
```
import os
import json
import hashlib
from pathlib import Path
from ItsPrompt.prompt import Prompt
import openai
import config

# Allows users to select files from the current directory and create a code summary in markdown format.
# The selected files are saved in a json file so that the user can easily select the same files again.

#Instructoins: 
# 1. Run the script
# 2. Use arrow keys to select/deselect files, press ENTER to continue.
# 3. The code summary will be saved in the current directory as code_summary.md

openai.api_key = config.OPENAI_API_KEY

# Creates a hidden directory to store the summary files
def create_hidden_directory():
    hidden_directory = Path(".summary_files")
    if not hidden_directory.exists():
        hidden_directory.mkdir()

def generate_summary(file_content):
    print("Waiting for summary. This may take a few minutes...")
    response = openai.ChatCompletion.create(
        model="gpt-4",
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
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a code documenter. Your task is to create an updated README.md file for a project using the compressed code summary provided. Make it look nice, use emoji, and include the following sections: Project Description, Installation, and Usage. No license info is needed."},
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
        for file in selected_files:
            file_path = Path(file)
            metadata_path = Path(".summary_files") / f"{file}_metadata.json"

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


def display_files():
    print("List of files in the current directory:")
    files = [f for f in os.listdir() if os.path.isfile(f)]
    return files

def select_files(files, previous_selection):
    print("\nUse arrow keys to select/deselect files, press ENTER to continue.")
    selected_files = Prompt.checkbox(
        question="Select files",
        options=[(file, file) for file in files],
        pointer_at=0,
        default_checked=[file for file in previous_selection if file in files],
        min_selections=0,
    )
    return selected_files

def create_code_summary(selected_files):
    summary_directory = Path(".summary_files")  # Add this line
    summary_file = summary_directory / "code_summary.md"  # Update this line
    if summary_file.exists():
        summary_file.unlink()
    with open(summary_file, "a") as summary:  # Update this line
        for file in selected_files:
            summary.write(f"\n{file}\n```\n")
            with open(file, "r") as f:
                summary.write(f.read())
            summary.write("```\n---\n")


def read_previous_selection():
    hidden_directory = Path(".summary_files")  # Add this line
    selection_file = hidden_directory / "previous_selection.json"  # Update this line
    if selection_file.exists():
        with open(selection_file, "r") as f:  # Update this line
            previous_selection = json.load(f)
        return previous_selection
    else:
        return []

def write_previous_selection(selected_files):
    hidden_directory = Path(".summary_files")  # Add this line
    with open(hidden_directory / "previous_selection.json", "w") as f:  # Update this line
        json.dump(selected_files, f)

def main():
    create_hidden_directory()  # Add this line
    files = display_files()
    previous_selection = read_previous_selection()
    selected_files = select_files(files, previous_selection)
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
    readme_content = generate_readme(compressed_summary)

    # Save the updated README.md file
    readme_file = Path("README.md")
    if readme_file.exists():
        readme_file.unlink()
    with open(readme_file, "w") as f:
        f.write(readme_content)

    print("\nUpdated README.md file successfully generated in 'README.md'.")

if __name__ == "__main__":
    main()


```
---

renameto_config.py
```
#Rename this file to config.py
OPENAI_API_KEY = 'YOUR API KEY HERE'```
---
