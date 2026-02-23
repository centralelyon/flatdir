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


def test_list_entries_with_limit(tmp_path: Path):
    """Test that list_entries respects the limit parameter."""
    # create a directory with 5 files
    for i in range(5):
        (tmp_path / f"file{i}.txt").write_text(f"content {i}")

    # Test with limit
    limited = listing.list_entries(tmp_path, limit=2)
    assert len(limited) == 2

    # Test without limit (None)
    unlimited = listing.list_entries(tmp_path, limit=None)
    assert len(unlimited) == 5

    # Test with negative limit (should return all)
    neg_limited = listing.list_entries(tmp_path, limit=-1)
    assert len(neg_limited) == 5

    # Test with zero limit (should return empty list)
    zero_limited = listing.list_entries(tmp_path, limit=0)
    assert len(zero_limited) == 0
