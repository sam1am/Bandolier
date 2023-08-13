import os
import json
import hashlib
import datetime
import textract

import argparse
import numpy as np
import faiss
import schedule
import time
from sentence_transformers import SentenceTransformer


# Variable for running the script every X seconds
X = 900 #15 mins  

def extract_text(document):
    # Implement logic to extract text from each document
    pass

def job():
    directory = '/home/sam/Insync/sam.garfield@gamp.ai/Google Drive - Shared drives/TNano'
    supported_file_types = ['docx', 'pdf', 'csv', 'txt', 'md']
    documents = []
    skipped_files = []
    log_file = 'log_file.txt'
    metadata = {}
    index_name = 'tnano'  # Define your user-defined index name
    workspace_directory = 'workspace'
    index_directory = os.path.join(workspace_directory, index_name)

    # Create the directory if it doesn't exist
    if not os.path.exists(index_directory):
        os.makedirs(index_directory)

    model = SentenceTransformer('all-mpnet-base-v2')

    parser = argparse.ArgumentParser(description='Index documents')
    parser.add_argument('--reindex', action='store_true', help='Re-index documents')
    args = parser.parse_args()

    dimension = 768  # The dimension of your vectors

    # Define the full path for the index and the metadata file
    index_path = os.path.join(workspace_directory, index_name)
    index_file_path = os.path.join(index_path, f'{index_name}.index')
    metadata_file_path = os.path.join(index_path, 'metadata.json')

    # Make sure the directory for the index exists
    os.makedirs(index_path, exist_ok=True)

    # Check if the index file exists or if full re-indexing is requested
    if args.reindex or not os.path.exists(index_file_path):
        print("Re-indexing documents")
        # Delete the existing index and metadata files
        if os.path.exists(index_file_path):
            os.remove(index_file_path)
        if os.path.exists(metadata_file_path):
            os.remove(metadata_file_path)
        # Create the base index
        index_base = faiss.IndexFlatL2(dimension)
        # Create the IDMap index
        index = faiss.IndexIDMap(index_base)
        metadata = {}
    else:
        # Load the existing index and metadata
        print("Loading existing index")
        index = faiss.read_index(index_file_path)
        with open(metadata_file_path, 'r') as f:
            metadata = json.load(f)

    # Iterate over all documents and index them
    for document in documents:
        print("Indexing: " + document)
        try:
            chunks = extract_text(document)
            for text in chunks:
                text = text.strip()
                vector = model.encode(text)  # Use the Sentence Transformer model to encode the text
                vector = np.array([vector], dtype=np.float32)
                index.add_with_ids(vector, np.array([len(metadata)]))
                file_id = hashlib.md5(text.encode()).hexdigest()  # Use the chunk content to generate the ID
                index_id = len(metadata)
                metadata[file_id] = {
                    'file_path': document,
                    'file_type': document.split('.')[-1],
                    'indexing_date': str(datetime.datetime.now()),
                    'index_id': index_id,
                    'text': text,  # Add the chunk text to the metadata
                }
        except Exception as e:
            print(f"Error processing {document}: {str(e)}")
            skipped_files.append(document)

    # Save the index and the metadata
    faiss.write_index(index, index_file_path)
    with open(metadata_file_path, 'w') as f:
        json.dump(metadata, f)

    print(f"Successfully indexed {len(metadata)} documents.")
    if skipped_files:
        print(f"Skipped {len(skipped_files)} files due to errors.")
        with open(log_file, 'w') as f:
            for file in skipped_files:
                f.write(f"{file}\n")
job()

# Schedule the job every X seconds
schedule.every(X).seconds.do(job)

# Keep the script running
while True:
    schedule.run_pending()
    if schedule.idle_seconds() > 0:
        print(f"\rSleeping for {int(schedule.idle_seconds())} seconds until the next job.", end='')
    time.sleep(1)
