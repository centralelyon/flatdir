"""Tests for the --match filtering option."""

import json
import subprocess
from pathlib import Path


def test_match_filename(tmp_path: Path):
    # Setup test directory
    (tmp_path / "ABC-19-20-John-Doe").mkdir()
    (tmp_path / "ABC-20-21-Jane-Smith").mkdir()
    (tmp_path / "Other-Dir").mkdir()
    (tmp_path / "ABC-19-20-John-Doe" / "file.txt").touch()

    # Run flatdir with --match pattern
    cmd = [
        "python",
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
        "python",
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
