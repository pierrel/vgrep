import datetime
from pathlib import Path
from typing import List, Dict
import re
import pdb

class FS:
    """Handles filesystem operations"""
    def __init__(self, files: List[Path]):
        self.files = files

    def all_files_modifications(self) -> Dict[Path, float]:
        """Returns a dict of Path -> modification time"""
        return dict(map(lambda x: [x,
                                   self.file_timestamp(x)],
                        sum(map(self.all_files_recur,
                                self.files),
                            [])))

    @classmethod
    def all_files_recur(cls, path: Path) -> List[Path]:
        """Returns all files in `path`"""
        if path.is_file():
            if cls.valid_file(path):
                return [path]
            else:
                return []
        elif path.is_dir():
            return sum(map(cls.all_files_recur, path.iterdir()),
                       [])
        else:
            return []

    @classmethod
    def valid_file(cls, path: Path) -> bool:
        '''for now just org files'''
        return re.match('.+\\.org$',
                        path.as_posix()) != None
        
        
    @classmethod
    def file_timestamp(cls, path: Path) -> float:
        return path.stat().st_mtime

    @classmethod
    def to_path(cls, filepath: str) -> Path:
        Path(filepath)

