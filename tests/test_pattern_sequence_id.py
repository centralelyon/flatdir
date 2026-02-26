"""Tests for the pattern_sequence_id plugin."""

from pathlib import Path

from flatdir.plugins.pattern_sequence_id import sequence_id, sequence_name


def test_sequence_id_normal(tmp_path: Path):
    file_path = tmp_path / "01_document.txt"
    file_path.touch()
    
    assert sequence_id(file_path, tmp_path) == 1
    assert sequence_name(file_path, tmp_path) == "document.txt"


def test_sequence_id_zero(tmp_path: Path):
    file_path = tmp_path / "00_intro"
    file_path.touch()
    
    assert sequence_id(file_path, tmp_path) == 0
    assert sequence_name(file_path, tmp_path) == "intro"


def test_sequence_id_no_padding(tmp_path: Path):
    file_path = tmp_path / "42_answer.md"
    file_path.touch()
    
    assert sequence_id(file_path, tmp_path) == 42
    assert sequence_name(file_path, tmp_path) == "answer.md"


def test_sequence_id_max_padding(tmp_path: Path):
    # 10 zeros
    file_path = tmp_path / "00000000001_max_pad"
    file_path.touch()
    
    assert sequence_id(file_path, tmp_path) == 1
    assert sequence_name(file_path, tmp_path) == "max_pad"


def test_sequence_id_too_much_padding(tmp_path: Path):
    # 11 zeros
    file_path = tmp_path / "000000000001_exceeded_pad"
    file_path.touch()
    
    assert sequence_id(file_path, tmp_path) is None
    assert sequence_name(file_path, tmp_path) is None


def test_sequence_id_no_match_middle(tmp_path: Path):
    file_path = tmp_path / "doc_01_version"
    file_path.touch()
    
    assert sequence_id(file_path, tmp_path) is None
    assert sequence_name(file_path, tmp_path) is None


def test_sequence_id_no_match(tmp_path: Path):
    file_path = tmp_path / "document_without_id"
    file_path.touch()
    
    assert sequence_id(file_path, tmp_path) is None
    assert sequence_name(file_path, tmp_path) is None
