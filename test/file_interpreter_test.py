from unittest import TestCase
from pathlib import Path
from tempfile import NamedTemporaryFile

from langchain_text_splitters import RecursiveCharacterTextSplitter

from vgrep.file_interpreter import FileInterpreter


class TestFileInterpreter(TestCase):
    def test_line_numbers_overlap_bug(self):
        fi = FileInterpreter()
        fi.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=30,
            chunk_overlap=15,
            add_start_index=True,
        )

        text = "".join(f"line{i}\n" for i in range(1, 11))

        with NamedTemporaryFile("w+") as f:
            f.write(text)
            f.flush()

            chunks = list(fi.file_chunks(Path(f.name)))

        line_starts = [c.metadata.line_start for c in chunks]

        # If overlap newlines were handled correctly we would get [0, 3, 6]
        self.assertEqual(line_starts, [0, 3, 6])

