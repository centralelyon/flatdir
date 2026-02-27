"""Tests for the --fields plugin system."""

import json
from pathlib import Path

from flatdir.__main__ import main
from flatdir.listing import list_entries
from flatdir.plugins_loader import load_fields_file


# -- plugin loader tests --


def test_load_fields_file_extracts_public_functions(tmp_path: Path):
    """Public functions in the fields file become field providers."""
    fields_file = tmp_path / "my_fields.py"
    fields_file.write_text(
        "from pathlib import Path\n"
        "def ext(path: Path, root: Path) -> str:\n"
        "    return path.suffix\n"
        "def _private(path: Path, root: Path) -> str:\n"
        "    return 'hidden'\n"
    )
    fields = load_fields_file(str(fields_file))
    assert "ext" in fields
    assert "_private" not in fields


def test_load_fields_file_ignores_classes(tmp_path: Path):
    """Classes should not be picked up as field providers."""
    fields_file = tmp_path / "my_fields.py"
    fields_file.write_text(
        "from pathlib import Path\n"
        "class Foo:\n"
        "    pass\n"
        "def ext(path: Path, root: Path) -> str:\n"
        "    return path.suffix\n"
    )
    fields = load_fields_file(str(fields_file))
    assert "ext" in fields
    assert "Foo" not in fields


def test_load_fields_file_not_found():
    """A missing fields file should raise FileNotFoundError."""
    try:
        load_fields_file("/nonexistent/fields.py")
        assert False, "should have raised"
    except FileNotFoundError:
        pass


# -- listing integration tests --


def test_list_entries_with_custom_fields(tmp_path: Path):
    """Custom fields should appear in each entry."""
    (tmp_path / "doc.txt").write_text("hello")
    (tmp_path / "img.png").write_bytes(b"\x89PNG")

    fields = {
        "ext": lambda p, root: p.suffix,
        "stem": lambda p, root: p.stem,
    }
    entries = list_entries(tmp_path, fields=fields)
    assert len(entries) == 2
    for entry in entries:
        assert "ext" in entry
        assert "stem" in entry

    txt_entry = next(e for e in entries if e["name"] == "doc.txt")
    assert txt_entry["ext"] == ".txt"
    assert txt_entry["stem"] == "doc"


def test_list_entries_without_fields_unchanged(tmp_path: Path):
    """Without fields, entries should have only the built-in keys."""
    (tmp_path / "a.txt").write_text("a")
    entries = list_entries(tmp_path)
    assert set(entries[0].keys()) == {"name", "path", "type", "mtime", "size"}


# -- CLI integration tests --


def test_cli_fields_flag(tmp_path: Path, capsys):
    """--fields FILE should add custom fields to the JSON output."""
    # create a fields plugin
    fields_file = tmp_path / "my_fields.py"
    fields_file.write_text(
        "from pathlib import Path\n"
        "def ext(path: Path, root: Path) -> str:\n"
        "    return path.suffix\n"
    )

    # create a directory to scan
    scan_dir = tmp_path / "data"
    scan_dir.mkdir()
    (scan_dir / "notes.md").write_text("# Notes")

    rc = main(["--fields", str(fields_file), str(scan_dir)])
    assert rc == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data) == 1
    assert data[0]["ext"] == ".md"


def test_cli_fields_combined_with_output(tmp_path: Path):
    """--fields + --output should write enriched JSON to file."""
    fields_file = tmp_path / "my_fields.py"
    fields_file.write_text(
        "from pathlib import Path\n"
        "def ext(path: Path, root: Path) -> str:\n"
        "    return path.suffix\n"
    )

    scan_dir = tmp_path / "data"
    scan_dir.mkdir()
    (scan_dir / "a.py").write_text("pass")

    out_file = tmp_path / "result.json"
    rc = main([
        "--fields", str(fields_file),
        "--output", str(out_file),
        str(scan_dir),
    ])
    assert rc == 0
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data[0]["ext"] == ".py"


def test_cli_fields_missing_argument(capsys):
    """--fields without a file path should return error code 1."""
    rc = main(["--fields"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()


def test_cli_fields_nonexistent_file(capsys):
    """--fields with a nonexistent file should return error code 1."""
    rc = main(["--fields", "/nonexistent/fields.py", "."])
    assert rc == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err.lower()
