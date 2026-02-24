from pathlib import Path

from flatdir import listing


def test_list_entries_with_depth(tmp_path: Path):
    """Test that list_entries respects the depth parameter."""
    # create a nested directory structure
    # tmp_path/
    #   file0.txt
    #   sub1/
    #     file1.txt
    #     sub2/
    #       file2.txt
    (tmp_path / "file0.txt").write_text("depth 0")
    sub1 = tmp_path / "sub1"
    sub1.mkdir()
    (sub1 / "file1.txt").write_text("depth 1")
    sub2 = sub1 / "sub2"
    sub2.mkdir()
    (sub2 / "file2.txt").write_text("depth 2")

    # Test with depth=0 (root level only: file0.txt + sub1/)
    depth0 = listing.list_entries(tmp_path, depth=0)
    assert len(depth0) == 2
    assert "file0.txt" in [e["name"] for e in depth0]
    assert "sub1" in [e["name"] for e in depth0]

    # Test with depth=1 (root + one level down)
    depth1 = listing.list_entries(tmp_path, depth=1)
    assert len(depth1) == 4  # file0.txt, sub1/, sub1/file1.txt, sub1/sub2/
    names = {e["name"] for e in depth1}
    assert "file0.txt" in names
    assert any("file1.txt" in n for n in names)

    # Test with depth=2 (root + two levels down)
    depth2 = listing.list_entries(tmp_path, depth=2)
    assert len(depth2) == 5  # file0.txt, sub1/, sub1/file1.txt, sub1/sub2/, sub1/sub2/file2.txt

    # Test with no depth limit (None)
    unlimited = listing.list_entries(tmp_path, depth=None)
    assert len(unlimited) == 5
"""Tests for the depth plugin."""

from pathlib import Path

from flatdir.plugins.depth import depth


def test_depth_plugin(tmp_path: Path):
    """Depth should represent the number of directories from root."""
    root = tmp_path
    
    # root itself is depth 0
    assert depth(root, root) == 0
    
    # file at root is depth 1
    file_at_root = root / "a.txt"
    assert depth(file_at_root, root) == 1
    
    # file in a sub dir is depth 2
    subdir = root / "sub"
    file_in_sub = subdir / "b.txt"
    
    assert depth(subdir, root) == 1
    assert depth(file_in_sub, root) == 2
