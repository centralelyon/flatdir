from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main

def test_text_plugin(tmp_path: Path, capsys):
    (tmp_path / "hello.txt").write_text("Hello world!\nThis is a test.")
    (tmp_path / "empty.md").write_text("   \n  \t  ")
    (tmp_path / "binary.bin").write_bytes(b"\x00\x01\x02")
    (tmp_path / "folder").mkdir()
    
    code = main([
        str(tmp_path),
        "--fields", "src/flatdir/plugins/text.py",
        "--sort", "name"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    # Extract entries
    hello = next(d for d in data if d["name"] == "hello.txt")
    empty = next(d for d in data if d["name"] == "empty.md")
    binary = next(d for d in data if d["name"] == "binary.bin")
    folder = next(d for d in data if d["name"] == "folder")
    
    # Directories and non-text formats should be ignored
    assert "text_lines" not in folder
    assert "text_lines" not in binary
    
    # Assert counts for standard text
    assert hello["text_lines"] == 2
    assert hello["text_words"] == 6
    assert hello["text_characters"] == 28
    assert hello["text_is_blank"] is False
    
    # Assert pure whitespace files
    assert empty["text_lines"] == 2
    assert empty["text_words"] == 0
    assert empty["text_is_blank"] is True
