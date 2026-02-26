"""Tests for the pattern_PRE_YR1_YR2_LOW_UP plugin."""

from pathlib import Path

from flatdir.plugins.pattern_PRE_YR1_YR2_LOW_UP import (
    pattern_prefix,
    pattern_year1,
    pattern_year2,
    pattern_lower,
    pattern_upper,
)


def test_pattern_valid_lowercase_first(tmp_path: Path):
    file_path = tmp_path / "ABC-19-20-aa-BB-BB"
    file_path.touch()
    
    assert pattern_prefix(file_path, tmp_path) == "ABC"
    assert pattern_year1(file_path, tmp_path) == "19"
    assert pattern_year2(file_path, tmp_path) == "20"
    assert pattern_lower(file_path, tmp_path) == "aa"
    assert pattern_upper(file_path, tmp_path) == "BB-BB"


def test_pattern_valid_uppercase_first(tmp_path: Path):
    file_path = tmp_path / "ABC-19-20-BB-BB-aa"
    file_path.touch()
    
    assert pattern_prefix(file_path, tmp_path) == "ABC"
    assert pattern_year1(file_path, tmp_path) == "19"
    assert pattern_year2(file_path, tmp_path) == "20"
    assert pattern_lower(file_path, tmp_path) == "aa"
    assert pattern_upper(file_path, tmp_path) == "BB-BB"


def test_pattern_mixed_length(tmp_path: Path):
    file_path = tmp_path / "ABC-19-20-aa-BBB-CC"
    file_path.touch()
    
    assert pattern_lower(file_path, tmp_path) == "aa"
    assert pattern_upper(file_path, tmp_path) == "BBB-CC"


def test_pattern_no_match(tmp_path: Path):
    file_path = tmp_path / "Invalid-Name-Format"
    file_path.touch()
    
    assert pattern_prefix(file_path, tmp_path) is None
    assert pattern_year1(file_path, tmp_path) is None
    assert pattern_year2(file_path, tmp_path) is None
    assert pattern_lower(file_path, tmp_path) is None
    assert pattern_upper(file_path, tmp_path) is None


def test_pattern_more_parts(tmp_path: Path):
    file_path = tmp_path / "ABC-19-20-aa-dd-BB"
    file_path.touch()

    assert pattern_prefix(file_path, tmp_path) == "ABC"
    assert pattern_year1(file_path, tmp_path) == "19"
    assert pattern_year2(file_path, tmp_path) == "20"
    assert pattern_lower(file_path, tmp_path) == "aa-dd"
    assert pattern_upper(file_path, tmp_path) == "BB"


def test_pattern_different_values(tmp_path: Path):
    file_path = tmp_path / "DEF-22-23-hello-WORLD"
    file_path.touch()

    assert pattern_prefix(file_path, tmp_path) == "DEF"
    assert pattern_year1(file_path, tmp_path) == "22"
    assert pattern_year2(file_path, tmp_path) == "23"
    assert pattern_lower(file_path, tmp_path) == "hello"
    assert pattern_upper(file_path, tmp_path) == "WORLD"
