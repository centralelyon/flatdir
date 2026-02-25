# flatdir

A Python library to create a flat JSON index of files and directories.

## Installation

```bash
pip install -e .
```

Or from PyPI:

```bash
pip install flatdir
```

## Usage

```bash
python -m flatdir .
```

Returns a JSON file with metadata for each entry in the current directory and its subdirectories.

```json
python -m flatdir .
[
    {
        "name": ".DS_Store",
        "type": "file",
        "mtime": "Mon, 23 Feb 2026 13:12:54 GMT",
        "size": 6148
    },
...
]
```

`--limit N` to limit the number of entries processed:

```bash
python -m flatdir . --limit 10
```

`--depth N` to limit the depth of the directory tree:

```bash
python -m flatdir . --depth 2
```

`--output FILE` to write the result to a file:

```bash
python -m flatdir . --output flat.json
```

`--fields FILE` to add custom fields via a plugin file:

```bash
python -m flatdir . --fields my_fields.py
```

The plugin file is a Python file where each public function becomes a JSON field.
Each function receives the entry `Path` and the `root` directory path.
Return `None` to omit the field from the output:

```python
# my_fields.py
from pathlib import Path

def ext(path: Path, root: Path) -> str:
    return path.suffix

def line_count(path: Path, root: Path) -> int | None:
    if path.is_dir():
        return None
    return len(path.read_text().splitlines())
```

Output (both files and directories are listed):

```json
[
    {
        "name": "docs",
        "type": "directory",
        "mtime": "Mon, 23 Feb 2026 13:12:54 GMT"
    },
    {
        "name": "README.md",
        "type": "file",
        "mtime": "Mon, 23 Feb 2026 13:12:54 GMT",
        "size": 835,
        "ext": ".md",
        "line_count": 54
    }
]
```

The default fields (`name`, `type`, `mtime`, `size`) are themselves plugins defined
in `src/flatdir/plugins/defaults.py`. Additional examples are in `src/flatdir/plugins/`.

All options can be combined:

```bash
python -m flatdir . --depth 0 --limit 10 --fields my_fields.py --output result.json
```

`--exclude` to exclude entries based on a field value:

```bash
python -m flatdir . --exclude type=directory    
```

`--only` to include ONLY entries matching a field value (opposite of exclude):

```bash
python -m flatdir . --only type=file --only ext=.py
```

`--match PATTERN` to include ONLY entries whose name matches a regular expression:

```bash
python -m flatdir . --match "^ABC-\d{2}-\d{2}"
```

`--sort FIELD` to sort entries by a specific field:

```bash
python -m flatdir . --sort size
```

`--desc` to reverse the sort order (descending):

```bash
python -m flatdir . --sort size --desc
```

`--full_path` to include the absolute path of the entry:

```bash
python -m flatdir . --fields full_path.py
```

`--parent` to include the relative path to the entry's parent directory:

```bash
python -m flatdir . --fields parent.py
```

`--nested` to format the output as a nested, tree-like dictionary mirroring the directory hierarchy:

```bash
python -m flatdir . --nested
```

`--add` to inject static fields and values to every entry in the output:

```bash
python -m flatdir . --add is_checked=true --add custom_field=NA
```