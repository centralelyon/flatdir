from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main

def test_ignore_typical(tmp_path: Path, capsys):
    # Setup some normal, should-be-included files
    foo_dir = tmp_path / "foo"
    foo_dir.mkdir()
    (foo_dir / "bar.txt").write_text("hello")
    
    # Setup "typical" ignore directories and files
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("...")
    
    node_dir = tmp_path / "node_modules"
    node_dir.mkdir()
    (node_dir / "package").write_text("...")
    
    (tmp_path / ".DS_Store").write_text("...")
    (tmp_path / "Thumbs.db").write_text("...")
    (tmp_path / "dummy.pyc").write_text("...")
    (tmp_path / "my_project.egg-info").mkdir()
    
    code = main([
        str(tmp_path),
        "--no-defaults",
        "--ignore-typical"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    # We should only see 'foo' and 'foo/bar.txt'
    names = [d["name"] for d in data]
    
    assert "foo" in names
    assert "foo/bar.txt" in names
    
    # Ignored typicals should emphatically NOT be returned
    assert ".git" not in names
    assert ".git/config" not in names
    assert "node_modules" not in names
    assert "node_modules/package" not in names
    assert ".DS_Store" not in names
    assert "Thumbs.db" not in names
    assert "dummy.pyc" not in names
    assert "my_project.egg-info" not in names
