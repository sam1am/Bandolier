import os
import json
import hashlib
import datetime
import pickle
import argparse
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.document_loaders import DirectoryLoader#, UnstructuredLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss

directory = '/home/sam/Insync/sam.garfield@gamp.ai/Google Drive - Shared drives/TNano'
supported_file_types = ['docx', 'pdf', 'csv', 'txt', 'md']
log_file = 'log_file.txt'
metadata = {}
index_name = 'hydrosonix'
workspace_directory = 'workspace'
index_directory = os.path.join(workspace_directory, index_name)

if not os.path.exists(index_directory):
    os.makedirs(index_directory)

pickle_file_path = os.path.join(index_directory, 'vectorizer.pickle')

model = SentenceTransformer('all-mpnet-base-v2')

parser = argparse.ArgumentParser(description='Index documents')
parser.add_argument('--reindex', action='store_true', help='Re-index documents')
args = parser.parse_args()

def load_documents(directory, glob_pattern, show_progress=True, use_multithreading=True):
    loader = DirectoryLoader(
        directory,
        glob=glob_pattern,
        show_progress=show_progress,
        use_multithreading=use_multithreading
    )
    return loader.load()

def split_text(document, chunk_size=100, chunk_overlap=20):
    content = document.content
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_text(content)

glob_pattern = "*.*"
documents = load_documents(directory, glob_pattern)

dimension = 768  # The dimension of your vectors. Assuming using SentenceTransformer('all-MiniLM-L6-v2') which has 768 dimensions
index = faiss.IndexFlatL2(dimension)

for document in documents:
    print("Indexing: " + document.metadata['source'])
    chunks = split_text(document)
    for text in chunks:
        text = text.strip()
        vector = model.encode([text])
        vector = np.array(vector, dtype=np.float32)
        index.add(vector)
        file_id = hashlib.md5(text.encode()).hexdigest()
        index_id = index.ntotal - 1
        metadata[file_id] = {
            'file_path': document.metadata['source'],
            'file_type': document.metadata['source'].split('.')[-1],
            'indexing_date': str(datetime.datetime.now()),
            'index_id': index_id,
            'text': text,
        }

index_file_path = os.path.join(index_directory, 'faiss.index')
faiss.write_index(index, index_file_path)

metadata_file_path = os.path.join(index_directory, 'docstore.json')
with open(metadata_file_path, 'w') as f:
    json.dump(metadata, f)
