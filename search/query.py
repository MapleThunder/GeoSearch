import chromadb
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from typing import TypedDict

Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434"
)
Settings.llm = Ollama(
    model="llama3.1:8b",
    request_timeout=360.0
)

class QueryResult(TypedDict):
    answer: str
    sources: list[dict]

def query_documents(query_text: str) -> QueryResult:
    """Embed a query string, retrieve the top 5 similar documents from ChromaDB, build a grounded RAG prompt, and return the LLM's answer alongside a list of source metadata dicts."""

    client = chromadb.PersistentClient(path="./storage")
    collection = client.get_or_create_collection(name="geodocs")
    # Run a similarity search against the collection
    embed_query = Settings.embed_model.get_text_embedding(query_text)
    results = collection.query(
        query_embeddings=[embed_query],
        n_results=5
    )

    """
        Build the RAG prompt, I will need:
        Instructions: Directions for the llm on what role to take and what to do
        Retrieved Context: The gathered context from chromadb
        Question: The user question
    """
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

    response = Settings.llm.complete(prompt)
    sources = build_sources(results)

    return {
        "answer": response.text,
        "sources": sources
    }

def build_context(context) -> str:
    """Format ChromaDB query results into a plaintext context block, with each entry showing its source filename and document content separated by dividers."""

    constructed_context = ""
    documents = context["documents"][0]
    metadata_arr = context["metadatas"][0]

    for document, metadata in zip(documents, metadata_arr):
        constructed_context += f"""
            Source: {metadata["file_name"]}
            Content: {document}
            ---
        """

    return constructed_context

def build_sources(context) -> list:
    """Extract and return a list of source dicts from ChromaDB query results, each containing the filename, similarity distance, and a 250-character content snippet."""

    sources = []
    documents = context["documents"][0]
    metadata_arr = context["metadatas"][0]
    distances = context["distances"][0]

    for document, metadata, distance in zip(documents, metadata_arr, distances):
        sources.append({
            "file_name": metadata["file_name"],
            "distance": distance,
            "snippet": document[:250]
        })

    return sources