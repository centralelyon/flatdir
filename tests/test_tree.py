"""Tests for the --tree functionality."""

import json
import subprocess
from pathlib import Path


def test_tree_outputs_children_arrays(tmp_path: Path):
    """--tree should format the JSON logically grouping parent names tying into children lists."""
    (tmp_path / "analytics").mkdir()
    (tmp_path / "analytics" / "cluster").mkdir()
    (tmp_path / "analytics" / "cluster" / "AgglomerativeCluster.py").touch()
    
    (tmp_path / "animate").mkdir()
    (tmp_path / "animate" / "Easing.py").touch()

    result = subprocess.run(
        ["python", "-m", "flatdir", str(tmp_path), "--tree"],
        capture_output=True,
        text=True,
        check=True,
    )
    
    tree = json.loads(result.stdout)
    assert tree["name"] == tmp_path.name
    
    children_names = [child["name"] for child in tree["children"]]
    assert "analytics" in children_names
    assert "animate" in children_names
    
    # Locate analytics
    analytics_node = next(child for child in tree["children"] if child["name"] == "analytics")
    assert "children" in analytics_node
    
    cluster_node = next(child for child in analytics_node["children"] if child["name"] == "cluster")
    assert "children" in cluster_node
    
    leaf_node = next(child for child in cluster_node["children"] if child["name"] == "AgglomerativeCluster.py")
    assert leaf_node["type"] == "file"
    assert "children" not in leaf_node


def test_tree_handles_base_properties_and_exclusions(tmp_path: Path):
    """--tree handles base folder properties directly and prunes empty branches."""
    (tmp_path / "base").mkdir()
    (tmp_path / "base" / "test_root.py").touch()

    result = subprocess.run(
        [
            "python", "-m", "flatdir", str(tmp_path), 
            "--tree",
            "--add", "injected_property=True"
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    
    tree = json.loads(result.stdout)
    assert tree["name"] == tmp_path.name
    
    children_names = [child["name"] for child in tree["children"]]
    assert "base" in children_names
    
    base_folder_node = next(child for child in tree["children"] if child["name"] == "base")
    assert "injected_property" in base_folder_node
    assert base_folder_node["injected_property"] is True
    
    base_file_node = next(child for child in base_folder_node["children"] if child["name"] == "test_root.py")
    assert base_file_node["injected_property"] is True
    assert "children" not in base_file_node
