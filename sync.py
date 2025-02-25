from vgrep.db import DB
from vgrep.fs import FS
from settings import parse_settings
from chromadb import chromadb, Settings
from vgrep.file_sync import FileSync
from pathlib import Path
import pdb

settings = parse_settings('./settings.json')

# point to FS
fs = FS(settings['sync_dirs'].keys())

# set up DB
chroma_settings = chromadb.Settings(anonymized_telemetry=False)
client = chromadb.PersistentClient(path=settings['db_dir'],
                                   settings=chroma_settings)
collection = None
try: collection =  client.get_collection(name="main")
except chromadb.errors.InvalidCollectionException:
    collection = client.create_collection(name="main")
db = DB(collection)

# create the sync
fsync = FileSync(fs, db)
fsync.sync()
