"""Tests for the pattern_PRE_YR1_YR2 plugin."""

from pathlib import Path

from flatdir.plugins.pattern_PRE_YR1_YR2 import (
    pattern_prefix,
    pattern_year1,
    pattern_year2,
)


def test_pattern_valid(tmp_path: Path):
    file_path = tmp_path / "ABC-19-20"
    file_path.touch()
    
    assert pattern_prefix(file_path, tmp_path) == "ABC"
    assert pattern_year1(file_path, tmp_path) == "19"
    assert pattern_year2(file_path, tmp_path) == "20"


def test_pattern_valid_another(tmp_path: Path):
    file_path = tmp_path / "DEF-22-23"
    file_path.touch()
    
    assert pattern_prefix(file_path, tmp_path) == "DEF"
    assert pattern_year1(file_path, tmp_path) == "22"
    assert pattern_year2(file_path, tmp_path) == "23"


def test_pattern_no_match_extra_parts(tmp_path: Path):
    file_path = tmp_path / "ABC-19-20-aa-BB"
    file_path.touch()
    
    assert pattern_prefix(file_path, tmp_path) is None
    assert pattern_year1(file_path, tmp_path) is None
    assert pattern_year2(file_path, tmp_path) is None


def test_pattern_no_match_invalid_format(tmp_path: Path):
    file_path = tmp_path / "Invalid-Name-Format"
    file_path.touch()
    
    assert pattern_prefix(file_path, tmp_path) is None
    assert pattern_year1(file_path, tmp_path) is None
    assert pattern_year2(file_path, tmp_path) is None
