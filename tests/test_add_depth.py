from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main

def test_add_depth_flat(tmp_path: Path, capsys):
    foo_dir = tmp_path / "foo"
    foo_dir.mkdir()
    (foo_dir / "bar.txt").write_text("hello")
    
    code = main([
        str(tmp_path),
        "--add", "custom=true",
        "--add-depth", "2"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    assert len(data) == 2
    
    # foo is at depth 1, shouldn't have custom field
    foo_entry = next(d for d in data if d["name"] == "foo")
    assert "custom" not in foo_entry
    
    # bar.txt is at depth 2, should have custom field
    bar_entry = next(d for d in data if d["name"] == "bar.txt" and d.get("path") == "foo")
    assert bar_entry["custom"] is True

def test_add_depth_nested(tmp_path: Path, capsys):
    foo_dir = tmp_path / "foo"
    foo_dir.mkdir()
    (foo_dir / "bar.txt").write_text("hello")
    
    code = main([
        str(tmp_path),
        "--nested",
        "--no-defaults",
        "--add", "custom=true",
        "--add-depth", "2"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    # Root container 'foo' should NOT have 'custom'
    assert "custom" not in data["foo"]
    
    # Nested leaf 'bar.txt' SHOULD have 'custom'
    assert data["foo"]["bar.txt"]["custom"] is True
