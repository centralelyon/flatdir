"""Command-line entrypoint for flatdir: print directory listing as JSON.

Usage: python -m flatdir [--limit N] [--depth N] [path]
"""

import json
import sys
from pathlib import Path

from .listing import list_entries


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    # parse --limit flag if present
    limit: int | None = None
    if "--limit" in argv:
        try:
            idx = argv.index("--limit")
            limit = int(argv[idx + 1])
            argv = argv[:idx] + argv[idx + 2 :]
        except (IndexError, ValueError):
            print("error: --limit requires a valid integer argument", file=sys.stderr)
            return 1

    # parse --depth flag if present
    depth: int | None = None
    if "--depth" in argv:
        try:
            idx = argv.index("--depth")
            depth = int(argv[idx + 1])
            argv = argv[:idx] + argv[idx + 2 :]
        except (IndexError, ValueError):
            print("error: --depth requires a valid integer argument", file=sys.stderr)
            return 1

    path = Path(argv[0]) if argv else Path(".")

    # error in case of missing path or path is not a directory
    if not path.exists() or not path.is_dir():
        print(f"path is not a directory: {path}", file=sys.stderr)
        return 2

    # generate the actual list of entries to be returned as JSON
    entries = list_entries(path, limit=limit, depth=depth)

    # returns an indented JSON list of entries to stdout
    json.dump(entries, sys.stdout, ensure_ascii=False, indent=4)
    _ = sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
