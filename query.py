from vgrep.db import DB
from settings import parse_settings
from vgrep.file_sync import FileSync
from chromadb import chromadb
from pathlib import Path
from typing import List

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
    
    for res in db.query(args.search):
        print(f'{res["filename"]}:{res["line_start"]}')
        print(f'{res["text"]}\n\n')
