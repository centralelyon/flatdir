from pathlib import Path

from flatdir import listing


def test_list_entries_sort_by_name(tmp_path: Path):
    """Test default sorting by name."""
    (tmp_path / "c.txt").write_text("1")
    (tmp_path / "a.txt").write_text("123")
    (tmp_path / "b.txt").write_text("12")

    entries = listing.list_entries(tmp_path)
    
    names = [e["name"] for e in entries]
    assert names == ["a.txt", "b.txt", "c.txt"]


def test_list_entries_sort_by_name_desc(tmp_path: Path):
    """Test sorting by name descending."""
    (tmp_path / "c.txt").write_text("1")
    (tmp_path / "a.txt").write_text("123")
    (tmp_path / "b.txt").write_text("12")

    entries = listing.list_entries(tmp_path, sort_desc=True)
    
    names = [e["name"] for e in entries]
    assert names == ["c.txt", "b.txt", "a.txt"]


def test_list_entries_sort_by_size(tmp_path: Path):
    """Test numerical sorting by size."""
    (tmp_path / "z.txt").write_text("1")          # size 1
    (tmp_path / "x.txt").write_text("123456789")  # size 9
    (tmp_path / "y.txt").write_text("12")         # size 2

    # If it was lexicographical, 1, 12, 9 -> z, y, x
    # Since it's numerical, 1, 2, 9 -> z, y, x
    entries = listing.list_entries(tmp_path, sort_by="size")
    sizes = [e["size"] for e in entries]
    names = [e["name"] for e in entries]
    
    assert sizes == [1, 2, 9]
    assert names == ["z.txt", "y.txt", "x.txt"]


def test_list_entries_sort_by_size_desc(tmp_path: Path):
    """Test numerical sorting by size descending."""
    (tmp_path / "a.txt").write_text("1")          # size 1
    (tmp_path / "b.txt").write_text("123456789")  # size 9
    (tmp_path / "c.txt").write_text("12")         # size 2

    entries = listing.list_entries(tmp_path, sort_by="size", sort_desc=True)
    names = [e["name"] for e in entries]
    
    assert names == ["b.txt", "c.txt", "a.txt"]


def test_list_entries_sort_by_missing_field(tmp_path: Path):
    """Test sorting by a field that might be missing gracefully."""
    (tmp_path / "a.txt").write_text("1")
    (tmp_path / "b.txt").write_text("1")
    
    # Missing fields should be handled gracefully (defaulting to 0/empty tuple block)
    entries = listing.list_entries(tmp_path, sort_by="non_existent_field")
    assert len(entries) == 2
