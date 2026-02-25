from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main

def test_no_defaults_flag(tmp_path: Path, capsys):
    (tmp_path / "foo.txt").write_text("hello")
    
    code = main([
        str(tmp_path),
        "--no-defaults",
        "--add", "custom=1"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    assert len(data) == 1
    # Check that default fields are missing, but name is preserved
    assert data[0]["name"] == "foo.txt"
    assert "type" not in data[0]
    assert "size" not in data[0]
    assert "mtime" not in data[0]
    # Check custom field was added
    assert data[0]["custom"] == 1

def test_no_defaults_with_nested(tmp_path: Path, capsys):
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "file.txt").write_text("hello")
    
    code = main([
        str(tmp_path),
        "--nested",
        "--no-defaults",
        "--add", "my_field=hi"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    # name should be stripped because of nesting, but defaults also gone
    assert data["dir1"]["my_field"] == "hi"
    assert "type" not in data["dir1"]
    
    assert data["dir1"]["file.txt"]["my_field"] == "hi"
    assert "type" not in data["dir1"]["file.txt"]
    assert "size" not in data["dir1"]["file.txt"]
