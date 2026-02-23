import os
import time
from pathlib import Path

""" 
List entries in a directory and return metadata as a list of dict.
"""
def list_entries(root: Path):
    entries = []
    root = root.resolve()
    for dirpath, _, filenames in os.walk(root):
        base = Path(dirpath)
        for filename in filenames:

            # get metadata for file or folder
            p = (base / filename).resolve()
            rel = p.relative_to(root)
            st = p.stat()
            mtime = time.gmtime(st.st_mtime)
            mtime_str = time.strftime("%a, %d %b %Y %H:%M:%S GMT", mtime)
            size = int(st.st_size)

            # append entry to list
            entries.append({
                "name": str(rel),
                "type": "file",
                "mtime": mtime_str,
                "size": size,
            })

    # return a sorted list of entries
    entries.sort(key=lambda e: e["name"])
    return entries