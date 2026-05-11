from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main
from flatdir import compare


def test_diff_option_with_plain_flatdir_json(tmp_path: Path, capsys):
    scan_dir = tmp_path / "data"
    scan_dir.mkdir()
    (scan_dir / "a.txt").write_text("a")

    baseline = tmp_path / "baseline.json"
    rc = main([str(scan_dir), "--output", str(baseline)])
    assert rc == 0

    (scan_dir / "b.txt").write_text("b")

    rc = main([str(scan_dir), "--diff", str(baseline)])
    assert rc == 0

    out, _ = capsys.readouterr()
    data = json.loads(out)

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "b.txt"


def test_diff_option_with_headers_wrapped_flatdir_json(tmp_path: Path, capsys):
    scan_dir = tmp_path / "data"
    scan_dir.mkdir()
    (scan_dir / "a.txt").write_text("a")

    baseline = tmp_path / "baseline_with_headers.json"
    rc = main([str(scan_dir), "--with-headers", "--output", str(baseline)])
    assert rc == 0

    (scan_dir / "b.txt").write_text("b")

    rc = main([str(scan_dir), "--diff", str(baseline)])
    assert rc == 0

    out, _ = capsys.readouterr()
    data = json.loads(out)

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "b.txt"


def test_diff_option_requires_file_argument(capsys):
    rc = main(["--diff"])
    assert rc == 1

    _, err = capsys.readouterr()
    assert "--diff requires a file path argument" in err


def test_compare_entries(tmp_path: Path):
    """Test the compare_entries function with added, removed, and modified entries."""
    old_entries = [
        {"path": ".", "name": "file1.txt", "size": 100},
        {"path": ".", "name": "file2.txt", "size": 200},
        {"path": ".", "name": "file3.txt", "size": 300},
    ]
    
    new_entries = [
        {"path": ".", "name": "file1.txt", "size": 100},  # unchanged
        {"path": ".", "name": "file2.txt", "size": 250},  # modified
        # file3.txt is removed
        {"path": ".", "name": "file4.txt", "size": 400},  # added
    ]
    
    result = compare.compare_entries(old_entries, new_entries)

    assert len(result) == 3

    by_key = {(entry["path"], entry["name"]): entry for entry in result}

    # Check added entry
    assert (".", "file4.txt") in by_key
    assert by_key[(".", "file4.txt")]["size"] == 400
    assert by_key[(".", "file4.txt")]["_status"] == compare.status.ADDED

    # Check removed entry
    assert (".", "file3.txt") in by_key
    assert by_key[(".", "file3.txt")]["size"] == 300
    assert by_key[(".", "file3.txt")]["_status"] == compare.status.REMOVED

    # Check modified entry
    assert (".", "file2.txt") in by_key
    assert by_key[(".", "file2.txt")]["size"] == 250
    assert by_key[(".", "file2.txt")]["_status"] == compare.status.MODIFIED