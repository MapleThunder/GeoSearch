import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434"
)
Settings.llm = Ollama(
    model="llama3.1:8b",
    request_timeout=60.0
)

def query_documents(query_text: str) -> list[dict]:
    client = chromadb.PersistentClient(path="./storage")
    collection = client.get_or_create_collection(name="geodocs")
    # Run a similarity search against the collection
    results = collection.query(
        query_texts=[query_text],
        n_results=10
    )

    # Build the RAG prompt, I will need:
    # Instructions: 
    # Retrieved Context:
    # Question: The user question
    instruction = ""
    context = ""
    prompt = f"{instruction} {context} {query_text}"
    # Step 3: Take the retrieved chunks and pass them + the original query to the LLM
    # This is the "augmented generation" part of RAG
    Settings.llm.complete()
    
    # Step 4: Return something structured enough for handle_search to display
    # Think about what handle_search will need: filename, snippet, relevance score
    pass