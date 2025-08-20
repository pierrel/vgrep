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

    def test_file_with_non_utf8_bytes_is_handled(self):
        fi = FileInterpreter()

        # Create content that is not valid UTF-8 by including a lone 0xA1 byte
        # followed by ASCII text. Reading this file using the default encoding
        # previously raised ``UnicodeDecodeError``.
        data = b"First line\n" + b"\xA1Hola!\n"

        with NamedTemporaryFile("wb") as f:
            f.write(data)
            f.flush()

            chunks = list(fi.file_chunks(Path(f.name)))

        # We should still get chunks and the non-UTF-8 byte should be skipped
        self.assertGreater(len(chunks), 0)
        self.assertIn("Hola", chunks[0].chunk)

