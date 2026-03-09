import json
import pytest
from pathlib import Path
from flatdir.__main__ import main

def test_only_field_existence(tmp_path: Path, capsys):
    """Test filtering by field existence (without = sign)."""
    # Create two directories, one that will match a pattern and one that won't
    (tmp_path / "2024-test").mkdir()
    (tmp_path / "not-matching").mkdir()
    
    # Use the pattern_FULLYR_KEYWORDS plugin
    plugin_path = "src/flatdir/plugins/pattern_FULLYR_KEYWORDS.py"
    
    # Run with --only pattern_year
    code = main([
        str(tmp_path),
        "--fields", plugin_path,
        "--only", "pattern_year",
        "--only", "type=directory"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    entries = json.loads(out)
    
    # Only 2024-test should be returned because it has the pattern_year field
    assert len(entries) == 1
    assert entries[0]["name"] == "2024-test"
    assert "pattern_year" in entries[0]

def test_only_field_existence_multiple(tmp_path: Path, capsys):
    """Test filtering by multiple field existences."""
    (tmp_path / "2024-test").mkdir()
    (tmp_path / "simple").mkdir()
    (tmp_path / "file.txt").touch()
    
    # Custom fields file
    fields_file = tmp_path / "custom_fields.py"
    fields_file.write_text("""
from pathlib import Path
def is_special(path: Path, root: Path):
    if "test" in path.name:
        return True
    return None

def has_content(path: Path, root: Path):
    if path.is_file():
        return True
    return None
""")
    
    # 1. Filter by is_special
    code = main([str(tmp_path), "--fields", str(fields_file), "--only", "is_special", "--ignore-typical"])
    assert code == 0
    out, _ = capsys.readouterr()
    entries = json.loads(out)
    # Should only find '2024-test'
    assert len(entries) == 1
    assert entries[0]["name"] == "2024-test"
    
    # 2. Filter by has_content AND name=file.txt to be absolutely sure
    code = main([str(tmp_path), "--fields", str(fields_file), "--only", "has_content", "--only", "name=file.txt", "--ignore-typical"])
    assert code == 0
    out, _ = capsys.readouterr()
    entries = json.loads(out)
    assert len(entries) == 1
    assert entries[0]["name"] == "file.txt"

def test_only_field_existence_with_value_mix(tmp_path: Path, capsys):
    """Test mixing field existence and field value filters."""
    (tmp_path / "2024-test").mkdir()
    (tmp_path / "2023-test").mkdir()
    (tmp_path / "other").mkdir()
    
    plugin_path = "src/flatdir/plugins/pattern_FULLYR_KEYWORDS.py"
    
    # Filter by pattern_year (existence) AND pattern_year=2024 (value)
    code = main([
        str(tmp_path),
        "--fields", plugin_path,
        "--only", "pattern_year",
        "--only", "pattern_year=2024"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    entries = json.loads(out)
    
    assert len(entries) == 1
    assert entries[0]["name"] == "2024-test"
    assert entries[0]["pattern_year"] == "2024"

def test_only_non_existent_field(tmp_path: Path, capsys):
    """Test filtering by a field that doesn't exist anywhere."""
    (tmp_path / "a").mkdir()
    
    code = main([str(tmp_path), "--only", "something_weird"])
    assert code == 0
    out, _ = capsys.readouterr()
    entries = json.loads(out)
    assert len(entries) == 0
