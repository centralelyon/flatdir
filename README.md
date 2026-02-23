# flatdir

A Python library to create a flat JSON index of files and directories

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
(base) rvuillem@Romains-MacBook-Pro flatdir % python -m flatdir .
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
The function receives the file `Path` and returns a value:

```python
# my_fields.py
from pathlib import Path

def ext(p: Path) -> str:
    return p.suffix

def line_count(p: Path) -> int:
    return len(p.read_text().splitlines())
```

Output:

```json
[
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

An example extension is included in `src/flatdir/extensions/filename_length.py`.

All options can be combined:

```bash
python -m flatdir . --depth 1 --limit 10 --fields my_fields.py --output result.json
```