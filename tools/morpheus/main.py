from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers
from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from safetensors import safe_open

from IPython.display import display, HTML
import json
import time
import pathlib

loader = DirectoryLoader("/home/sam/Resilio Sync/OBSIDIAN/Transcriptions", glob="*.md", loader_cls=TextLoader)
dimension = 768

print("Hello")

# interpret information in the documents
documents = loader.load()
print("Loaded {} documents".format(len(documents)))
splitter = RecursiveCharacterTextSplitter()
texts = splitter.split_documents(documents)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'})

# create and save the local database
db = FAISS.from_documents(texts, embeddings)
db.save_local("faiss")

# prepare the template we will use when prompting the AI
template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Context: {context}
Question: {question}
Only return the helpful answer below and nothing else.
Helpful answer:
"""

# load the language model
config = {'max_new_tokens': 256, 'temperature': 0.01}
llm = CTransformers(model='/home/sam/oobabooga_linux/text-generation-webui/models/TheBloke_Hermes-LLongMA-2-7B-8K-GGML/hermes-llongma-2-7b-8k.ggmlv3.q2_K.bin',
                    model_type='llama', config=config)

# load the interpreted information from the local database
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'})
db = FAISS.load_local("faiss", embeddings)

# prepare a version of the llm pre-loaded with the local content
retriever = db.as_retriever(search_kwargs={'k': 2})
prompt = PromptTemplate(
    template=template,
    input_variables=['context', 'question'])

QA_LLM = RetrievalQA.from_chain_type(llm=llm,
                                     chain_type='stuff',
                                     retriever=retriever,
                                     return_source_documents=True,
                                     chain_type_kwargs={'prompt': prompt})

def query(model, question):
    model_path = model.combine_documents_chain.llm_chain.llm.model
    model_name = pathlib.Path(model_path).name
    time_start = time.time()
    print("Running Query...")
    output = model({'query': question})
    response = output["result"]
    time_elapsed = time.time() - time_start
    print("Response time: ", time_elapsed)
    print("Question: ", question)
    print("Answer: ", response[0])


result = query(QA_LLM, "What is this all about?")