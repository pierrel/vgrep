"""Command line interface for vgrep.

This module exposes a ``main`` function so it can be used as an entry point
when the project is installed as a package.  The previous implementation kept
most of the logic at module import time, which made reuse difficult.  The
logic has been wrapped in ``main`` so tools like ``setuptools`` can create a
``console_script`` entry point.
"""

from pathlib import Path
from typing import List

from chromadb import chromadb

from vgrep.db import DB, QueryResult
from vgrep.file_sync import FileSync
from vgrep.fs import FS
from settings import parse_settings


def org_format_result(result: QueryResult) -> str:
    name_link = f"[[{result['filename']}::{result['line_start']}][{result['filename']}]]"
    body = f"#+begin_quote\n{result['text']}\n#+end_quote"
    
    return f"{name_link}\n{body}"
    
def org_format_results(results: List[QueryResult]) -> str:
    return "\n\n".join(map(org_format_result, results))


def main() -> None:
    """Entry point for the ``vgrep`` command line tool."""
    settings = parse_settings("./settings.json")

    # set up DB
    chroma_settings = chromadb.Settings(anonymized_telemetry=False)
    client = chromadb.PersistentClient(
        path=settings["db_dir"], settings=chroma_settings
    )
    try:
        collection = client.get_collection(name="main")
    except chromadb.errors.InvalidCollectionException:
        collection = client.create_collection(name="main")
    db = DB(collection)

    paths = map(Path, settings["sync_dirs"].keys())
    fs = FS(paths)
    fsync = FileSync(fs, db)

    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        help="The search string to use for the query",
    )
    parser.add_argument(
        "-s",
        "--sync",
        action="store_true",
        help="Switch to sync the vector db with the file system",
    )
    args = parser.parse_args()

    if args.sync:
        print("Syncing...")
        fsync.sync()
        print("Done.")

    if args.query:
        print(f"Results for '{args.query}'")
        print(org_format_results(db.query(args.query)))

    if not args.query and not args.sync:
        parser.print_help(sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
