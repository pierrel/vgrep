from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from typing import Generator
from pathlib import Path
from hashlib import md5
import pdb


class TextChunkMetadata(BaseModel):
    line_start: int
    id: str


class TextChunkWithMetadata(BaseModel):
    chunk: str
    metadata: TextChunkMetadata


class FileInterpreter:
    """Understands how to split files into text and associate the
    correct metadata.

    """

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True)

    def file_chunks(self,
                    p: Path) -> Generator[TextChunkWithMetadata]:
        line_number = 0  # This has a bug in that it double-counts
        # newlines that are at the overlap of
        # chunks. Also it should probably be split
        # into its own function.
        with open(p) as f:
            split_text = self.text_splitter.split_text(f.read())
            for idx, chunk in enumerate(split_text):
                id = chunk_id(chunk, p, idx)
                chunk_meta = TextChunkMetadata(line_start=line_number,
                                               id=id)
                yield TextChunkWithMetadata(chunk=chunk,
                                            metadata=chunk_meta)
                line_number += chunk.count("\n")


def chunk_id(s: str, path: Path, idx: int) -> str:
    together = s + path.as_posix()
    return f'{md5(together.encode()).hexdigest()}:{idx}'
