# --- Imports ---
import argparse
from pipelines.ingest import ingest_pipeline
from search.query import query_documents
from rich import print, box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from operator import itemgetter

def handle_search(args) -> str:
    response = query_documents(query_text=args.query)
    # Query
    label = Text.assemble(
        ("Query: ", "bold pink1"),
        (args.query, "yellow"),
        justify="center"
    )
    print(label)

    # Answer panel
    panel = Panel(
        Markdown(response["answer"]),
        title="GeoSearch Response",
        border_style="green",
    )
    print(panel)

    # Source table
    table = Table(title="Sources", show_lines=True, box=box.ROUNDED)
    table.add_column("File", style="cyan", header_style="pink1")
    table.add_column("Distance", justify="right", header_style="pink1", style="deep_sky_blue2")
    table.add_column("Snippet", header_style="pink1")

    for source in sources:
        table.add_row(
            source["file_name"],
            str(round(source["distance"], 4)),
            source["snippet"]
        )

    print(table)

def handle_ingest(args):
    print("Starting Prefect ingest flow...")
    ingest_pipeline(args.data_dir)
    print("Finished Prefect ingest flow !")

def main():
    parser = argparse.ArgumentParser(
        prog='GeoSearch',
        description='GeoSearch allows ingestion and RAG query of PDF documents locally on device',
    )
    parser.set_defaults(func=lambda args: parser.print_help())
    # Create the subparsers for the different commands, ingest & search
    subparsers = parser.add_subparsers()
    parser_ingest = subparsers.add_parser(
        "ingest",
        aliases=["i"],
        help="Runs the Prefect ingest flow on all PDF documents in the provided directory"
    )
    parser_ingest.add_argument(
        "--data_dir",
        type=str,
        default="./data/",
        help="The directory where the PDFs for ingest are located"
    )
    parser_ingest.set_defaults(func=handle_ingest)

    parser_search = subparsers.add_parser(
        "search",
        aliases=["s"],
        help="Uses a local llm to query the ingested documents"
    )
    parser_search.add_argument(
        'query',
        type=str,
        help="A natural language query to send to the llm"
    )
    parser_search.set_defaults(func=handle_search)
    
    args = parser.parse_args()
    args.func(args)


# --- Entry point ---
if __name__ == "__main__":
    main()
