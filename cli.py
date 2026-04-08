# --- Imports ---
import argparse
from pipelines.ingest import ingest_pipeline
from search.query import query_documents

def handle_search(args) -> str:
    response = query_documents(query_text=args.query)
    # Step 2: format and display results using rich

def handle_ingest(args):
    print("Starting Prefect ingest flow...")
    # ingest_pipeline(args.data_dir)
    print("Finished Prefect ingest flow !")

def main():
    # print("Initializing parsers...")

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
    
    # print("Parsers initialized !")
    # print("Reading args...")
    
    # I know I need to pass the content from the script call into parse_args but am not sure how yet
    args = parser.parse_args()
    args.func(args)


# --- Entry point ---
if __name__ == "__main__":
    main()
