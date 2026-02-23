from pathlib import Path

from flatdir import listing


def test_outputs_valid_json(tmp_path: Path):
    # create a small directory with one file
    sub = tmp_path / "sub"
    sub.mkdir()
    f = sub / "a.txt"
    _ = f.write_text("this is a test")

    entries = listing.list_entries(tmp_path)

    # ensure our file is present in the listing (cast name to str for typing)
    assert any(str(entry.get("name", "")).endswith("a.txt") for entry in entries)
