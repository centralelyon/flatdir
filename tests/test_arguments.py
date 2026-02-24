"""Tests for CLI arguments validation."""

from pathlib import Path

from flatdir.__main__ import main


def test_cli_unknown_argument(tmp_path: Path, capsys):
    """An unknown argument like --foo should return error code 1."""
    rc = main(["--foo", str(tmp_path)])
    
    assert rc == 1
    captured = capsys.readouterr()
    assert "error: unrecognized argument: --foo" in captured.err


def test_cli_too_many_positionals(tmp_path: Path, capsys):
    """More than one positional argument should return error code 1."""
    rc = main([str(tmp_path), "another_dir"])
    
    assert rc == 1
    captured = capsys.readouterr()
    assert "error: too many positional arguments" in captured.err


def test_cli_valid_positional(tmp_path: Path, capsys):
    """A valid single positional argument works correctly."""
    (tmp_path / "a.txt").write_text("a")
    rc = main([str(tmp_path)])
    
    assert rc == 0
