"""Plugin: split the existing pattern_id field into a list."""

from __future__ import annotations

from pathlib import Path

from flatdir.plugins import options
from flatdir.plugins.pattern_PRE_YR1_YR2_ID_NAME import pattern_id


def pattern_ids(path: Path, root: Path) -> list[str] | None:
    id_string = pattern_id(path, root)
    if id_string is None:
        return None

    separator = options.pattern_id_separator
    if separator == "":
        return [id_string]

    return [part.strip() for part in id_string.split(separator) if part.strip()]
