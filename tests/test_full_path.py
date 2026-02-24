"""Tests for the full_path plugin."""

from pathlib import Path

from flatdir.plugins.full_path import full_path


def test_full_path_plugin(tmp_path: Path):
    """full_path should return the absolute resolved path."""
    file_path = tmp_path / "a.txt"
    file_path.write_text("test")
    
    result = full_path(file_path, tmp_path)
    assert result == str(file_path.resolve())
