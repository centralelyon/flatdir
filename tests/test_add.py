from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import _parse_value, main

def test_parse_value():
    assert _parse_value("true") is True
    assert _parse_value("True") is True
    assert _parse_value("false") is False
    assert _parse_value("null") is None
    assert _parse_value("42") == 42
    assert _parse_value("3.14") == 3.14
    assert _parse_value("HELLO") == "HELLO"

def test_add_fields_cli(tmp_path: Path, capsys):
    (tmp_path / "foo.txt").write_text("hello")
    
    code = main([
        str(tmp_path),
        "--add", "custom_field=NA",
        "--add", "is_checked=true",
        "--add", "count=5"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    assert len(data) == 1
    assert data[0]["custom_field"] == "NA"
    assert data[0]["is_checked"] is True
    assert data[0]["count"] == 5

def test_add_fields_with_nested(tmp_path: Path, capsys):
    (tmp_path / "foo").mkdir()
    (tmp_path / "foo" / "bar.txt").write_text("hello")

    code = main([
        str(tmp_path),
        "--nested",
        "--add", "global=true"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    print("DUMP DATA:", json.dumps(data, indent=2))

    
    assert data["foo"]["global"] is True
    assert data["foo"]["bar.txt"]["global"] is True
