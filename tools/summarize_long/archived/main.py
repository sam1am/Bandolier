# from tabnanny import verbose
import tiktoken
from langchain import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import PromptTemplate
import os
from dotenv import load_dotenv

file = "homer.txt"

with open(file, "r") as f:
    text = f.read()

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)

text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n"], chunk_size=7500, chunk_overlap=500
)

docs = text_splitter.create_documents([text])

num_docs = len(docs)

num_tokens_first_doc = llm.get_num_tokens(docs[0].page_content)
print(
    f"Now we have {num_docs} documents and the first one has {num_tokens_first_doc} tokens"
)

map_prompt = """
Write a detailed summary of the following:
"{text}"
CONCISE SUMMARY:
"""
map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])

combine_prompt = """
Write a detailed summary of the following text delimited by triple backquotes.
Return your response in bullet points which covers the key points of the text.
```{text}```
BULLET POINT SUMMARY:
"""
combine_prompt_template = PromptTemplate(
    template=combine_prompt, input_variables=["text"]
)


summary_chain = load_summarize_chain(
    llm=llm,
    chain_type="map_reduce",
    map_prompt=map_prompt_template,
    combine_prompt=combine_prompt_template,
)


output = summary_chain.run(docs)

print(output)
