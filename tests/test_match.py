"""Tests for the --match filtering option."""

import json
import subprocess
import sys
from pathlib import Path


def test_match_filename(tmp_path: Path):
    # Setup test directory
    (tmp_path / "ABC-19-20-John-Doe").mkdir()
    (tmp_path / "ABC-20-21-Jane-Smith").mkdir()
    (tmp_path / "Other-Dir").mkdir()
    (tmp_path / "ABC-19-20-John-Doe" / "file.txt").touch()

    # Run flatdir with --match pattern
    cmd = [
        sys.executable,
        "-m",
        "flatdir",
        str(tmp_path),
        "--match",
        r"^ABC-\d{2}-\d{2}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    entries = json.loads(result.stdout)
    names = [e["name"] for e in entries]

    assert "ABC-19-20-John-Doe" in names
    assert "ABC-20-21-Jane-Smith" in names
    assert "Other-Dir" not in names
    # file.txt doesn't match the pattern
    assert "file.txt" not in names


def test_match_with_only(tmp_path: Path):
    (tmp_path / "ABC-19-20").mkdir()
    (tmp_path / "ABC-19-20" / "ABC-file").touch()
    
    # Run flatdir with --match and --only type=directory
    cmd = [
        sys.executable,
        "-m",
        "flatdir",
        str(tmp_path),
        "--match",
        r"^ABC",
        "--only",
        "type=directory",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    entries = json.loads(result.stdout)
    names = [e["name"] for e in entries]

    assert "ABC-19-20" in names
    assert "ABC-file" not in names  # Filtered out by --only type=directory


def test_match_year_prefix_includes_2022_directory(tmp_path: Path):
    (tmp_path / "2022-Competition").mkdir()
    (tmp_path / "2021-Archive").mkdir()
    (tmp_path / "notes-2022").mkdir()
    (tmp_path / "report.txt").touch()

    cmd = [
        sys.executable,
        "-m",
        "flatdir",
        str(tmp_path),
        "--match",
        r"^[0-9]{4}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    entries = json.loads(result.stdout)
    names = [e["name"] for e in entries]

    assert "2022-Competition" in names
    assert "2021-Archive" in names
    assert "notes-2022" not in names
    assert "report.txt" not in names


def test_match_supports_character_classes_and_quantifiers(tmp_path: Path):
    (tmp_path / "2022-test").mkdir()
    (tmp_path / "202A-test").mkdir()
    (tmp_path / "2022").mkdir()
    (tmp_path / "notes-2022").mkdir()

    cmd = [
        sys.executable,
        "-m",
        "flatdir",
        str(tmp_path),
        "--match",
        r"^[0-9]{4}-",
        "--only",
        "type=directory",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    entries = json.loads(result.stdout)
    names = [e["name"] for e in entries]

    assert "2022-test" in names
    assert "202A-test" not in names
    assert "2022" not in names
    assert "notes-2022" not in names


def test_match_supports_end_anchor_for_exact_year(tmp_path: Path):
    (tmp_path / "2022").mkdir()
    (tmp_path / "1999").mkdir()
    (tmp_path / "2022-test").mkdir()
    (tmp_path / "year-2022").mkdir()

    cmd = [
        sys.executable,
        "-m",
        "flatdir",
        str(tmp_path),
        "--match",
        r"^[0-9]{4}$",
        "--only",
        "type=directory",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    entries = json.loads(result.stdout)
    names = [e["name"] for e in entries]

    assert "2022" in names
    assert "1999" in names
    assert "2022-test" not in names
    assert "year-2022" not in names
