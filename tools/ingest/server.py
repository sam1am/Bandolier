from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import openai
import numpy as np
import faiss
import json
from sentence_transformers import SentenceTransformer

# Load OpenAI API key from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define your directory and index name here
workspace_directory = 'workspace'
index_name = 'tnano'  # Define your user-defined index name
index_directory = os.path.join(workspace_directory, index_name)

# Define the full path for the index and the metadata file
index_path = os.path.join(workspace_directory, index_name)
index_file_path = os.path.join(index_path, f'{index_name}.index')
metadata_file_path = os.path.join(index_path, 'metadata.json')

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-mpnet-base-v2')
# Load the index
if os.path.exists(index_file_path):
    faissindex = faiss.read_index(index_file_path)
else:
    print(f"Error: {index_file_path} does not exist or is not a valid index file.")


# Load the metadata
with open(metadata_file_path, 'r') as f:
    metadata = json.load(f)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ''
    if request.method == 'POST':
        query = request.form.get('query')

        # Vectorize the query using SentenceTransformer
        query_vector = model.encode([query])

        # Search the Faiss index
        D, I = faissindex.search(query_vector, 20)  # Search for the 10 most similar vectors

        # Compile Faiss results into a string
        faiss_results = ''
        for i in range(len(I[0])):
            for key in metadata:
                if metadata[key]['index_id'] == I[0][i]:
                    faiss_results += f"{metadata[key]['text']}\n"
        # truncate the string after 5k characters
        faiss_results = faiss_results[:5000]


        querystring = query + " Include references."
        # Pass the faiss results and the user's query to the OpenAI API
        completion = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are an AI expert in carbon nanotubes. Using the following context, answer the user\'s question. Always include references to the document name the answer came from: ' + faiss_results
                },
                {
                    'role': 'user',
                    'content': querystring
                }
            ]
        )
        result = completion.choices[0].message['content']

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
