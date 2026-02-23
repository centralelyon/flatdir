"""List entries in a directory and return metadata as a list of dict.

Each entry is a dict with keys: name, type, mtime, size.
"""

import os
import time
from pathlib import Path


def list_entries(root: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    root = root.resolve()
    for dirpath, _, filenames in os.walk(root):
        base = Path(dirpath)
        for filename in filenames:
            # get metadata for file
            p = (base / filename).resolve()
            rel = p.relative_to(root)
            st = p.stat()
            mtime = time.gmtime(st.st_mtime)
            mtime_str = time.strftime("%a, %d %b %Y %H:%M:%S GMT", mtime)
            size = int(st.st_size)

            # append entry to list
            entries.append(
                {
                    "name": str(rel),
                    "type": "file",
                    "mtime": mtime_str,
                    "size": size,
                }
            )

    # return a sorted list of entries
    entries.sort(key=lambda e: str(e["name"]))
    return entries
