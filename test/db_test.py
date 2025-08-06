from vgrep.db import DB
from chromadb import chromadb
from unittest import TestCase
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

class TestDB(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = TemporaryDirectory()
        cls.db_dir = TemporaryDirectory()
        chroma_settings = chromadb.Settings(anonymized_telemetry=False)
        client = chromadb.PersistentClient(path=cls.db_dir.name,
                                           settings=chroma_settings)

        class DummyEmbeddingFunction:
            def __call__(self, input):
                return [[0.0] for _ in input]

            @staticmethod
            def name() -> str:
                return "default"

            def get_config(self):
                return {}

        collection = client.get_or_create_collection(
            name="main",
            embedding_function=DummyEmbeddingFunction(),
        )
        cls.collection = collection
        cls.db = DB(collection)

    def clear_db(self):
        self.collection.delete()

    def test_files_added(self):
        org_file = NamedTemporaryFile(dir=self.dir.name,
                                      suffix=".org")
        org_file.write(b"Hello there!")
        org_file.truncate()
        self.db.add(Path(org_file.name))
        files = self.db.all_files()
        self.assertEqual(len(files),
                         1,
                         "Should have 1 file in the DB")
        
