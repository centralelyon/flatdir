from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main

def test_with_headers_flat(tmp_path: Path, capsys):
    (tmp_path / "foo.txt").write_text("hello")
    
    code = main([
        str(tmp_path),
        "--with-headers"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    assert "headers" in data
    assert "entries" in data
    
    assert data["headers"]["entries_count"] == 1
    assert "execution_time_seconds" in data["headers"]
    assert "generated_at" in data["headers"]
    assert "command" in data["headers"]
    
    assert isinstance(data["entries"], list)
    assert len(data["entries"]) == 1
    assert data["entries"][0]["name"] == "foo.txt"

def test_with_headers_nested(tmp_path: Path, capsys):
    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "foo.txt").write_text("hello")
    
    code = main([
        str(tmp_path),
        "--nested",
        "--with-headers"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    assert "headers" in data
    assert "entries" in data
    
    assert data["headers"]["entries_count"] == 2
    
    assert isinstance(data["entries"], dict)
    assert "dir" in data["entries"]
    assert "foo.txt" in data["entries"]["dir"]
