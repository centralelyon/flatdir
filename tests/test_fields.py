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


def test_cli_include_json_default(tmp_path: Path, capsys):
    """--include-json KEY should embed KEY using <dirname>.json by default."""
    scan_dir = tmp_path / "data"
    scan_dir.mkdir()
    
    sub_dir = scan_dir / "MSO"
    sub_dir.mkdir()
    
    # Create the JSON file with the same name as the directory
    json_path = sub_dir / "MSO.json"
    json_path.write_text('{"cours": "Dataviz", "credits": 5}', encoding="utf-8")
    
    rc = main(["--include-json", str(scan_dir)])
    assert rc == 0
    
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    # Find MSO directory entry
    mso_entry = next((e for e in data if e["name"] == "MSO"), None)
    assert mso_entry is not None
    assert "include" in mso_entry
    assert isinstance(mso_entry["include"], dict)
    assert mso_entry["include"]["cours"] == "Dataviz"
    assert mso_entry["include"]["credits"] == 5


def test_cli_include_json_custom_file(tmp_path: Path, capsys):
    """--include-json KEY=FILE should embed KEY using FILE explicitly."""
    scan_dir = tmp_path / "data"
    scan_dir.mkdir()
    
    sub_dir = scan_dir / "MOS"
    sub_dir.mkdir()
    
    json_path = sub_dir / "meta.json"
    json_path.write_text('{"active": true}', encoding="utf-8")
    
    rc = main(["--include-json", "payload=meta.json", str(scan_dir)])
    assert rc == 0
    
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    mos_entry = next((e for e in data if e["name"] == "MOS"), None)
    assert mos_entry is not None
    assert "payload" in mos_entry
    assert mos_entry["payload"]["active"] is True


def test_cli_join_default_local_key(tmp_path: Path, capsys):
    """--join FILE:REMOTE_KEY should join entries matching name=REMOTE_KEY."""
    scan_dir = tmp_path / "data"
    scan_dir.mkdir()
    
    sub_dir = scan_dir / "MSO"
    sub_dir.mkdir()
    
    db_file = tmp_path / "db.json"
    db_file.write_text('[{"cours": "MSO", "credits": 5}]', encoding="utf-8")
    
    rc = main(["--join", f"{db_file}:cours", str(scan_dir)])
    assert rc == 0
    
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    mso_entry = next((e for e in data if e["name"] == "MSO"), None)
    assert mso_entry is not None
    assert mso_entry.get("credits") == 5


def test_cli_join_explicit_local_key(tmp_path: Path, capsys):
    """--join FILE:REMOTE_KEY:LOCAL_KEY should join using the specified local key."""
    scan_dir = tmp_path / "data"
    scan_dir.mkdir()
    
    sub_dir = scan_dir / "item_123"
    sub_dir.mkdir()
    
    db_file = tmp_path / "db.json"
    db_file.write_text('{"db_id": "123", "value": "test"}', encoding="utf-8")
    
    # Inject a local key via --add to join against
    rc = main(["--add", "custom_id=123", "--join", f"{db_file}:db_id:custom_id", str(scan_dir)])
    assert rc == 0
    
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    entry = next((e for e in data if e["name"] == "item_123"), None)
    assert entry is not None
    assert entry.get("value") == "test"


def test_cli_pattern_pre_yr1_yr2_id_name(tmp_path: Path, capsys):
    """Test the pattern_PRE_YR1_YR2_ID_NAME.py plugin."""
    scan_dir = tmp_path / "data"
    scan_dir.mkdir()
    
    # Create an entry matching the pattern
    (scan_dir / "PE-25-26-70-Competition").mkdir()
    
    plugin_path = Path(__file__).parent.parent / "src" / "flatdir" / "plugins" / "pattern_PRE_YR1_YR2_ID_NAME.py"
    
    rc = main(["--fields", str(plugin_path), str(scan_dir)])
    assert rc == 0
    
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    entry = next((e for e in data if e["name"] == "PE-25-26-70-Competition"), None)
    assert entry is not None
    assert entry.get("pattern_prefix") == "PE"
    assert entry.get("pattern_year1") == "25"
    assert entry.get("pattern_year2") == "26"
    assert entry.get("pattern_id") == "70"
    assert entry.get("pattern_name") == "Competition"


def test_cli_pattern_yr_mo_dy_low_up(tmp_path: Path, capsys):
    """Test the pattern_YR_MO_DY_LOW_UP.py plugin."""
    scan_dir = tmp_path / "data"
    scan_dir.mkdir()
    
    # Create an entry matching the pattern
    (scan_dir / "25-09-29-Aaaa-BBBBB").mkdir()
    
    plugin_path = Path(__file__).parent.parent / "src" / "flatdir" / "plugins" / "pattern_YR_MO_DY_LOW_UP.py"
    
    rc = main(["--fields", str(plugin_path), str(scan_dir)])
    assert rc == 0
    
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    entry = next((e for e in data if e["name"] == "25-09-29-Aaaa-BBBBB"), None)
    assert entry is not None
    assert entry.get("pattern_year") == "25"
    assert entry.get("pattern_month") == "09"
    assert entry.get("pattern_day") == "29"
    assert entry.get("pattern_low") == "Aaaa"
    assert entry.get("pattern_up") == "BBBBB"
    assert entry.get("pattern_date") == "2025-09-29"
