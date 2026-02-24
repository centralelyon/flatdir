"""Tests for the parent plugin."""

from pathlib import Path

from flatdir.plugins.parent import parent


def test_parent_plugin(tmp_path: Path):
    """parent should return the relative path to the entry's parent."""
    root = tmp_path
    
    # parent of root is "."
    assert parent(root, root) == "."
    
    # file at root
    file_at_root = root / "a.txt"
    assert parent(file_at_root, root) == "."
    
    # file in a sub dir
    subdir = root / "sub"
    file_in_sub = subdir / "b.txt"
    
    assert parent(subdir, root) == "."
    assert parent(file_in_sub, root) == "sub"
    
    # nested file
    nested = subdir / "nested"
    nested_file = nested / "c.txt"
    assert parent(nested_file, root) == "sub/nested"
