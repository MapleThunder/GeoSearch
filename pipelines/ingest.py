# --- Imports ---
import chromadb
from prefect import flow, task
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import re

# --- Initialization ---
Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434",
    embed_batch_size=1
)
Settings.llm = Ollama(
    model="llama3.1:8b",
    request_timeout=60.0
)
client = chromadb.PersistentClient(path="./storage")
collection = client.get_or_create_collection(name="geodocs")


# --- Tasks ---
@task
def load_documents(path: str) -> list[Document]:
    # Load only PDFs
    required_exts = [".pdf"]

    reader = SimpleDirectoryReader(
        input_dir=path,
        required_exts=required_exts
    )
    documents = reader.load_data()
    
    return documents

@task
def chunk_documents(documents: list[Document]) -> list[TextNode]:
    for document in documents:
        # Some documents have tables with formatting that show up as long strings of "."
        # This pushes those chunks above the context window maximum and fails the flow
        # This removes only strings of "." 3 or longer
        document.set_content(re.sub(r'\.{3,}', ' ', document.text))

    splitter = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=100
    )
    nodes = splitter.get_nodes_from_documents(documents)
    nodes = [node for node in nodes if node.text] # Remove empty nodes
    
    return nodes

@task
def embed_and_store(nodes: list[TextNode]):
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex(
        nodes,
        storage_context=storage_context
    )

# --- Flow ---
@flow
def ingest_pipeline(data_dir: str):
    documents = load_documents(data_dir)
    chunks = chunk_documents(documents)
    embed_and_store(chunks)

# --- Entry point ---
if __name__ == "__main__":
    ingest_pipeline("./data/")