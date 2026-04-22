from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main
from flatdir.plugins import options
from flatdir.plugins.subfolders import subfolders
from flatdir.plugins.pattern_ids import pattern_ids


ROOT = Path(__file__).resolve().parents[1]
PATTERN_PLUGIN = ROOT / "src" / "flatdir" / "plugins" / "pattern_PRE_YR1_YR2_ID_NAME.py"
SUBFOLDERS_PLUGIN = ROOT / "src" / "flatdir" / "plugins" / "subfolders.py"
PATTERN_IDS_PLUGIN = ROOT / "src" / "flatdir" / "plugins" / "pattern_ids.py"


def test_subfolders_plugin_uses_cli_whitelist(tmp_path: Path, capsys):
    project = tmp_path / "PAr-25-26-105-Analyse"
    project.mkdir()
    for name in ["SUBFOLDER1", "SUBFOLDER2", "SUBFOLDER3", "REFS", "shared"]:
        (project / name).mkdir()

    rc = main([
        "--fields", str(PATTERN_PLUGIN),
        "--fields", str(SUBFOLDERS_PLUGIN),
        "--subfolders-whitelist", "SUBFOLDER1,SUBFOLDER2,SUBFOLDER3",
        "--only", "type=directory",
        "--only", "pattern_prefix=PAr",
        str(tmp_path),
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data) == 1
    assert data[0]["subfolders"] == ["SUBFOLDER1", "SUBFOLDER2", "SUBFOLDER3"]


def test_pattern_ids_plugin_uses_cli_separator(tmp_path: Path, capsys):
    (tmp_path / "PAr-25-26-105_106-Analyse").mkdir()

    rc = main([
        "--fields", str(PATTERN_PLUGIN),
        "--fields", str(PATTERN_IDS_PLUGIN),
        "--pattern-id-separator", "_",
        "--only", "type=directory",
        "--only", "pattern_prefix=PAr",
        str(tmp_path),
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["pattern_id"] == "105_106"
    assert data[0]["pattern_ids"] == ["105", "106"]


def test_subfolders_defaults_to_all_child_directories(tmp_path: Path):
    options.set_options()
    project = tmp_path / "project"
    project.mkdir()
    (project / "SUBFOLDER1").mkdir()
    (project / "REFS").mkdir()

    assert subfolders(project, tmp_path) == ["REFS", "SUBFOLDER1"]


def test_pattern_ids_defaults_to_hyphen_separator(tmp_path: Path):
    options.set_options()
    project = tmp_path / "PAr-25-26-105-Analyse"
    project.mkdir()

    assert pattern_ids(project, tmp_path) == ["105"]
