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
