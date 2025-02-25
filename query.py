import argparse
from vgrep.db import DB
from settings import parse_settings
from vgrep.file_sync import FileSync
from chromadb import chromadb
from pathlib import Path

settings = parse_settings('./settings.json')

# get the search string
parser = argparse.ArgumentParser()
parser.add_argument("search",
                    help="The search string to use for the query")
args = parser.parse_args()

# set up DB
settings = chromadb.Settings(anonymized_telemetry=False)
client = chromadb.PersistentClient(path=settings['db_dir'],
                                   settings=settings)
collection = None
try:
    collection =  client.get_collection(name="main")
except chromadb.errors.InvalidCollectionException:
    collection = client.create_collection(name="main")
db = DB(collection)

for res in db.query(args.search):
    print(f'{res["filename"]}:{res["line_start"]}')
    print(f'{res["text"]}\n\n')
