# ── MILESTONE 1: Ingest PDFs into ChromaDB and run a test query ──────────────

# 1. IMPORTS
# import chromadb, llama_index SimpleDirectoryReader, VectorStoreIndex,
# ChromaVectorStore, StorageContext
import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

# 2. SET UP CHROMADB
# create a PersistentClient pointing at ./storage
# get_or_create_collection called "geodocs"
client = chromadb.PersistentClient(path="./storage")
collection = client.get_or_create_collection(name="geodocs")

# 3. SET UP THE VECTOR STORE
# wrap the chroma collection in a ChromaVectorStore
# create a StorageContext from the vector store


# 4. LOAD AND PARSE THE PDFs
# use SimpleDirectoryReader to load all files from ./data
# this handles PDF text extraction automatically


# 5. BUILD THE INDEX
# create a VectorStoreIndex from the loaded documents
# pass in the storage_context so it writes to ChromaDB instead of memory


# 6. CREATE A QUERY ENGINE
# call .as_query_engine() on the index


# 7. RUN A TEST QUERY
# hardcode a question relevant to your PDFs e.g. "what files mention copper deposits"
# pass it to query_engine.query()
# print the response