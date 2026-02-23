"""Tests for the --output flag."""

import json
from pathlib import Path

from flatdir.__main__ import main


def test_output_writes_json_to_file(tmp_path: Path):
    """--output FILE should write JSON to the given file instead of stdout."""
    # create a directory with a file
    (tmp_path / "hello.txt").write_text("hello")

    out_file = tmp_path / "result.json"
    rc = main(["--output", str(out_file), str(tmp_path)])

    assert rc == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "hello.txt"


def test_output_creates_file_with_multiple_entries(tmp_path: Path):
    """--output should write all entries to the file."""
    for i in range(3):
        (tmp_path / f"file{i}.txt").write_text(f"content {i}")

    out_file = tmp_path / "out.json"
    rc = main(["--output", str(out_file), str(tmp_path)])

    assert rc == 0
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert len(data) == 3


def test_output_combined_with_limit(tmp_path: Path):
    """--output combined with --limit should write only limited entries."""
    for i in range(5):
        (tmp_path / f"file{i}.txt").write_text(f"content {i}")

    out_file = tmp_path / "limited.json"
    rc = main(["--limit", "2", "--output", str(out_file), str(tmp_path)])

    assert rc == 0
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert len(data) == 2


def test_output_combined_with_depth(tmp_path: Path):
    """--output combined with --depth should write only depth-limited entries."""
    (tmp_path / "root.txt").write_text("root")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "deep.txt").write_text("deep")

    out_file = tmp_path / "shallow.json"
    rc = main(["--depth", "0", "--output", str(out_file), str(tmp_path)])

    assert rc == 0
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["name"] == "root.txt"


def test_output_missing_argument(capsys):
    """--output without a file path should print an error and return 1."""
    rc = main(["--output"])

    assert rc == 1
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()


def test_no_output_flag_prints_to_stdout(tmp_path: Path, capsys):
    """Without --output, JSON should be printed to stdout."""
    (tmp_path / "a.txt").write_text("a")
    rc = main([str(tmp_path)])

    assert rc == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert len(data) == 1
