import pandas as pd
import os
import lancedb
from torch import cuda
import urllib.request

from langchain.retrievers import EnsembleRetriever
from langchain.schema import Document
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain_community.vectorstores.lancedb import LanceDB
from langchain_community.retrievers import BM25Retriever
from langchain_community.llms.llamacpp import LlamaCpp

from langchain_core.documents.base import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnablePick
from langchain_core.prompts import ChatPromptTemplate


### Settings to run solution

path_to_data_csv = 'data.csv'

path_to_database = 'db'

embedding_model = 'sentence-transformers/all-MiniLM-L6-v2'

HF_AUTH = os.getenv('HF_AUTH', None)
os.environ['HF_HOME'] = os.getenv('HF_HOME', 'models')
model_id='llama-2-7b-chat.Q2_K.gguf'

chunk_size = 400
chunk_overlap = 50

retrieve_top_k_docs_bm25 = 1
retrieve_top_k_docs_vector = 1
context_length_for_llm = chunk_size*(retrieve_top_k_docs_bm25 + retrieve_top_k_docs_vector)+200 #not larger than 2048
retrievers_weights_bm25 = 0.4 #probability
llama_temperature = 0.75 #randomness parameter

### Load the data into type Document

df = pd.read_csv(path_to_data_csv)

documents=[]
for index, row in df.iterrows():
    doc = Document(page_content = row['chunk'],
                   metadata={'id': row['id'], 'title': row['title'], 'authors': row['authors'], 'sources': row['sources']})
    documents.append(doc)

print(f'---\n--- Read {len(documents)} documents from {path_to_data_csv}')

### Create retrievers

print(f'---\n--- Creating retrievers...')

bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k =  retrieve_top_k_docs_bm25

device = 'cuda' if cuda.is_available() else 'cpu'

# Create embedding
embed_model = HuggingFaceEmbeddings(
    model_name=embedding_model,
    model_kwargs={'device': device},
    encode_kwargs={'device': device, 'batch_size': 32}
)

# Try if the LanceDB exists, if yes, use if, if no, create new one
try:
    print("--- Trying to connect to LanceDB")
    db = lancedb.connect(path_to_database)
    table = db.open_table("chatmaja_test")
    docsearch = LanceDB(connection=table, embedding=embed_model)
    print("--- LanceDB found, connected successfully")
except:
    print("--- Error connecting to LanceDB, creating new one")
    db = lancedb.connect(path_to_database)
    table = db.create_table("chatmaja_test", data=[
            {"vector": embed_model.embed_query("Hello World"), "text": "Hello World", "id": "1", "authors": "authoors", "sources": "sourcees", "title": "tiitle"}
        ], mode="overwrite")
    print("--- LanceDB created and connected successfully")
    table.delete('authors = "authoors"')
    docsearch = LanceDB.from_documents(documents, embed_model, connection=table)
    print("--- Finished loading documents to LanceDB")

retriever_lancedb = docsearch.as_retriever(search_kwargs={"k": retrieve_top_k_docs_vector})

# Create ensemble retriver
ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, retriever_lancedb],
                                       weights=[retrievers_weights_bm25, 1-retrievers_weights_bm25])

print("---\n--- Created BM25 and vector search retrievers")

### Get model

# Create directory if it does not exist
os.makedirs(os.getenv('HF_HOME'), exist_ok=True)

# Download model if not exists
path_to_model = os.path.join(os.getenv('HF_HOME'), model_id)
link_to_model = f"https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/{model_id}"

if not os.path.isfile(path_to_model):
    print(f"--- Downloading {model_id}...")
    urllib.request.urlretrieve(link_to_model, path_to_model)
    print(f"--- Downloaded {model_id} successfully.")
else:
    print(f"--- Model {model_id} already downloaded.")


# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Make sure the model path is correct for your system!
n_gpu_layers = -1 if device == 'cuda' else 0
llm = LlamaCpp(
    model_path=path_to_model,
    temperature=llama_temperature,
    max_tokens=min(context_length_for_llm*2, 4096),
    n_gpu_layers=n_gpu_layers,
    n_ctx=min(context_length_for_llm, 2048),
    top_p=1,
    callback_manager=callback_manager,
    verbose=True,  # Verbose is required to pass to the callback manager
)

### Create pipeline for the solution

def format_docs(docs):
  return "\n\n".join(doc.page_content for doc in docs)

# Prompt
rag_prompt_llama = ChatPromptTemplate.from_messages([
    ("human", """[INST]<<SYS>> You are an assistant for ques
     tion-answering tasks.
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, just say that you don't know.
    Use three sentences maximum and keep the answer concise.<</SYS>> \nQuestion: {question} \nContext: {context} \nAnswer: [/INST]"""),
])

# Chain
chain = (
    RunnablePassthrough.assign(context=RunnablePick("context") | format_docs)
    | rag_prompt_llama
    | llm
    | StrOutputParser()
)

def answer_query(question):
    """
    Get answer for provided question.

    Args:
        question (str): question from the user.
    """
    docs = ensemble_retriever.get_relevant_documents(question)
    answer = chain.invoke({"context": docs, "question": question})
    sources = "Sources:\n - " + "\n - ".join([
        d.metadata['title'] + ", " + d.metadata['authors'] + ", " + d.metadata['sources']
        for d in docs])
    answer_with_sources = answer + '\n\n' + sources
    return answer_with_sources

def answer_query_streaming(message: str, history: list):
    """
    Get answer for provided question for streaming.

    Args:
        question (str): question from the user.
        history (list): list of pairs of strings.
    """

    docs = ensemble_retriever.get_relevant_documents(message)
    sources = "Sources:\n - " + "\n - ".join([
        d.metadata['title'] + ", " + d.metadata['authors'] + ", " + d.metadata['sources']
        for d in docs])

    printed_so_far = ''
    for chunk in chain.stream({"context": docs, "question": message}):
        printed_so_far += chunk
        yield printed_so_far

    answer_with_sources = printed_so_far + '\n\n' + sources
    yield answer_with_sources

### Sample usage
    
# query = "What is used in brain cancer imaging?"
# answer_with_sources = answer_query(query)

# print(f'- - - Answer with sources: {answer_with_sources}')