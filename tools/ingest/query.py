import os
import json
import pickle
import numpy as np
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer

# Define your directory and index name here
workspace_directory = 'workspace'
index_name = 'tnano'  # Define your user-defined index name
pickle_file_path = os.path.join(workspace_directory, 'vectorizer.pickle')

# Define the full path for the index and the metadata file
index_path = os.path.join(workspace_directory, index_name)
index_file_path = os.path.join(index_path, f'{index_name}.index')
metadata_file_path = os.path.join(index_path, 'metadata.json')

# Load the vectorizer
vectorizer = pickle.load(open(pickle_file_path, "rb"))

# Load the index
index = faiss.read_index(index_file_path)

# Load the metadata
with open(metadata_file_path, 'r') as f:
    metadata = json.load(f)

# Define your query
query = "Can I kill quagga mussels with sound waves?"
print(f"Query: {query}\n\n")

# Vectorize the query
query_vector = vectorizer.transform([query]).toarray()[0]

# Search the index
D, I = index.search(np.array([query_vector], dtype=np.float32), 10)  # Search for the 10 most similar vectors

# Print the results
for i in range(len(I[0])):
    print(f"Result {i+1}:")
    print(f"Distance: {D[0][i]}")
    for key in metadata:
        if metadata[key]['index_id'] == I[0][i]:
            print(f"Metadata: {metadata[key]}")
            print(f"Relevant text: {metadata[key]['text']}")  # Print the relevant chunk of text
    print("\n")


