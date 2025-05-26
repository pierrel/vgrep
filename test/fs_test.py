from unittest import TestCase
from tempfile import NamedTemporaryFile, TemporaryDirectory
from pathlib import Path
from vgrep.fs import FS

class TestFS(TestCase):
    def test_files_modifications(self):
        td = TemporaryDirectory()
        top_org_file = NamedTemporaryFile(dir=td.name,
                                          suffix=".org")
        bd = TemporaryDirectory(dir=td.name)
        bottom_org_file = NamedTemporaryFile(dir=bd.name,
                                             suffix=".org")

        fs = FS([Path(td.name)])

        res = set(map(Path,
                      map(lambda x: x.name,
                          [bottom_org_file, top_org_file])))

        found_files_modifications = fs.all_files_modifications()
        found_files = set(found_files_modifications.keys())
        self.assertSetEqual(found_files,
                            res)

    def test_all_files_recur(self):
        td = TemporaryDirectory()
        top_org_file = NamedTemporaryFile(dir=td.name,
                                          suffix=".org")
        bd = TemporaryDirectory(dir=td.name)
        bottom_org_file = NamedTemporaryFile(dir=bd.name,
                                             suffix=".org")

        res = set(map(Path,
                      map(lambda x: x.name,
                          [bottom_org_file, top_org_file])))

        found_files = set(FS.all_files_recur(Path(td.name)))
        self.assertSetEqual(found_files,
                            res)
