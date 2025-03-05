from vgrep.db import DB, QueryResult
from settings import parse_settings
from vgrep.file_sync import FileSync
from chromadb import chromadb
from pathlib import Path
from typing import List


def org_format_result(result: QueryResult) -> str:
    name_link = f"[[{result['filename']}::{result['line_start']}][{result['filename']}]]"
    body = f"#+begin_quote\n{result['text']}\n#+end_quote"
    
    return f"{name_link}\n{body}"
    
def org_format_results(results: List[QueryResult]) -> str:
    return "\n\n".join(map(org_format_result, results))

settings = parse_settings('./settings.json')

# set up DB
chroma_settings = chromadb.Settings(anonymized_telemetry=False)
client = chromadb.PersistentClient(path=settings['db_dir'],
                                   settings=chroma_settings)
collection = None
try:
    collection = client.get_collection(name="main")
except chromadb.errors.InvalidCollectionException:
    collection = client.create_collection(name="main")
db = DB(collection)

if __name__ == "__main__":
    import argparse
    # get the search string
    parser = argparse.ArgumentParser()
    parser.add_argument("search",
                        help="The search string to use for the query")
    args = parser.parse_args()

    print(org_format_results(db.query(args.search)))
