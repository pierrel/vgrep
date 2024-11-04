import chromadb
from typing import List, Dict, Iterable
from hashlib import md5
from pathlib import Path
from itertools import repeat, accumulate
from functools import reduce
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdb

class DB:
    '''Handle interactions like updates and queries to the vector DB'''
    def __init__(self, collection: chromadb.Collection):
        self.collection = collection
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True)
    
    def add(self, p:Path):
        print(f'Adding {p}')
        with open(p) as f:
            split_text = self.text_splitter.split_text(f.read())
            if len(split_text) > 0:
                ids = [self.to_id(x, p, idx) for idx, x in enumerate(split_text)]
                lines = self.to_lines(split_text)
                meta_base = {'filename': p.as_posix(),
                             'last_modified': p.stat().st_mtime}
                metadatas = list(map(lambda x: {**meta_base, 'line_start': x},
                                     lines))
                self.collection.add(documents=split_text,
                                    ids=ids,
                                    metadatas=metadatas)
            else:
                print(f'Skipping {p}')

    def remove(self, p:Path):
        print(f'Removing {p}')
        self.collection.delete(where={"filename": p.as_posix()})

    def update(self, p:Path):
        self.remove(p)
        self.add(p)

    def query(self, s: str) -> List[Dict]:
        res = self.collection.query(query_texts=[s],
                                    n_results=100)
        docs = res['documents'][0]
        filenames = map(lambda x: x['filename'],
                        res['metadatas'][0])
        return list(map(lambda x: {'text': x[0],
                                   'filename': Path(x[1])},
                        zip(docs, filenames)))

    def last_modified(self, p: Path):
        filename = p.as_posix()
        res = self.collection.get(where={'filename': filename})
        return min(map(lambda x: x['last_modified'],
                       res['metadatas']))

    def all_files(self) -> Dict[Path, float]:
        '''Returns a dict of Path -> modified_time'''
        return reduce(self.__metadata_reducer__,
                      self.__iterate_files__(),
                      {})

    @classmethod
    def to_lines(cls, text: List[str]) -> List[int]:
        '''Returns the line number of the first line in the text elements'''
        return [0] + list(accumulate(map(lambda x: x.count("\n"),
                                         text)))[:-1]
    
    @classmethod
    def __metadata_reducer__(
            cls,
            acc: Dict[Path, float],
            cur: tuple[str, float]) -> Dict[Path,float]:
        cur_modified = cur[1]
        cur_file = Path(cur[0])
        acc_modified = acc.get(cur_file)
        if not acc_modified or acc_modified > cur_modified:
            acc[cur_file] = cur_modified
        
        return acc

    def __iterate_files__(self, batch_size=10) -> Iterable[tuple[str, float]]:
        total = self.collection.count()
        for i in range(0, total, batch_size):
            batch = self.collection.get(include=["metadatas"],
                                        limit=batch_size,
                                        offset=i)
            for meta in batch["metadatas"]:
                yield (meta["filename"],
                       meta["last_modified"])
    
    @classmethod
    def to_id(cls, s: str, path: Path, idx: int) -> str:
        together = s + path.as_posix()
        return f'{md5(together.encode()).hexdigest()}:{idx}'


