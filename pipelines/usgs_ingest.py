"""
usgs_ingest.py

Downloads PDFs from the USGS Publications Warehouse API.
Targets Canada-focused mineral and geology reports for use as a RAG dataset.

Usage:
    python usgs_ingest.py                         # default: canada minerals
    python usgs_ingest.py --query "copper canada" --max 20
    python usgs_ingest.py --query "lithium deposits canada" --output ./data --max 30

Requirements:
    pip install requests rich
"""

import argparse
import time
import re
import sys
from pathlib import Path

import requests
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich import print as rprint

# ── Constants ────────────────────────────────────────────────────────────────

API_BASE     = "https://pubs.usgs.gov/pubs-services/publication"
PAGE_SIZE    = 100          # max recommended by USGS docs
DELAY        = 0.5          # seconds between PDF downloads — be a polite scraper
TIMEOUT      = 30           # seconds per request
MAX_RETRIES  = 3

console = Console()


# ── API Helpers ───────────────────────────────────────────────────────────────

def fetch_page(query: str, page_number: int) -> dict:
    """Hit the USGS pubs API and return parsed JSON for one page of results."""
    params = {
        "q":           query,
        "page_size":   PAGE_SIZE,
        "page_number": page_number,
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(API_BASE, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            if attempt == MAX_RETRIES:
                console.print(f"[red]API request failed after {MAX_RETRIES} attempts: {exc}[/red]")
                sys.exit(1)
            console.print(f"[yellow]Attempt {attempt} failed, retrying…[/yellow]")
            time.sleep(2 ** attempt)


def extract_pdf_url(record: dict) -> str | None:
    """
    Pull the first PDF link from a publication record.
    The API returns a `links` list; we want entries where the URL ends in .pdf
    or the link type is 'Document'.
    """
    for link in record.get("links", []):
        url = link.get("url", "")
        if url.lower().endswith(".pdf"):
            return url
        if link.get("type", {}).get("text") == "Document" and url:
            return url
    return None


def collect_records(query: str, max_results: int) -> list[dict]:
    """
    Page through the API until we have `max_results` records (or exhaust results).
    Returns only records that have a downloadable PDF.
    """
    collected = []
    page = 1
    total_available = None

    with console.status(f"[bold cyan]Searching USGS for: '{query}'…") as status:
        while len(collected) < max_results:
            data = fetch_page(query, page)

            if total_available is None:
                total_available = data.get("recordCount", 0)
                console.print(
                    f"[green]Found {total_available} total records.[/green] "
                    f"Scanning for PDFs…"
                )

            records = data.get("records", [])
            if not records:
                break

            for rec in records:
                pdf_url = extract_pdf_url(rec)
                if pdf_url:
                    collected.append({
                        "title":  rec.get("title", "Untitled"),
                        "year":   rec.get("publicationYear", "n/a"),
                        "series": rec.get("seriesTitle", {}).get("text", ""),
                        "doi":    rec.get("doi", ""),
                        "url":    pdf_url,
                    })
                    if len(collected) >= max_results:
                        break

            # Stop if we've paged through everything
            row_start = int(data.get("pageRowStart", 0))
            if row_start + len(records) >= total_available:
                break

            page += 1
            status.update(f"[bold cyan]Page {page} — {len(collected)} PDFs found so far…")

    return collected


# ── Download ──────────────────────────────────────────────────────────────────

def sanitize_filename(title: str, year: str, url: str) -> str:
    """Turn a publication title into a safe filename, falling back to the URL slug."""
    if title and title != "Untitled":
        slug = re.sub(r"[^\w\s-]", "", title).strip()
        slug = re.sub(r"[\s]+", "_", slug)[:80]
        return f"{year}_{slug}.pdf"
    # fall back to the last segment of the URL
    return url.split("/")[-1] or "unknown.pdf"


def download_pdf(url: str, dest: Path) -> bool:
    """Download a single PDF to `dest`. Returns True on success."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, timeout=TIMEOUT, stream=True)
            resp.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except requests.RequestException as exc:
            if attempt == MAX_RETRIES:
                console.print(f"  [red]✗ Failed: {exc}[/red]")
                return False
            time.sleep(2 ** attempt)
    return False


def download_all(records: list[dict], output_dir: Path) -> tuple[int, int]:
    """
    Download all PDFs in `records` to `output_dir`.
    Returns (success_count, skip_count).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    success = skip = fail = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Downloading PDFs…", total=len(records))

        for rec in records:
            filename = sanitize_filename(rec["title"], rec["year"], rec["url"])
            dest = output_dir / filename

            if dest.exists():
                progress.console.print(f"  [dim]↷ Skipped (exists): {filename}[/dim]")
                skip += 1
            else:
                progress.console.print(f"  [cyan]↓[/cyan] {filename[:70]}…")
                ok = download_pdf(rec["url"], dest)
                if ok:
                    success += 1
                else:
                    fail += 1

            progress.advance(task)
            time.sleep(DELAY)

    return success, skip, fail


# ── Summary Table ─────────────────────────────────────────────────────────────

def print_summary(records: list[dict], success: int, skip: int, fail: int, output_dir: Path):
    table = Table(title="Downloaded Publications", show_lines=True)
    table.add_column("Year", style="dim", width=6)
    table.add_column("Series", style="cyan", width=20)
    table.add_column("Title", width=55)

    for rec in records:
        table.add_row(rec["year"], rec["series"], rec["title"][:80])

    console.print()
    console.print(table)
    console.print()
    console.print(
        f"[bold green]✓ {success} downloaded[/bold green]  "
        f"[dim]{skip} skipped (already existed)[/dim]  "
        f"[red]{fail} failed[/red]"
    )
    console.print(f"[bold]Output directory:[/bold] {output_dir.resolve()}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Bulk-download USGS geology PDFs for use as a RAG dataset."
    )
    parser.add_argument(
        "--query", "-q",
        default="canada minerals geology",
        help="Search query for the USGS Publications Warehouse (default: 'canada minerals geology')"
    )
    parser.add_argument(
        "--max", "-m",
        type=int,
        default=15,
        help="Maximum number of PDFs to download (default: 15)"
    )
    parser.add_argument(
        "--output", "-o",
        default="./data",
        help="Directory to save PDFs into (default: ./data)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output)

    console.rule("[bold blue]USGS Geology PDF Ingestion")
    console.print(f"  Query   : [cyan]{args.query}[/cyan]")
    console.print(f"  Max PDFs: [cyan]{args.max}[/cyan]")
    console.print(f"  Output  : [cyan]{output_dir}[/cyan]")
    console.print()

    # 1. Collect records from the API
    records = collect_records(args.query, args.max)

    if not records:
        console.print("[red]No downloadable PDFs found for that query. Try a broader search term.[/red]")
        sys.exit(0)

    console.print(f"\n[green]{len(records)} PDFs ready to download.[/green]\n")

    # 2. Download
    success, skip, fail = download_all(records, output_dir)

    # 3. Summary
    print_summary(records, success, skip, fail, output_dir)


if __name__ == "__main__":
    main()