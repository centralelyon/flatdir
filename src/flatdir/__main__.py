"""Command-line entrypoint for flatdir: print directory listing as JSON.

Usage: python -m flatdir [OPTIONS] [path]

Options:
  --limit N                  Limit the number of entries returned to N.
  --depth N                  Limit the directory traversal depth to max N.
  --min-depth N              Filter out objects positioned shallower than depth N.
  --output FILE              Write the JSON output to FILE instead of stdout.
  --fields FILE              Path to a python file defining custom formatting.
  --exclude field=value      Exclude objects precisely matching boolean parameters.
  --only field=value         Mandate object mapping fields validating correctly.
  --add field=value          Inject static metadata values sequentially across arrays.
  --add-depth N              Conditionally restrict --add parameters only to this tree depth.
  --match PATTERN            Apply regex validation pattern filters across filename nodes.
  --sort FIELD               Configure topological sequence ordering mapped by parameter.
  --desc                     Invert topological JSON indexing sequentially backwards.
  --nested                   Build hierarchal topological directory map nodes dynamically.
  --ignore-typical           Omit standard dev environments natively (like .git, .venv).
  --no-defaults              Omit default fields (type, size, mtime) but preserve name.
  --id                       Inject an auto-incrementing integer sequence post-sorting.
  --with-headers             Envelope the JSON payload mapping runtime stats arrays.
  --help, -h                 Show this help menu and exit.

path Defaults to the current directory '.'
"""

from __future__ import annotations

import json
import sys
import time
import datetime
from pathlib import Path

from .listing import list_entries
from .plugins_loader import load_fields_file


def main(argv: list[str] | None = None) -> int:
    start_time = time.time()
    argv = argv if argv is not None else sys.argv[1:]

    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0

    original_argv = list(argv)
    
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

    # parse --min-depth flag if present
    min_depth: int | None = None
    if "--min-depth" in argv:
        try:
            idx = argv.index("--min-depth")
            min_depth = int(argv[idx + 1])
            argv = argv[:idx] + argv[idx + 2 :]
        except (IndexError, ValueError):
            print("error: --min-depth requires a valid integer argument", file=sys.stderr)
            return 1

    # parse --add-depth flag if present
    add_depth: int | None = None
    if "--add-depth" in argv:
        try:
            idx = argv.index("--add-depth")
            add_depth = int(argv[idx + 1])
            argv = argv[:idx] + argv[idx + 2 :]
        except (IndexError, ValueError):
            print("error: --add-depth requires a valid integer argument", file=sys.stderr)
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

    # parse --add flags (repeatable: --add field=value)
    add_fields: dict[str, object] = {}
    while "--add" in argv:
        try:
            idx = argv.index("--add")
            raw = argv[idx + 1]
            argv = argv[:idx] + argv[idx + 2 :]
            if "=" not in raw:
                print(
                    "error: --add requires field=value format",
                    file=sys.stderr,
                )
                return 1
            field_name, _, value = raw.partition("=")
            add_fields[field_name] = _parse_value(value)
        except IndexError:
            print("error: --add requires a field=value argument", file=sys.stderr)
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

    # parse --nested flag if present
    nested: bool = False
    if "--nested" in argv:
        idx = argv.index("--nested")
        nested = True
        argv = argv[:idx] + argv[idx + 1 :]

    # parse --ignore-typical flag if present
    ignore_typical: bool = False
    if "--ignore-typical" in argv:
        idx = argv.index("--ignore-typical")
        ignore_typical = True
        argv = argv[:idx] + argv[idx + 1 :]

    # parse --no-defaults flag if present
    no_defaults: bool = False
    if "--no-defaults" in argv:
        idx = argv.index("--no-defaults")
        no_defaults = True
        argv = argv[:idx] + argv[idx + 1 :]

    # parse --id flag if present
    auto_id: bool = False
    if "--id" in argv:
        idx = argv.index("--id")
        auto_id = True
        argv = argv[:idx] + argv[idx + 1 :]

    # parse --with-headers flag if present
    with_headers: bool = False
    if "--with-headers" in argv:
        idx = argv.index("--with-headers")
        with_headers = True
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

    if no_defaults and (fields is None or "name" not in fields):
        from .plugins import defaults as _defaults
        if fields is None:
            fields = {}
        fields["name"] = _defaults.name

    # generate the actual list of entries to be returned as JSON
    entries = list_entries(
        path,
        limit=limit,
        depth=depth,
        min_depth=min_depth,
        add_depth=add_depth,
        fields=fields,
        exclude=exclude or None,
        only=only or None,
        add_fields=add_fields or None,
        match=match,
        sort_by=sort_by,
        sort_desc=sort_desc,
        ignore_typical=ignore_typical,
        use_defaults=not no_defaults,
    )

    if auto_id:
        for index, entry in enumerate(entries, start=1):
            entry["id"] = index

    out_data: object = entries
    if nested:
        out_data = _build_nested(entries)

    if with_headers:
        headers = {
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "execution_time_seconds": round(time.time() - start_time, 4),
            "command": "python -m flatdir " + " ".join(original_argv),
            "entries_count": len(entries)
        }
        out_data = {
            "headers": headers,
            "entries": out_data
        }

    # write JSON to output file or stdout
    if output is not None:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(out_data, f, ensure_ascii=False, indent=4)
            f.write("\n")
    else:
        json.dump(out_data, sys.stdout, ensure_ascii=False, indent=4)
        _ = sys.stdout.write("\n")
    return 0


def _build_nested(entries: list[dict[str, object]]) -> dict[str, object]:
    """Convert a flat list of entries into a nested dictionary based on 'name'."""
    nested_dict: dict[str, object] = {}
    for entry in entries:
        name_val = entry.get("name")
        if not isinstance(name_val, str):
            continue
            
        parts = Path(name_val).parts
        if not parts:
            continue
            
        current: dict[str, object] = nested_dict
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                current[part] = {}
            current = current[part] # type: ignore
            
        last_part = parts[-1]
        entry_data = {k: v for k, v in entry.items() if k != "name"}
        
        if last_part not in current:
            current[last_part] = entry_data
        else:
            existing = current[last_part]
            if isinstance(existing, dict):
                existing.update(entry_data)
            else:
                current[last_part] = entry_data
                
    return nested_dict


def _parse_value(value: str) -> object:
    """Parse string value into correct python type (bool, int, float, str)."""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() == "null":
        return None
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


if __name__ == "__main__":
    raise SystemExit(main())
