# README.md

## Project Description 📝

The project consists of a powerful Python application along with a convenient Bash script utility designed to simplify code documentation. The Python script `app.py` interacts with OpenAI's GPT-4 model through the OpenAI API, generating succinct summaries of your codebase and crafting an up-to-date and styled README.md for your projects. The accompanying Bash script `code_summarize.sh` eases the setup by creating a Python virtual environment, handling alias additions, and running the Python tool in an automated fashion.

## Installation 🛠️

To get started with this project, follow the steps below. Please ensure you have Python installed on your system and that you have network connectivity to access the OpenAI API.

1. Clone the repository or download the source files to your local machine.

2. Navigate to the project directory in your terminal.

3. Set up your Python environment:
   
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Before running the Python script, create an `.env` file in the root of the project with your OpenAI API credentials:

   ```
   OPENAI_API_KEY='your-api-key-here'
   ```
   
5. Optionally, you can run `code_summarize.sh` to automate the virtual environment setup. If prompted, add the script alias to easily run the Python application in the future without manual environment setup.

## Usage 🚀

To use the Python documentation tool, make sure your virtual environment is active and simply execute:

```sh
python app.py
```

Follow the interactive prompts to select which files from your project should be summarized. The script will generate a `code_summary.md` file along with a neatly formatted `README.md` at the end of the process.

To utilize the convenience shell script, you may need to grant it execution permissions:

```sh
chmod +x code_summarize.sh
```

Once the alias is set, you can run the documentation tool with:

```sh
code_summarize
```

## Acknowledgements 🙌

Kudos to everyone who has contributed to making this tool efficient and user-friendly. A special mention to the creators of the libraries and APIs used within this project.

## License 📜

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute the code as per the license's conditions.