from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import _build_nested, main

def test_build_nested_empty():
    assert _build_nested([]) == {}

def test_build_nested_simple_files():
    entries = [
        {"name": "a.txt", "size": 10},
        {"name": "b.txt", "size": 20},
    ]
    expected = {
        "a.txt": {"size": 10},
        "b.txt": {"size": 20},
    }
    assert _build_nested(entries) == expected

def test_build_nested_with_directories():
    entries = [
        {"name": "dir", "type": "directory"},
        {"name": "dir/file.txt", "type": "file"},
    ]
    expected = {
        "dir": {
            "type": "directory",
            "file.txt": {"type": "file"},
        }
    }
    assert _build_nested(entries) == expected

def test_build_nested_directory_after_file():
    # If a file is processed before its directory parent attributes
    entries = [
        {"name": "dir/file.txt", "type": "file"},
        {"name": "dir", "type": "directory"},
    ]
    expected = {
        "dir": {
            "type": "directory",
            "file.txt": {"type": "file"},
        }
    }
    assert _build_nested(entries) == expected

def test_build_nested_deep_hierarchy():
    entries = [
        {"name": "a/b/c/file.txt", "type": "file"},
        {"name": "a/b", "type": "directory"}
    ]
    expected = {
        "a": {
            "b": {
                "type": "directory",
                "c": {
                    "file.txt": {"type": "file"}
                }
            }
        }
    }
    assert _build_nested(entries) == expected

def test_main_nested(tmp_path: Path, capsys):
    (tmp_path / "foo").mkdir()
    (tmp_path / "foo" / "bar.txt").write_text("hello")

    # Run without nested
    code = main([str(tmp_path)])
    assert code == 0
    out, _ = capsys.readouterr()
    flat_data = json.loads(out)
    assert isinstance(flat_data, list)
    
    # Run with nested
    code = main(["--nested", str(tmp_path)])
    assert code == 0
    out, _ = capsys.readouterr()
    nested_data = json.loads(out)
    
    assert isinstance(nested_data, dict)
    assert "foo" in nested_data
    assert "bar.txt" in nested_data["foo"]
