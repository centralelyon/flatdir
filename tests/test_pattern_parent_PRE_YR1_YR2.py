"""Tests for the pattern_parent_PRE_YR1_YR2 plugin."""

from pathlib import Path

from flatdir.plugins.pattern_parent_PRE_YR1_YR2 import (
    parent_pattern_prefix,
    parent_pattern_year1,
    parent_pattern_year2,
)


def test_parent_pattern_valid(tmp_path: Path):
    parent_dir = tmp_path / "ABC-19-20"
    parent_dir.mkdir()
    file_path = parent_dir / "ABC-19-20-aa-BB"
    file_path.touch()
    
    assert parent_pattern_prefix(file_path, tmp_path) == "ABC"
    assert parent_pattern_year1(file_path, tmp_path) == "19"
    assert parent_pattern_year2(file_path, tmp_path) == "20"


def test_parent_pattern_no_match(tmp_path: Path):
    parent_dir = tmp_path / "Invalid-Parent-Dir"
    parent_dir.mkdir()
    file_path = parent_dir / "ABC-19-20-aa-BB"
    file_path.touch()
    
    assert parent_pattern_prefix(file_path, tmp_path) is None
    assert parent_pattern_year1(file_path, tmp_path) is None
    assert parent_pattern_year2(file_path, tmp_path) is None
