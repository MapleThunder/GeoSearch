# ── MILESTONE 1: Ingest PDFs into ChromaDB and run a test query ──────────────

# 1. IMPORTS
# import chromadb, llama_index SimpleDirectoryReader, VectorStoreIndex,
# ChromaVectorStore, StorageContext
import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import logging
import sys

# CONFIGURE MODELS
# Instantiate the LLM and embed models
# Add the models to the Settings object
Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434"
)
Settings.llm = Ollama(
    model="llama3.1:8b",
    request_timeout=60.0
)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# 2. SET UP CHROMADB
# create a PersistentClient pointing at ./storage
# get_or_create_collection called "geodocs"
client = chromadb.PersistentClient(path="./storage")
collection = client.get_or_create_collection(name="geodocs")

# 3. SET UP THE VECTOR STORE
# wrap the chroma collection in a ChromaVectorStore
# create a StorageContext from the vector store
vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 4. LOAD AND PARSE THE PDFs
# use SimpleDirectoryReader to load all files from ./data
# this handles PDF text extraction automatically
documents = SimpleDirectoryReader("./data/").load_data()


# 5. BUILD THE INDEX
# create a VectorStoreIndex from the loaded documents
# pass in the storage_context so it writes to ChromaDB instead of memory
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context
)
# index = VectorStoreIndex.from_vector_store(
#     vector_store=vector_store
# )

# 6. CREATE A QUERY ENGINE
# call .as_query_engine() on the index
query_engine = index.as_query_engine()


# 7. RUN A TEST QUERY
# hardcode a question relevant to your PDFs e.g. "what files mention copper deposits"
# pass it to query_engine.query()
# print the response
question = "Which documents mention minerals and what are they ?"

response = query_engine.query(question)

print(response)