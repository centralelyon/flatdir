from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main

def test_id_flag(tmp_path: Path, capsys):
    (tmp_path / "b_file.txt").write_text("hello")
    (tmp_path / "a_file.txt").write_text("world")
    
    code = main([
        str(tmp_path),
        "--no-defaults",
        "--id"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    # Check that sorting occurs correctly (a_file.txt should be first with id 1)
    assert len(data) == 2
    assert data[0]["name"] == "a_file.txt"
    assert data[0]["id"] == 1
    
    assert data[1]["name"] == "b_file.txt"
    assert data[1]["id"] == 2

