"""Command-line entrypoint for flatdir: print directory listing as JSON.

Usage: python -m flatdir [--limit N] [--depth N] [--output FILE] [--fields FILE]
                         [--exclude field=value ...] [--only field=value ...]
                         [--match PATTERN] [--sort FIELD] [--desc] [path]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .listing import list_entries
from .plugins_loader import load_fields_file


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

    # parse --output flag if present
    output: str | None = None
    if "--output" in argv:
        try:
            idx = argv.index("--output")
            output = argv[idx + 1]
            argv = argv[:idx] + argv[idx + 2 :]
        except (IndexError, ValueError):
            print("error: --output requires a file path argument", file=sys.stderr)
            return 1

    # parse --fields flag if present
    fields = None
    if "--fields" in argv:
        try:
            idx = argv.index("--fields")
            fields_path = argv[idx + 1]
            fields = load_fields_file(fields_path)
            argv = argv[:idx] + argv[idx + 2 :]
        except IndexError:
            print("error: --fields requires a file path argument", file=sys.stderr)
            return 1
        except (FileNotFoundError, ImportError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    # parse --exclude flags (repeatable: --exclude field=value --exclude field2=value2)
    exclude: list[tuple[str, str]] = []
    while "--exclude" in argv:
        try:
            idx = argv.index("--exclude")
            raw = argv[idx + 1]
            argv = argv[:idx] + argv[idx + 2 :]
            if "=" not in raw:
                print(
                    "error: --exclude requires field=value format",
                    file=sys.stderr,
                )
                return 1
            field_name, _, value = raw.partition("=")
            exclude.append((field_name, value))
        except IndexError:
            print("error: --exclude requires a field=value argument", file=sys.stderr)
            return 1

    # parse --only flags (repeatable: --only field=value)
    only: list[tuple[str, str]] = []
    while "--only" in argv:
        try:
            idx = argv.index("--only")
            raw = argv[idx + 1]
            argv = argv[:idx] + argv[idx + 2 :]
            if "=" not in raw:
                print(
                    "error: --only requires field=value format",
                    file=sys.stderr,
                )
                return 1
            field_name, _, value = raw.partition("=")
            only.append((field_name, value))
        except IndexError:
            print("error: --only requires a field=value argument", file=sys.stderr)
            return 1

    # parse --match flag if present
    match: str | None = None
    if "--match" in argv:
        try:
            idx = argv.index("--match")
            match = argv[idx + 1]
            argv = argv[:idx] + argv[idx + 2 :]
        except IndexError:
            print("error: --match requires a PATTERN argument", file=sys.stderr)
            return 1

    # parse --sort flag if present
    sort_by: str | None = None
    if "--sort" in argv:
        try:
            idx = argv.index("--sort")
            sort_by = argv[idx + 1]
            argv = argv[:idx] + argv[idx + 2 :]
        except IndexError:
            print("error: --sort requires a FIELD argument", file=sys.stderr)
            return 1

    # parse --desc flag if present
    sort_desc: bool = False
    if "--desc" in argv:
        idx = argv.index("--desc")
        sort_desc = True
        argv = argv[:idx] + argv[idx + 1 :]

    # check for unknown flags or too many arguments
    positionals = []
    for arg in argv:
        if arg.startswith("-"):
            print(f"error: unrecognized argument: {arg}", file=sys.stderr)
            return 1
        positionals.append(arg)
        
    if len(positionals) > 1:
        print("error: too many positional arguments", file=sys.stderr)
        return 1

    path = Path(positionals[0]) if positionals else Path(".")

    # error in case of missing path or path is not a directory
    if not path.exists() or not path.is_dir():
        print(f"path is not a directory: {path}", file=sys.stderr)
        return 2

    # generate the actual list of entries to be returned as JSON
    entries = list_entries(
        path,
        limit=limit,
        depth=depth,
        fields=fields,
        exclude=exclude or None,
        only=only or None,
        match=match,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )

    # write JSON to output file or stdout
    if output is not None:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=4)
            f.write("\n")
    else:
        json.dump(entries, sys.stdout, ensure_ascii=False, indent=4)
        _ = sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
