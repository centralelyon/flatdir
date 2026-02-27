from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main

def test_min_depth_flat(tmp_path: Path, capsys):
    foo_dir = tmp_path / "foo"
    foo_dir.mkdir()
    (foo_dir / "bar.txt").write_text("hello")
    
    code = main([
        str(tmp_path),
        "--no-defaults",
        "--min-depth", "2"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    # We should only see 'bar.txt' (depth 2), NOT 'foo' (depth 1)
    assert len(data) == 1
    assert data[0]["name"] == "bar.txt"

def test_min_depth_nested(tmp_path: Path, capsys):
    foo_dir = tmp_path / "foo"
    foo_dir.mkdir()
    (foo_dir / "bar.txt").write_text("hello")
    
    code = main([
        str(tmp_path),
        "--nested",
        "--no-defaults",
        "--min-depth", "2"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    # Because 'foo' was filtered out, nested builder reconstructs it but ONLY with 'bar.txt' leaf info
    assert "bar.txt" in data["foo"]
    # name is preserved in the leaf but dropped from upper wrapper keys during reconstruction
    assert data["foo"]["bar.txt"] == {}
