from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main

def test_no_defaults_with_only_filter(tmp_path: Path, capsys):
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "file.txt").write_text("hello")
    
    code = main([
        str(tmp_path),
        "--no-defaults",
        "--only", "type=directory",
        "--add", "matched=true"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    assert len(data) == 1
    assert data[0]["matched"] is True

def test_no_defaults_with_exclude_filter(tmp_path: Path, capsys):
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "file.txt").write_text("hello")
    
    code = main([
        str(tmp_path),
        "--no-defaults",
        "--exclude", "type=file",
        "--add", "matched=true"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    assert len(data) == 1
    assert data[0]["matched"] is True
