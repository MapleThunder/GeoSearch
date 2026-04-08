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
    request_timeout=360.0
)

def query_documents(query_text: str) -> list[dict]:
    client = chromadb.PersistentClient(path="./storage")
    collection = client.get_or_create_collection(name="geodocs")
    # Run a similarity search against the collection
    embed_query = Settings.embed_model.get_text_embedding(query_text)
    results = collection.query(
        query_embeddings=[embed_query],
        n_results=5
    )

    # Build the RAG prompt, I will need:
    # Instructions: Directions for the llm on what role to take and what to do
    # Retrieved Context: The gathered context from chromadb
    # Question: The user question
    context = build_context(results) 
    prompt = f"""
        You are an expert geoscience analyst helping researchers find information across geological survey documents.

        Tone: Professional and precise. Avoid filler phrases like "certainly" or "great question".

        Grounding: Base your answer exclusively on the context provided below. Do not draw on outside knowledge.

        If the context does not contain enough information to answer, say exactly: "The provided documents 
        do not contain sufficient information to answer this question."

        Format your response as:
        - A direct answer in 2-3 sentences
        - A bullet list of supporting evidence drawn from the context
        - Any relevant mineral names, locations, or deposit classifications mentioned

        Context:
        {context}

        Question:
        {query_text}
    """
    # Step 3: Take the retrieved chunks and pass them + the original query to the LLM
    # This is the "augmented generation" part of RAG

    response = Settings.llm.complete(prompt)
    print(response)
    
    # Step 4: Return something structured enough for handle_search to display
    # Think about what handle_search will need: filename, snippet, relevance score

def build_context(context) -> str:
    constructed_context = ""
    documents = context["documents"][0]
    metadatas = context["metadatas"][0]

    for document, metadata in zip(documents, metadatas):
        constructed_context += f"""
            Source: {metadata["file_name"]}
            Content: {document}
            ---
        """

    return constructed_context

def build_sources(context) -> list:
    sources = []
    documents = context["documents"][0]
    metadatas = context["metadatas"][0]
    distances = context["distances"][0]

    for document, metadata, distance in zip(documents, metadatas, distances):
        sources.append({
            "file_name": metadata["file_name"],
            "distance": distance,
            "snippet": document[:250]
        })

    return sources