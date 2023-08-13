import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

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
index = faiss.read_index(index_file_path)

# Load the metadata
with open(metadata_file_path, 'r') as f:
    metadata = json.load(f)

# Define your query
query = "Can I kill quagga mussels with sound waves?"
print(f"Query: {query}\n\n")
# Vectorize the query using SentenceTransformer
query_vector = model.encode([query])

# Check the shape of your query vector
print("Query vector shape:", query_vector.shape)

# Check the dimensionality of your Faiss index
print("Faiss index dimensionality:", index.d)

# Search the index
D, I = index.search(query_vector, 10)  # Search for the 10 most similar vectors

# Print the results
for i in range(len(I[0])):
    print(f"Result {i+1}:")
    print(f"Distance: {D[0][i]}")
    for key in metadata:
        if metadata[key]['index_id'] == I[0][i]:
            print(f"Metadata: {metadata[key]}")
            print(f"Relevant text: {metadata[key]['text']}")  # Print the relevant chunk of text
    print("\n")
