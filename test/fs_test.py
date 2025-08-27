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

        res = {Path(top_org_file.name), Path(bottom_org_file.name)}

        fs = FS([Path(td.name)])
        found_files = set(fs.all_files_recur(Path(td.name)))
        self.assertSetEqual(found_files, res)

    def test_ignore_patterns(self):
        td = TemporaryDirectory()
        project_path = Path(td.name) / "some_project"
        project_path.mkdir()
        tilde_file = project_path / "something.txt~"
        tilde_file.touch()
        hash_file = project_path / "#something.txt#"
        hash_file.touch()
        env_path = project_path / ".venv"
        env_path.mkdir()
        env_file = env_path / "something.py"
        env_file.touch()
        pycache = project_path / "__pycache__"
        pycache.mkdir()
        ignored_file = pycache / "foo.pyc"
        ignored_file.touch()

        fs = FS([Path(td.name)])
        found_files = set(fs.all_files_recur(Path(td.name)))
        print("found things")
        print(found_files)
        self.assertNotIn(env_path, found_files)
        self.assertNotIn(tilde_file, found_files)
        self.assertNotIn(hash_file, found_files)
        self.assertNotIn(env_file, found_files)
        self.assertNotIn(ignored_file, found_files)

    def test_ignore_override_by_match(self):
        td = TemporaryDirectory()
        env_path = Path(td.name) / ".env"
        env_path.touch()
        pycache = Path(td.name) / "__pycache__"
        pycache.mkdir()
        pyc_file = pycache / "foo.pyc"
        pyc_file.touch()

        match_env = lambda p: p.is_file() and p.name == ".env"
        match_pyc = lambda p: p.is_file() and p.suffix == ".pyc"
        fs = FS(
            [Path(td.name)],
            file_match=lambda p: match_env(p) or match_pyc(p),
            prune_ignored_dirs=False,
            match_supplied=True,
        )
        found_files = set(fs.all_files_recur(Path(td.name)))

        self.assertIn(env_path, found_files)
        self.assertIn(pyc_file, found_files)
