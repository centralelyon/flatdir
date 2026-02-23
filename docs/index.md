# flatdir

`flatdir` scans a directory and generates a flat JSON file with metadata for each entry (eg file, folder).

## Installation

```bash
pip install -e .
```

or using the latest version from PyPI:

```bash
pip install flatdir
```

## Usage


```bash
# prints JSON to stdout
python -m flatdir .
```

Outputs

```json
[
    {
        "name": ".coverage",
        "type": "file",
        "mtime": "Mon, 23 Feb 2026 12:09:46 GMT",
        "size": 53248
    }
...
]
```