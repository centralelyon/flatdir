"""Tests for the pattern_YR_MON_DAY_KW plugin."""

from pathlib import Path

from flatdir.plugins.pattern_YR_MON_DAY_KW import (
    pattern_year,
    pattern_month,
    pattern_day,
    pattern_kw,
    parsed_date,
)


def test_pattern_valid(tmp_path: Path):
    file_path = tmp_path / "25-09-06-AAA-BBB-CCC"
    file_path.touch()
    
    assert pattern_year(file_path, tmp_path) == "25"
    assert pattern_month(file_path, tmp_path) == "09"
    assert pattern_day(file_path, tmp_path) == "06"
    assert pattern_kw(file_path, tmp_path) == ["AAA", "BBB", "CCC"]
    assert parsed_date(file_path, tmp_path) == "2025-09-06"


def test_pattern_no_match(tmp_path: Path):
    file_path = tmp_path / "Invalid-Name-Format"
    file_path.touch()
    
    assert pattern_year(file_path, tmp_path) is None
    assert pattern_month(file_path, tmp_path) is None
    assert pattern_day(file_path, tmp_path) is None
    assert pattern_kw(file_path, tmp_path) is None
    assert parsed_date(file_path, tmp_path) is None
