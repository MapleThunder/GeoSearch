# 🪨 GeoSearch

> A terminal-first RAG pipeline that ingests a directory of unstructured geological documents, builds a local vector index via ChromaDB and LlamaIndex, and lets you query them in natural language from the CLI — orchestrated end to end with Prefect.

---

## Overview

GeoSearch is a local-first document intelligence tool built for querying large collections of unstructured geological reports and scientific documents using natural language. Point it at a directory of PDFs, run the ingest pipeline, and ask questions directly from your terminal — no cloud required.

Built as a portfolio project to explore RAG pipeline architecture, vector search, and terminal-first UX design.

---

## Features

- **Natural language search** over local document collections via CLI
- **Prefect-orchestrated ingest pipeline** with observable task runs and logging
- **Fully local** — embeddings and inference run on your machine via Ollama, no OpenAI API key required
- **ChromaDB vector store** with persistent local storage across sessions
- **Rich terminal output** — results displayed as formatted tables with filename, relevance score, and content snippet
- Supports PDF, plain text, and CSV documents

---

## Tech Stack

| Layer | Technology |
|---|---|
| Pipeline orchestration | Prefect |
| Document loading & chunking | LlamaIndex |
| Vector store | ChromaDB |
| Local LLM inference | Ollama (`mistral` or `llama3.2`) |
| Terminal UI | Rich |
| Language | Python 3.11+ |

---

## Getting Started

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com/download) installed and running locally

### Installation

```bash
# Clone the repository
git clone git@github.com:MapleThunder/GeoSearch.git
cd geosearch

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Pull a local model via Ollama
ollama pull mistral
```

### Project Structure

```
geosearch/
├── data/               # Drop your documents here
├── storage/            # ChromaDB persists its index here
├── pipelines/
│   └── ingest.py       # Prefect flow — chunking, embedding, storing
├── search/
│   └── query.py        # Retrieval and answer generation logic
├── cli.py              # Entry point for all CLI commands
└── requirements.txt
```

---

## Usage

### Ingest documents

Drop your PDFs or text files into the `/data` directory, then run:

```bash
python cli.py ingest
```

This triggers the Prefect pipeline, which loads, chunks, embeds, and stores all documents in the local ChromaDB index. You can monitor pipeline runs in the Prefect UI by running `prefect server start` in a separate terminal.

### Query your documents

```bash
python cli.py search "what formations are associated with copper deposits"
```

Results are returned as a formatted table in the terminal showing the source document, a relevance score, and a content snippet. A natural language summary is generated from the top retrieved chunks.

### Additional commands

```bash
# List all indexed documents
python cli.py list

# Clear the vector index and re-ingest
python cli.py ingest --reset
```

---

## Sample Dataset

This project was developed using open geological survey data from:

- [NRCan Open Geoscience](https://open.canada.ca/en/open-science/geoscience) — Natural Resources Canada
- [USGS Publications Warehouse](https://pubs.usgs.gov) — United States Geological Survey

Both sources are public domain and free to download. A collection of reports on lithium and copper deposits was used during development.

---

## Roadmap

- [ ] Watch mode — auto re-index when new files are added to `/data`
- [ ] `--summarize` flag to generate a digest across all indexed documents
- [ ] Filter by file type, date, or keyword before querying
- [ ] Support for additional file types (DOCX, Markdown)
- [ ] Optional OpenAI API backend for improved inference quality

---

## License

MIT
