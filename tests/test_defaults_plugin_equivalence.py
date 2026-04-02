"""Test that --fields src/flatdir/plugins/defaults.py produces the same output as the default command.

This ensures that defaults.py faithfully mirrors the built-in field set (name, path, type, mtime, size).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from flatdir.__main__ import main


DEFAULTS_PLUGIN = Path(__file__).parent.parent / "src" / "flatdir" / "plugins" / "defaults.py"


@pytest.fixture()
def sample_dir(tmp_path: Path) -> Path:
    """Create a representative directory tree for comparison tests."""
    (tmp_path / "readme.md").write_text("# Hello")
    (tmp_path / "data.json").write_text('{"key": "value"}')
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "nested.txt").write_text("nested content")
    return tmp_path


def _run(argv: list[str], capsys) -> list[dict]:
    rc = main(argv)
    assert rc == 0
    out, _ = capsys.readouterr()
    return json.loads(out)


def test_defaults_plugin_produces_same_keys_as_default(sample_dir: Path, capsys):
    """--fields defaults.py should yield the same field keys as the default run."""
    default_data = _run([str(sample_dir)], capsys)
    fields_data = _run(["--fields", str(DEFAULTS_PLUGIN), str(sample_dir)], capsys)

    assert len(default_data) == len(fields_data)
    for default_entry, fields_entry in zip(default_data, fields_data):
        assert set(default_entry.keys()) == set(fields_entry.keys()), (
            f"Key mismatch for entry '{default_entry.get('name')}': "
            f"default={set(default_entry.keys())}, fields={set(fields_entry.keys())}"
        )


def test_defaults_plugin_produces_same_values_as_default(sample_dir: Path, capsys):
    """--fields defaults.py should yield identical entry values as the default run."""
    default_data = _run([str(sample_dir)], capsys)
    fields_data = _run(["--fields", str(DEFAULTS_PLUGIN), str(sample_dir)], capsys)

    # Sort both by name for a stable comparison
    default_sorted = sorted(default_data, key=lambda e: e.get("name", ""))
    fields_sorted = sorted(fields_data, key=lambda e: e.get("name", ""))

    assert default_sorted == fields_sorted, (
        "Output with --fields defaults.py differs from the default command output.\n"
        f"Default: {json.dumps(default_sorted, indent=2)}\n"
        f"With --fields: {json.dumps(fields_sorted, indent=2)}"
    )


def test_defaults_plugin_same_output_flat_files_only(tmp_path: Path, capsys):
    """Equivalence check on a flat directory with only files (no subdirs)."""
    for name in ("alpha.py", "beta.txt", "gamma.json"):
        (tmp_path / name).write_text(name)

    default_data = _run([str(tmp_path)], capsys)
    fields_data = _run(["--fields", str(DEFAULTS_PLUGIN), str(tmp_path)], capsys)

    default_sorted = sorted(default_data, key=lambda e: e.get("name", ""))
    fields_sorted = sorted(fields_data, key=lambda e: e.get("name", ""))

    assert default_sorted == fields_sorted


def test_defaults_plugin_same_output_dirs_only(tmp_path: Path, capsys):
    """Equivalence check on a directory containing only subdirectories."""
    for name in ("aaa", "bbb", "ccc"):
        (tmp_path / name).mkdir()

    default_data = _run([str(tmp_path)], capsys)
    fields_data = _run(["--fields", str(DEFAULTS_PLUGIN), str(tmp_path)], capsys)

    default_sorted = sorted(default_data, key=lambda e: e.get("name", ""))
    fields_sorted = sorted(fields_data, key=lambda e: e.get("name", ""))

    assert default_sorted == fields_sorted


def test_defaults_plugin_same_output_with_depth(sample_dir: Path, capsys):
    """Equivalence holds when --depth is also applied."""
    default_data = _run(["--depth", "0", str(sample_dir)], capsys)
    fields_data = _run(["--fields", str(DEFAULTS_PLUGIN), "--depth", "0", str(sample_dir)], capsys)

    default_sorted = sorted(default_data, key=lambda e: e.get("name", ""))
    fields_sorted = sorted(fields_data, key=lambda e: e.get("name", ""))

    assert default_sorted == fields_sorted
