"""List entries in a directory and return metadata as a list of dict.

Each entry is a dict with keys determined by field plugins (defaults: name, type, mtime, size).
"""

from __future__ import annotations

import functools
import json
import os
import re
from pathlib import Path

from .plugins import defaults as _defaults
from .plugins_loader import load_fields_file

# built-in default fields, loaded once
DEFAULT_FIELDS = load_fields_file(_defaults.__file__)

IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".idea", ".vscode", ".ipynb_checkpoints", ".pytest_cache", ".ruff_cache"}
IGNORE_FILES = {".DS_Store", "Thumbs.db"}


def list_entries(
    root: Path,
    limit: int | None = None,
    depth: int | None = None,
    min_depth: int | None = None,
    add_depth: int | None = None,
    fields: dict[str, object] | None = None,
    exclude: list[tuple[str, str]] | None = None,
    only: list[tuple[str, str]] | None = None,
    add_fields: dict[str, object] | None = None,
    dict_fields: list[tuple[str, str | None]] | None = None,
    include_jsons: list[tuple[str, str | None]] | None = None,
    joins: list[tuple[str, str, str]] | None = None,
    match: str | None = None,
    sort_by: str | None = None,
    sort_desc: bool = False,
    ignore_typical: bool = False,
    use_defaults: bool = True,
) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    root = root.resolve()

    # merge default fields with custom fields (custom can override defaults)
    all_fields = dict(DEFAULT_FIELDS) if use_defaults else {}
    if fields:
        all_fields.update(fields)

    # compile regex pattern if match is provided
    pattern = None
    if match:
        pattern = re.compile(match)

    for dirpath, dirnames, filenames in os.walk(root):
        base = Path(dirpath)
        # check depth constraint
        current_depth = len(base.relative_to(root).parts)
        if depth is not None and depth >= 0 and current_depth > depth:
            continue

        if ignore_typical:
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.endswith(".egg-info")]
            filenames = [f for f in filenames if f not in IGNORE_FILES and not f.endswith(".pyc")]

        # list subdirectories at this level
        for dirname in dirnames:
            p = (base / dirname).resolve()
            entry: dict[str, object] = {}
            for field_name, func in all_fields.items():
                value = func(p, root)
                if value is not None:
                    entry[field_name] = value
                    
            # Extract dict-fields if requested
            if dict_fields:
                _apply_dict_fields(entry, p, dict_fields)
            
            # Embed full json payloads if requested
            if include_jsons:
                _apply_include_jsons(entry, p, include_jsons)
                
            item_depth = current_depth + 1
            if add_fields and (add_depth is None or item_depth == add_depth):
                entry.update(add_fields)
                
            # Apply external JSON joins if requested
            if joins:
                _apply_joins(entry, joins)
            if _excluded(entry, exclude, p, root) or not _included(entry, only, p, root) or not _matched(entry, pattern, p, root):
                continue
            
            if min_depth is not None and min_depth > 0 and item_depth < min_depth:
                continue
                
            entries.append(entry)

        # list files at this level
        for filename in filenames:
            p = (base / filename).resolve()
            entry = {}
            for field_name, func in all_fields.items():
                value = func(p, root)
                if value is not None:
                    entry[field_name] = value
                    
            item_depth = current_depth + 1
            if add_fields and (add_depth is None or item_depth == add_depth):
                entry.update(add_fields)
                
            if joins:
                _apply_joins(entry, joins)
            if _excluded(entry, exclude, p, root) or not _included(entry, only, p, root) or not _matched(entry, pattern, p, root):
                continue

            if min_depth is not None and min_depth > 0 and item_depth < min_depth:
                continue

            entries.append(entry)

    # return a sorted list of entries
    sort_field = sort_by if sort_by else "name"

    def _get_sort_key(entry: dict[str, object]) -> tuple[int, object]:
        val = entry.get(sort_field)
        if val is None:
            return (0, "")
        if isinstance(val, (int, float)):
            return (1, val)
        return (2, str(val).lower())

    entries.sort(key=_get_sort_key, reverse=sort_desc)

    # apply limit if provided
    if limit is not None and limit >= 0:
        entries = entries[:limit]

    return entries


@functools.lru_cache(maxsize=1024)
def _read_json_file(json_path: Path) -> object:
    if not json_path.is_file():
        return None
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        pass
    return None


def _apply_dict_fields(
    entry: dict[str, object], 
    directory_path: Path, 
    dict_fields: list[tuple[str, str | None]]
) -> None:
    """Read dict_fields logic and apply standard modifications for matching directory values."""
    node_name = str(entry.get("name", directory_path.name))

    for key, custom_filename in dict_fields:
        target_file = custom_filename if custom_filename else f"{node_name}.json"
        json_path = directory_path / target_file
        
        file_data = _read_json_file(json_path)
        if isinstance(file_data, dict) and key in file_data:
            entry[key] = file_data[key]


def _apply_include_jsons(
    entry: dict[str, object], 
    directory_path: Path, 
    include_jsons: list[tuple[str, str | None]]
) -> None:
    """Read full files and embed their entire parsed JSON dictionary under target key."""
    node_name = str(entry.get("name", directory_path.name))

    for key, custom_filename in include_jsons:
        target_file = custom_filename if custom_filename else f"{node_name}.json"
        json_path = directory_path / target_file
        
        file_data = _read_json_file(json_path)
        # If the file exists and is valid json, we inject the whole parsed object (list, dict, string...)
        if file_data is not None: 
            entry[key] = file_data


def _apply_joins(
    entry: dict[str, object], 
    joins: list[tuple[str, str, str]]
) -> None:
    """Enrich the entry with matching properties from an external JSON database file."""
    for filename, remote_key, local_key in joins:
        local_val = entry.get(local_key)
        if local_val is None:
            continue
            
        json_path = Path(filename).resolve()
        db_data = _read_json_file(json_path)
        
        if isinstance(db_data, list):
            for obj in db_data:
                if isinstance(obj, dict) and obj.get(remote_key) is not None and str(obj.get(remote_key)) == str(local_val):
                    for k, v in obj.items():
                        if k != remote_key:
                            entry[k] = v
                    break
        elif isinstance(db_data, dict):
            if db_data.get(remote_key) is not None and str(db_data.get(remote_key)) == str(local_val):
                for k, v in db_data.items():
                    if k != remote_key:
                        entry[k] = v


def _excluded(entry: dict[str, object], exclude: list[tuple[str, str]] | None, p: Path, root: Path) -> bool:
    """Return True if *entry* matches any of the exclude rules."""
    if not exclude:
        return False
    for field_name, value in exclude:
        entry_val = entry.get(field_name)
        if entry_val is None and field_name in _defaults.__dict__:
            func = getattr(_defaults, field_name)
            if callable(func):
                entry_val = func(p, root)
        if str(entry_val if entry_val is not None else "") == value:
            return True
    return False


def _included(entry: dict[str, object], only: list[tuple[str, str]] | None, p: Path, root: Path) -> bool:
    """Return True if *entry* matches the inclusive rules.
    If multiple fields are provided, it must match ALL fields (AND logic).
    If multiple values are provided for the same field, it must match ANY of them (OR logic).
    """
    if not only:
        return True
    
    # group by field
    required: dict[str, set[str]] = {}
    for f, v in only:
        required.setdefault(f, set()).add(v)
        
    for f, values in required.items():
        entry_val = entry.get(f)
        if entry_val is None and f in _defaults.__dict__:
            func = getattr(_defaults, f)
            if callable(func):
                entry_val = func(p, root)
        if str(entry_val if entry_val is not None else "") not in values:
            return False
            
    return True


def _matched(entry: dict[str, object], pattern: re.Pattern[str] | None, p: Path, root: Path) -> bool:
    """Return True if *entry* name matches the given regex pattern."""
    if pattern is None:
        return True
    name_val = entry.get("name")
    if name_val is None:
        name_val = _defaults.name(p, root)
    return pattern.search(str(name_val)) is not None
