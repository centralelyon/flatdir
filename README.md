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

`--output FILE` to specify the output file:

```bash
python -m flatdir . --output flat.json
```