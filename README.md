# Strata

> A terminal-first RAG pipeline that ingests a directory of geological PDF documents, builds a local vector index via ChromaDB and LlamaIndex, and lets you query them in natural language from the CLI — orchestrated end to end with Prefect.

---

## Overview

Strata is a local-first document intelligence tool built for querying large collections of unstructured geological reports and scientific documents using natural language. Point it at a directory of PDFs, run the ingest pipeline, and ask questions directly from your terminal — no cloud required.

Built as a portfolio project to explore RAG pipeline architecture, vector search, and terminal-first UX design.

---

## Features

- **Natural language search** over local PDF collections via CLI
- **Prefect-orchestrated ingest pipeline** with observable task runs and logging
- **Fully local** — embeddings and inference run on your machine via Ollama, no API key required
- **ChromaDB vector store** with persistent local storage across sessions
- **Rich terminal output** — results displayed as a formatted panel and source table with filename, similarity distance, and content snippet

---

## Tech Stack

| Layer                       | Technology                  |
| --------------------------- | --------------------------- |
| Pipeline orchestration      | Prefect                     |
| Document loading & chunking | LlamaIndex                  |
| Vector store                | ChromaDB                    |
| Embeddings                  | Ollama (`nomic-embed-text`) |
| Local LLM inference         | Ollama (`llama3.1:8b`)      |
| Terminal UI                 | Rich                        |
| Language                    | Python 3.12+                |

---

## Getting Started

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com/download) installed and running locally

### Installation

```bash
# Clone the repository
git clone git@github.com:MapleThunder/Strata.git
cd Strata

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Pull the required Ollama models
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

### Project Structure

```
Strata/
├── data/                    # Drop your PDF documents here
├── storage/                 # ChromaDB persists its index here
├── pipelines/
│   ├── ingest.py            # Prefect flow — loading, chunking, embedding, storing
│   └── usgs_ingest.py       # USGS-specific ingest pipeline
├── search/
│   └── query.py             # Retrieval and answer generation logic
├── cli.py                   # Entry point for all CLI commands
├── mvp.py                   # MVP/prototype script
└── requirements.txt
```

---

## Usage

### Ingest documents

Drop your PDFs into the `/data` directory (or specify another), then run:

```bash
python cli.py ingest
# or using the alias:
python cli.py i

# Ingest from a custom directory
python cli.py ingest --data_dir ./path/to/pdfs/
```

This triggers the Prefect pipeline, which loads, chunks, embeds, and stores all PDFs in the local ChromaDB index. You can monitor pipeline runs in the Prefect UI by running `prefect server start` in a separate terminal.

### Query your documents

```bash
python cli.py search "what formations are associated with copper deposits"
# or using the alias:
python cli.py s "what formations are associated with copper deposits"
```

Results are returned as a natural language answer panel followed by a source table showing the source document, similarity distance, and a content snippet.

---

## Sample Dataset

This project was developed using open geological survey data from:

- [NRCan Open Geoscience](https://open.canada.ca/en/open-science/geoscience) — Natural Resources Canada
- [USGS Publications Warehouse](https://pubs.usgs.gov) — United States Geological Survey

Both sources are public domain and free to download. A collection of reports on lithium, copper, and critical minerals was used during development.

---

## Roadmap

- [ ] Watch mode — auto re-index when new files are added to `/data`
- [ ] Settings flags to allow users to change the models used
- [ ] Filter by file type, date, or keyword before querying
- [ ] Support for additional file types (DOCX, Markdown)

---

## License

MIT
