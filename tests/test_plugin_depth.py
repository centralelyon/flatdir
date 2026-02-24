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
