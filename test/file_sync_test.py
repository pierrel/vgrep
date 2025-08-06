from unittest import TestCase
from tempfile import TemporaryDirectory
from pathlib import Path
import time

from chromadb import chromadb

from vgrep.db import DB
from vgrep.file_sync import FileSync
from vgrep.fs import FS


class DummyEmbeddingFunction:
    def __call__(self, input):
        return [[0.0] for _ in input]

    @staticmethod
    def name() -> str:
        return "default"

    def get_config(self):
        return {}


class TestFileSync(TestCase):
    def setUp(self):
        self.dir = TemporaryDirectory()
        self.db_dir = TemporaryDirectory()
        chroma_settings = chromadb.Settings(anonymized_telemetry=False)
        client = chromadb.PersistentClient(
            path=self.db_dir.name, settings=chroma_settings
        )
        collection = client.get_or_create_collection(
            name="main", embedding_function=DummyEmbeddingFunction()
        )
        self.db = DB(collection)
        self.fs = FS([Path(self.dir.name)])
        self.sync = FileSync(self.fs, self.db)

    def tearDown(self):
        self.dir.cleanup()
        self.db_dir.cleanup()

    def test_sync_add_update_remove(self):
        file = Path(self.dir.name) / "test.org"
        file.write_text("hello")

        # Add
        self.sync.sync()
        files = self.db.all_files()
        self.assertIn(file, files)
        first_mtime = files[file]

        # Query
        results = self.db.query("hello")
        self.assertEqual(results[0]["filename"], file)
        self.assertIn("hello", results[0]["text"])

        # Update
        time.sleep(1)
        file.write_text("hello again")
        self.sync.sync()
        files = self.db.all_files()
        self.assertGreater(files[file], first_mtime)

        # Remove
        file.unlink()
        self.sync.sync()
        self.assertNotIn(file, self.db.all_files())
