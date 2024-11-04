from vgrep.db import DB
from vgrep.fs import FS
from chromadb import chromadb
from vgrep.file_sync import FileSync
from pathlib import Path
import pdb

# point to FS
fs = FS([Path('/home/pierre/Documents')])

# set up DB
client = chromadb.PersistentClient(path="./db")
collection = None
try: collection =  client.get_collection(name="main")
except chromadb.errors.InvalidCollectionException:
    collection = client.create_collection(name="main")
db = DB(collection)

# create the sync
fsync = FileSync(fs, db)
fsync.sync()
