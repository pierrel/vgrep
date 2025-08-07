from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from vgrep.manager import Manager


class DummyEmbeddingFunction:
    def __call__(self, input):
        return [[0.0] for _ in input]

    @staticmethod
    def name() -> str:
        return "default"

    def get_config(self):
        return {}


class TestManager(TestCase):
    def setUp(self):
        self.dir = TemporaryDirectory()
        self.db_dir = Path(self.dir.name) / "db"

    def tearDown(self):
        self.dir.cleanup()

    def test_sync_and_query(self):
        file = Path(self.dir.name) / "test.txt"
        file.write_text("hello world")
        m = Manager(
            Path(self.dir.name),
            db_path=self.db_dir,
            embedding=DummyEmbeddingFunction(),
        )
        m.sync()
        results = m.query("hello")
        self.assertTrue(any("hello" in r["text"] for r in results))

    def test_match_function(self):
        keep = Path(self.dir.name) / "keep.txt"
        skip = Path(self.dir.name) / "skip.md"
        keep.write_text("hello")
        skip.write_text("world")

        def matcher(p: Path) -> bool:
            return p.suffix == ".txt"

        m = Manager(
            Path(self.dir.name),
            file_match=matcher,
            db_path=self.db_dir,
            embedding=DummyEmbeddingFunction(),
        )
        m.sync()
        files = m.db.all_files()
        self.assertIn(keep, files)
        self.assertNotIn(skip, files)

    def test_default_db_path_deterministic(self):
        m1 = Manager(
            Path(self.dir.name),
            file_match=lambda p: p.suffix == ".txt",
            embedding=DummyEmbeddingFunction(),
        )
        m2 = Manager(
            Path(self.dir.name),
            file_match=lambda p: p.suffix == ".txt",
            embedding=DummyEmbeddingFunction(),
        )
        self.assertEqual(m1.db_path, m2.db_path)
