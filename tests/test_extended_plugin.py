from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main

def test_extended_plugin(tmp_path: Path, capsys):
    test_file = tmp_path / "hello.txt"
    test_file.write_text("hello world")
    
    code = main([
        str(tmp_path),
        "--fields", "src/flatdir/plugins/extended.py"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    # Extract the entry for hello.txt
    hello = next(d for d in data if d["name"] == "hello.txt")
    
    assert "file_uuid" in hello
    assert len(hello["file_uuid"]) == 36  # UUID length
    
    assert hello["extension"] == "txt"
    assert hello["mime_type"] == "text/plain"
    
    assert "created_at" in hello
    assert "Z" in hello["created_at"] or "+00:00" in hello["created_at"]
    
    assert "modified_at" in hello
    assert "Z" in hello["modified_at"] or "+00:00" in hello["modified_at"]
    
    # "hello world" sha256
    expected_hash = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    assert hello["sha256"] == expected_hash
    assert hello["signature"] == expected_hash
    
    assert "permissions" in hello
    assert len(hello["permissions"]) == 3
    assert hello["permissions"].isdigit()
    
    assert "owner_id" in hello
    assert isinstance(hello["owner_id"], int)
