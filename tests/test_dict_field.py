"""Tests for the --dict-field functionality."""

import json
import subprocess
from pathlib import Path


def test_dict_field_default_filename(tmp_path: Path):
    """--dict-field KEY should read from <dirname>.json and extract the key if present."""
    (tmp_path / "projectA").mkdir()
    (tmp_path / "projectB").mkdir()
    
    # Matching json
    (tmp_path / "projectA" / "projectA.json").write_text('{"year": 2023, "author": "Alice"}', encoding="utf-8")
    # Missing json
    # projectB has no matching JSON file
    
    result = subprocess.run(
        ["python", "-m", "flatdir", str(tmp_path), "--dict-field", "year"],
        capture_output=True,
        text=True,
        check=True,
    )
    
    data = json.loads(result.stdout)
    entries_by_name = {e["name"]: e for e in data}
    
    # Exists
    assert "year" in entries_by_name["projectA"]
    assert entries_by_name["projectA"]["year"] == 2023
    
    # Missing, shouldn't error and shouldn't inject key
    assert "year" not in entries_by_name["projectB"]


def test_dict_field_custom_filename(tmp_path: Path):
    """--dict-field KEY=FILE should read from FILE and extract the key if present."""
    (tmp_path / "repoX").mkdir()
    (tmp_path / "repoX" / "package.json").write_text('{"version": "1.0.4"}', encoding="utf-8")
    
    result = subprocess.run(
        ["python", "-m", "flatdir", str(tmp_path), "--dict-field", "version=package.json"],
        capture_output=True,
        text=True,
        check=True,
    )
    
    data = json.loads(result.stdout)
    entries_by_name = {e["name"]: e for e in data}
    
    assert "version" in entries_by_name["repoX"]
    assert entries_by_name["repoX"]["version"] == "1.0.4"


def test_dict_field_multiple_keys_same_file(tmp_path: Path):
    """--dict-field can extract multiple keys from the same file."""
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "meta.json").write_text('{"a": 1, "b": 2, "c": 3}', encoding="utf-8")
    
    result = subprocess.run(
        [
            "python", "-m", "flatdir", str(tmp_path), 
            "--dict-field", "a=meta.json", 
            "--dict-field", "c=meta.json"
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    
    data = json.loads(result.stdout)
    entries_by_name = {e["name"]: e for e in data}
    
    assert "a" in entries_by_name["app"]
    assert entries_by_name["app"]["a"] == 1
    assert "c" in entries_by_name["app"]
    assert entries_by_name["app"]["c"] == 3
    assert "b" not in entries_by_name["app"]


def test_dict_field_with_filter(tmp_path: Path):
    """--only should correctly filter items based on extracted dict-fields."""
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "meta.json").write_text('{"status": "active"}', encoding="utf-8")
    
    (tmp_path / "dir2").mkdir()
    (tmp_path / "dir2" / "meta.json").write_text('{"status": "archived"}', encoding="utf-8")
    
    result = subprocess.run(
        [
            "python", "-m", "flatdir", str(tmp_path), 
            "--dict-field", "status=meta.json",
            "--only", "status=active"
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    
    data = json.loads(result.stdout)
    names = [e["name"] for e in data]
    
    assert "dir1" in names
    assert "dir2" not in names
