"""List entries in a directory and return metadata as a list of dict.

Each entry is a dict with keys: name, type, mtime, size.
"""

from __future__ import annotations

import os
import time
from pathlib import Path


def list_entries(
    root: Path,
    limit: int | None = None,
    depth: int | None = None,
    fields: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    root = root.resolve()
    for dirpath, _, filenames in os.walk(root):
        base = Path(dirpath)
        # check depth constraint
        current_depth = len(base.relative_to(root).parts)
        if depth is not None and depth >= 0 and current_depth > depth:
            continue
        for filename in filenames:
            # get metadata for file
            p = (base / filename).resolve()
            try:
                rel = p.relative_to(root)
            except ValueError:
                rel = Path(os.path.relpath(str(p), str(root)))
            st = p.stat()
            mtime = time.gmtime(st.st_mtime)
            mtime_str = time.strftime("%a, %d %b %Y %H:%M:%S GMT", mtime)
            size = int(st.st_size)

            # append entry to list with default fields
            entry: dict[str, object] = {
                "name": str(rel),
                "type": "file",
                "mtime": mtime_str,
                "size": size,
            }

            # apply custom field functions
            if fields:
                for field_name, func in fields.items():
                    entry[field_name] = func(p)

            entries.append(entry)

    # return a sorted list of entries
    entries.sort(key=lambda e: str(e["name"]))

    # apply limit if provided
    if limit is not None and limit >= 0:
        entries = entries[:limit]

    return entries
