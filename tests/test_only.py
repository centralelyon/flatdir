"""Tests for the --only filtering mechanism."""

import json
from pathlib import Path

from flatdir.__main__ import main
from flatdir.listing import list_entries
from flatdir.plugins_loader import load_fields_file


# -- listing integration tests --


def test_only_by_type(tmp_path: Path):
    """--only type=file should drop directories."""
    (tmp_path / "file.txt").write_text("f")
    (tmp_path / "subdir").mkdir()

    entries = list_entries(tmp_path, only=[("type", "file")])
    names = [e["name"] for e in entries]
    assert "file.txt" in names
    assert "subdir" not in names


def test_only_multiple_same_field(tmp_path: Path):
    """Multiple --only for the same field uses OR logic."""
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.py").write_text("b")
    (tmp_path / "c.js").write_text("c")

    ext_plugin = Path(__file__).resolve().parents[1] / "src" / "flatdir" / "plugins" / "ext.py"
    fields = load_fields_file(str(ext_plugin))

    entries = list_entries(
        tmp_path, 
        fields=fields, 
        only=[("ext", ".txt"), ("ext", ".py")]
    )
    names = [e["name"] for e in entries]
    assert "a.txt" in names
    assert "b.py" in names
    assert "c.js" not in names


def test_only_multiple_different_fields(tmp_path: Path):
    """Multiple --only for different fields uses AND logic."""
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "subdir").mkdir()

    # Create a plugin dynamically to add 'ext'
    ext_plugin = Path(__file__).resolve().parents[1] / "src" / "flatdir" / "plugins" / "ext.py"
    fields = load_fields_file(str(ext_plugin))

    # Should match: type=file AND ext=.txt
    entries = list_entries(
        tmp_path,
        fields=fields,
        only=[("type", "file"), ("ext", ".txt")]
    )
    names = [e["name"] for e in entries]
    assert "a.txt" in names
    assert "subdir" not in names


# -- CLI integration tests --


def test_cli_only_flag(tmp_path: Path, capsys):
    """--only type=directory should include only directories from JSON output."""
    (tmp_path / "file.txt").write_text("f")
    (tmp_path / "subdir").mkdir()

    rc = main(["--only", "type=directory", str(tmp_path)])
    assert rc == 0

    data = json.loads(capsys.readouterr().out)
    names = [e["name"] for e in data]
    assert "file.txt" not in names
    assert "subdir" in names


def test_cli_only_missing_argument(capsys):
    """--only without a value should return error code 1."""
    rc = main(["--only"])
    assert rc == 1
    assert "error" in capsys.readouterr().err.lower()

def test_cli_exclude_and_only(tmp_path: Path, capsys):
    """--only type=directory --exclude type=directory should return empty list."""
    (tmp_path / "file.txt").write_text("f")
    (tmp_path / "subdir").mkdir()

    rc = main(["--only", "type=directory", "--exclude", "type=directory", str(tmp_path)])
    assert rc == 0

    data = json.loads(capsys.readouterr().out)
    assert data == []


def test_only_with_inline_array(tmp_path: Path, capsys):
    (tmp_path / "app.py").write_text("")
    (tmp_path / "script.js").write_text("")
    (tmp_path / "data.json").write_text("")
    (tmp_path / "style.css").write_text("")
    
    code = main([
        str(tmp_path),
        "--only", 'name=["app.py", "style.css"]'
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    assert len(data) == 2
    names = {d["name"] for d in data}
    assert "app.py" in names
    assert "style.css" in names
    assert "script.js" not in names


def test_exclude_with_inline_unquoted_array(tmp_path: Path, capsys):
    (tmp_path / "app.py").write_text("")
    (tmp_path / "script.js").write_text("")
    (tmp_path / "data.json").write_text("")
    (tmp_path / "style.css").write_text("")
    
    code = main([
        str(tmp_path),
        "--exclude", 'name=[app.py, script.js]'
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    assert len(data) == 2
    names = {d["name"] for d in data}
    assert "data.json" in names
    assert "style.css" in names
    assert "app.py" not in names


def test_only_with_whitespace_array_unquoted(tmp_path: Path, capsys):
    """Test arrays formatted with extra whitespace inside brackets."""
    (tmp_path / "a.js").write_text("")
    (tmp_path / "b.ts").write_text("")
    (tmp_path / "c.go").write_text("")
    
    code = main([
        str(tmp_path),
        "--only", 'name=[ a.js , c.go ]'
    ])
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    names = {d["name"] for d in data}
    assert "a.js" in names
    assert "c.go" in names
    assert "b.ts" not in names


def test_exclude_single_element_array(tmp_path: Path, capsys):
    """Test arrays containing only one element fallback structure."""
    (tmp_path / "target.txt").write_text("")
    (tmp_path / "other.txt").write_text("")
    
    code = main([
        str(tmp_path),
        "--exclude", 'name=[target.txt]'
    ])
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    names = {d["name"] for d in data}
    assert "other.txt" in names
    assert "target.txt" not in names


def test_exclude_combined_array_and_single(tmp_path: Path, capsys):
    """Tests array parsing stacking with standard sequential argument passing."""
    (tmp_path / "1.txt").write_text("")
    (tmp_path / "2.txt").write_text("")
    (tmp_path / "3.txt").write_text("")
    (tmp_path / "4.txt").write_text("")
    
    code = main([
        str(tmp_path),
        "--exclude", 'name=[1.txt, 2.txt]',
        "--exclude", "name=3.txt"
    ])
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    names = {d["name"] for d in data}
    assert "4.txt" in names
    assert "1.txt" not in names
    assert "2.txt" not in names
    assert "3.txt" not in names


