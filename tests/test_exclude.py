"""Tests for the --exclude filtering mechanism."""

import json
from pathlib import Path

from flatdir.__main__ import main
from flatdir.listing import list_entries
from flatdir.plugins_loader import load_fields_file


# -- listing integration tests --


def test_exclude_by_starts_with(tmp_path: Path):
    """Entries whose starts_with field matches '.' should be excluded."""
    (tmp_path / "visible.txt").write_text("hello")
    (tmp_path / ".hidden").write_text("secret")
    (tmp_path / ".DS_Store").write_bytes(b"\x00")

    starts_with_plugin = Path(__file__).resolve().parents[1] / "src" / "flatdir" / "plugins" / "starts_with.py"
    fields = load_fields_file(str(starts_with_plugin))

    entries = list_entries(tmp_path, fields=fields, exclude=[("starts_with", ".")])
    names = [e["name"] for e in entries]

    assert "visible.txt" in names
    assert ".hidden" not in names
    assert ".DS_Store" not in names


def test_exclude_does_not_affect_unmatched(tmp_path: Path):
    """Exclude should leave non-matching entries intact."""
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")

    entries = list_entries(tmp_path, exclude=[("type", "directory")])
    assert len(entries) == 2
    assert all(e["type"] == "file" for e in entries)


def test_exclude_by_type(tmp_path: Path):
    """Excluding type=directory should keep only files."""
    (tmp_path / "file.txt").write_text("f")
    (tmp_path / "subdir").mkdir()

    entries = list_entries(tmp_path, exclude=[("type", "directory")])
    names = [e["name"] for e in entries]
    assert "file.txt" in names
    assert "subdir" not in names


def test_exclude_multiple_rules(tmp_path: Path):
    """Multiple exclude rules should all apply (OR logic)."""
    (tmp_path / ".hidden").write_text("h")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "visible.txt").write_text("v")

    starts_with_plugin = Path(__file__).resolve().parents[1] / "src" / "flatdir" / "plugins" / "starts_with.py"
    fields = load_fields_file(str(starts_with_plugin))

    entries = list_entries(
        tmp_path,
        fields=fields,
        exclude=[("starts_with", "."), ("type", "directory")],
    )
    names = [e["name"] for e in entries]
    assert names == ["visible.txt"]


def test_no_exclude_returns_all(tmp_path: Path):
    """Without exclude, all entries should be returned."""
    (tmp_path / ".hidden").write_text("h")
    (tmp_path / "visible.txt").write_text("v")

    entries = list_entries(tmp_path)
    assert len(entries) == 2


# -- CLI integration tests --


def test_cli_exclude_flag(tmp_path: Path, capsys):
    """--exclude type=directory should drop directories from JSON output."""
    (tmp_path / "file.txt").write_text("f")
    (tmp_path / "subdir").mkdir()

    rc = main(["--exclude", "type=directory", str(tmp_path)])
    assert rc == 0

    data = json.loads(capsys.readouterr().out)
    names = [e["name"] for e in data]
    assert "file.txt" in names
    assert "subdir" not in names


def test_cli_exclude_with_fields(tmp_path: Path, capsys):
    """--exclude combined with --fields should filter hidden files."""
    starts_with_plugin = Path(__file__).resolve().parents[1] / "src" / "flatdir" / "plugins" / "starts_with.py"

    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "readme.md").write_text("# hi")
    (tmp_path / "data" / ".secret").write_text("shh")

    rc = main([
        "--fields", str(starts_with_plugin),
        "--exclude", "starts_with=.",
        str(tmp_path / "data"),
    ])
    assert rc == 0

    data = json.loads(capsys.readouterr().out)
    names = [e["name"] for e in data]
    assert "readme.md" in names
    assert ".secret" not in names


def test_cli_exclude_missing_argument(capsys):
    """--exclude without a value should return error code 1."""
    rc = main(["--exclude"])
    assert rc == 1
    assert "error" in capsys.readouterr().err.lower()


def test_cli_exclude_bad_format(tmp_path: Path, capsys):
    """--exclude without = separator should return error code 1."""
    rc = main(["--exclude", "noequals", str(tmp_path)])
    assert rc == 1
    assert "error" in capsys.readouterr().err.lower()


def test_cli_exclude_all_types(tmp_path: Path, capsys):
    """--exclude type=directory --exclude type=file should return an empty list."""
    (tmp_path / "file.txt").write_text("f")
    (tmp_path / "subdir").mkdir()

    rc = main(["--exclude", "type=directory", "--exclude", "type=file", str(tmp_path)])
    assert rc == 0

    data = json.loads(capsys.readouterr().out)
    assert data == []
