from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main


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
