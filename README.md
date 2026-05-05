# flatdir

A Python library to create a flat JSON index of files and directories.

A simple example with the following directory structure:

```
├── dir_1
│   ├── file_1.txt
└── file_2.txt
```

..it generates the following flat array of dicts as a JSON file:

```
[
    {
        "name": "dir_1",
        "type": "directory",
        "path": "/"
    },
    {
        "name": "file_1.txt",
        "type": "file",
        "path": "/dir_1/"
    }, 
    {
        "name": "file_2.txt",
        "type": "file",
        "path": "/"
    }
]
````

## Installation

```bash
pip install -e .
```

Or from PyPI:

```bash
pip install flatdir
```

More examples are available at the bottom of this README.md file.

## Usage

```bash
python -m flatdir .
```

Returns a JSON file, by default with some metadata for each entry in the current directory and its subdirectories.

```json
[
    {
        "name": ".DS_Store",
        "path": ".",
        "type": "file",
        "mtime": "Mon, 23 Feb 2026 13:12:54 GMT",
        "size": 6148
    }, {
        
    }
...
]
```

Options are provided to customize the output, for instance to remove the default fields, display only files, discard system files, etc.

## Options

Use `--help` to display all available options.

`--limit N` to limit the number of entries processed:

```bash
python -m flatdir . --limit 10
```

`--depth N` to limit the depth of the directory tree:

```bash
python -m flatdir . --depth 2
```

`--output FILE` to write the result to a file (similar to `>` in bash):


```bash
python -m flatdir . --output flat.json
```

`--diff FILE` to compare the current result with a previously generated flatdir JSON file and output only added, removed, or modified entries:

```bash
python -m flatdir . --diff flat.json
```

`--fields FILE` to add custom fields via a plugin file:

```bash
python -m flatdir . --fields my_fields.py
```

The plugin file is a Python file where each public function becomes a JSON field. Each function receives the entry `Path` and the `root` directory path. Examples of fields are provided in the `src/flatdir/plugins/` directory. Below is  an example of a plugin file (return `None` to omit the field from the output):

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
        "path": ".",
        "type": "directory",
        "mtime": "Mon, 23 Feb 2026 13:12:54 GMT"
    },
    {
        "name": "README.md",
        "path": ".",
        "type": "file",
        "mtime": "Mon, 23 Feb 2026 13:12:54 GMT",
        "size": 835,
        "ext": ".md",
        "line_count": 54
    }
]
```

The default fields (`name`, `path`, `type`, `mtime`, `size`) are themselves plugins defined
in `src/flatdir/plugins/defaults.py`. Additional examples are in `src/flatdir/plugins/`.

So by default, flatdir will run the following plugins:

```
python -m flatdir . --fields src/flatdir/plugins/defaults.py
```

All options can be combined:

```bash
python -m flatdir . --depth 0 --limit 10 --fields my_fields.py --output result.json
```

Some bundled plugins accept command-line configuration. `subfolders.py` returns immediate child directories and can be filtered with `--subfolders-whitelist`; `pattern_ids.py` splits the `pattern_id` produced by `pattern_PRE_YR1_YR2_ID_NAME.py` with `--pattern-id-separator`:

```bash
python -m flatdir . \
  --fields src/flatdir/plugins/pattern_PRE_YR1_YR2_ID_NAME.py \
  --fields src/flatdir/plugins/subfolders.py \
  --fields src/flatdir/plugins/pattern_ids.py \
  --subfolders-whitelist SUBFOLDER1,SUBFOLDER2,SUBFOLDER3 \
  --pattern-id-separator _ \
  --only type=directory \
  --only pattern_prefix=PAr
```

`--ics` converts an iCalendar file to flatdir JSON. Each selected ICS component becomes one JSON entry. By default flatdir emits `VEVENT` entries; use `--ics-component NAME` to select another component, or `--ics-component ALL` to emit every component except the root `VCALENDAR`. ICS property names are preserved as JSON keys, for example `UID`, `DTSTART`, `DTEND`, `SUMMARY`, `ATTENDEE`, and nested components such as `VALARM`.

```bash
python -m flatdir calendar.ics --ics --output calendar.json
```

An `.ics` or `.ical` file path is auto-detected, so this is equivalent:

```bash
python -m flatdir calendar.ics > calendar.json
```

Example output:

```json
[
    {
        "BEGIN": "VEVENT",
        "DTSTART": "20260422T070000Z",
        "DTEND": "20260422T080000Z",
        "UID": "event-one@example.com",
        "SUMMARY": "Project review",
        "END": "VEVENT"
    }
]
```

`--exclude` to exclude entries based on a field value:

```bash
python -m flatdir . --exclude type=directory    
```

`--only` to include ONLY entries matching a field value (opposite of exclude):

```bash
python -m flatdir . --only type=file --only ext=.py
```

You can also filter by field existence by omitting the `=` sign. This is useful for plugins:

```bash
python -m flatdir . --fields my_fields.py --only line_count
```

You can also pass arrays inline formatted as `[value1,value2]` or strictly valid JSON `["value1", "value2"]`. This behaves identically to passing multiple arguments for the same field (OR logic):

```bash
python -m flatdir . --only name=["folder_A", "folder_B", "folder_C"]
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

Use the `pattern_PRE_YR1_YR2_LOW_UP.py` plugin to parse names matching a specific pattern (e.g., `ABC-19-20-aa-BB`), splitting the name into `pattern_prefix`, `pattern_year1`, `pattern_year2`, `pattern_lower`, and `pattern_upper` fields:

```bash
python -m flatdir . --fields src/flatdir/plugins/pattern_PRE_YR1_YR2_LOW_UP.py
```

You can then filter based on these extracted attributes using `--only`. For example, to only include directories that match the prefix `PCP`:

```bash
python -m flatdir . --fields src/flatdir/plugins/pattern_PRE_YR1_YR2_LOW_UP.py --only type=directory --only pattern_prefix=PCP
```

Similarly, use `pattern_PRE_YR1_YR2.py` for strictly parsing just the prefix and years (e.g., `ABC-19-20`) into `pattern_prefix`, `pattern_year1`, and `pattern_year2`:

```bash
python -m flatdir . --fields src/flatdir/plugins/pattern_PRE_YR1_YR2.py
```

To parse directory patterns combining a prefix, two years, a numeric ID and a trailing name string (e.g., `PRE-25-26-123-Text`), use the `pattern_PRE_YR1_YR2_ID_NAME.py` plugin. This maps out `pattern_prefix`, `pattern_year1`, `pattern_year2`, `pattern_id`, and `pattern_name`:

```bash
python -m flatdir . --fields src/flatdir/plugins/pattern_PRE_YR1_YR2_ID_NAME.py
```

To filter entries based on the pattern of their parent directory, use `pattern_parent_PRE_YR1_YR2.py`. This extracts `parent_pattern_prefix`, `parent_pattern_year1`, and `parent_pattern_year2`. You can combine this with the file pattern plugin to filter on both the parent's attributes and the file's own attributes simultaneously:

```bash
python -m flatdir . \
  --fields src/flatdir/plugins/pattern_parent_PRE_YR1_YR2.py \
  --fields src/flatdir/plugins/pattern_PRE_YR1_YR2_LOW_UP.py \
  --only parent_pattern_prefix=ABC \
  --only pattern_lower=aa
```

To extract an integer sequence ID and the remainder of the filename from items prefixed with numbers (like `00_intro`, `01_setup`), use `pattern_sequence_id.py`. This trims out up to 10 leading zeros and returns a natively sortable `sequence_id` integer and a `sequence_name` string:

```bash
python -m flatdir . --fields src/flatdir/plugins/pattern_sequence_id.py --sort sequence_id
```

`--parent` to include the relative path to the entry's parent directory:

```bash
python -m flatdir . --fields parent.py
```

To natively extract the MIME type of a file efficiently based on its file extension (e.g. `image/png`, `application/json`), map the `mime.py` plugin. This is extremely fast because it relies on string resolution without reading file bin data. Unknown signatures default to `application/octet-stream` and directories omit the field natively.

```bash
python -m flatdir . --fields src/flatdir/plugins/mime.py
```

To extract plain-text specific properties (such as calculating the `text_lines`, `text_words`, `text_characters`, and `text_is_blank` booleans) from text-based file formats (`.txt`, `.md`, `.json`, `.csv`, etc.), use `text.py`. It operates efficiently via an in-memory cache evaluating binaries exactly once per file:

```bash
python -m flatdir . --fields src/flatdir/plugins/text.py
```

To extract extended file system properties such as UUIDs, strict ISO 8601 timestamps, CHMOD UNIX permissions, file ownership, and securely size-limited SHA-256 cryptographic signatures, map the `extended.py` plugin:

```bash
python -m flatdir . --fields src/flatdir/plugins/extended.py
```

`--nested` to format the output as an embedded nested object structure mapping raw directory keys dynamically mirroring the underlying topological hierarchy:

```bash
python -m flatdir . --nested
```

`--tree` transforms the evaluated JSON sequence strictly into a universally standardized tree array compatible seamlessly with D3.js representations (specifically conforming to the `flare-2.json` hierarchy graph), dynamically rendering parents explicitly possessing a `children` list encompassing nested objects:

```bash
python -m flatdir . --tree
```

`--add` to inject static fields and values to every entry in the output:

```bash
python -m flatdir . --add is_checked=true --add custom_field=NA
```

`--ignore-typical` dynamically filters out extremely common developer structures ensuring highly recursive nested hidden trees prevent iteration loops (dramatically increasing mapping speed). 

Typically blocks: `.git`, `node_modules`, `__pycache__`, `.venv`, `venv`, `.idea`, `.vscode`, `*.egg-info`, `.DS_Store`, `Thumbs.db`, `*.pyc`.

```bash
python -m flatdir . --ignore-typical
```

`--add-depth` to conditionally restrict `--add` parameters exclusively to nodes situated at a specified numerical directory depth:

```bash
python -m flatdir . --add is_checked=true --add-depth 1
```

`--id` to include a unique identifier for each entry:

```bash
python -m flatdir . --id
```

`--min-depth` to strictly cut-off evaluation filtering explicitly shallower hierarchical entries out of processing:

```bash
python -m flatdir . --min-depth 2
```

`--dict-field KEY[=FILE]` to extract the value of `KEY` from a JSON `FILE` located within each traversed directory, merging it directly into the directory's resulting JSON object mapping. If the `FILE` name is omitted, it defaults to using the directory's basename (`<dirname>.json`). This is highly cache-optimized when fetching multiple keys from the same matched file.

```bash
python -m flatdir . --dict-field author=meta.json --dict-field version
```

`--include-json [FILE]` to deeply embed the completely parsed body of a JSON `FILE` located within each traversed directory. The entire file will be mounted in the JSON output specifically inside a top-level key named `"include"`.
If no file is explicitly described, it attempts to load `<dirname>.json` by default. You can also override the target key using the syntax `--include-json KEY=FILE`.

```bash
python -m flatdir . --include-json
```

`--join FILE:REMOTE_KEY[:LOCAL_KEY]` acts as a powerful relational operator (similar to a SQL LEFT JOIN). It extracts entries dynamically from a standalone local database JSON array (or dictionary) mapped by the specified arguments, and merges their inner properties natively directly to the matching dynamically generated Flatdir outputs. 

- `FILE`: Path to the standalone JSON database file (`conferences.json`). It can contain an Array or a Dictionary.
- `REMOTE_KEY`: The key to evaluate across each element within the external `FILE` (e.g `short_name`).
- `LOCAL_KEY` (optional): The dynamically generated key from the Flatdir runtime loop (defaults to `"name"`). 

When Flatdir identifies that a mapped directory evaluates `[LOCAL_KEY] == FILE[REMOTE_KEY]`, the entire matched external JSON block is natively deeply merged to the folder JSON entry safely mapping external meta-data.

```bash
# E.g matches flatdir entries where their physical basename ("name") equals conferences.json values at "short_name"
python -m flatdir . --join conferences.json:short_name

# E.g matches flatdir entries where custom mapped prop "nom_court" matches "short_name" inside the database
python -m flatdir . --join conferences.json:short_name:nom_court
```

`--no-defaults` to omit the default generated fields (`name`, `path`, `type`, `size`, `mtime`):

```bash
python -m flatdir . --no-defaults --add custom_field=NA
```

`--id` generates an auto-incrementing integer identifier perfectly corresponding horizontally sorting indexes tracking explicitly returned sequences dynamically post-evaluation. 

```bash
python -m flatdir . --id
```

`--with-headers` to wrap the dictionary inside an envelope including `headers` (execution stats) and `entries` (the actual layout payload):

```bash
python -m flatdir . --with-headers
```

The resulting JSON is:

```json
{
    "headers": {
        "root": ".",
        "count": 123456,
        "duration": 123.456,
        "timestamp": "2026-03-04T11:14:40.123456"
    },
    "entries": [
        {
            "name": "file1.txt",
            "path": "file1.txt",
            "type": "file",
            "size": 123,
            "mtime": "2026-03-04T11:14:40.123456"
        }
        ...
    ]
}
```

Additional fields can be added as plugins. See `src/flatdir/plugins` for examples. But you can also use other tools to add fields to the JSON output. For example, you can use [`ntt`](https://github.com/centralelyon/ntt) to add EXIF data to the JSON output:

```bash
!python -m flatdir . --match "\.jpg$" --depth 0 | python -m ntt enrich_exif --json -
```

## Examples of use case

- Generate a D3.js compatible JSON [hierarchical tree](https://d3js.org/d3-hierarchy/hierarchy) from the current directory and save it to a file to generate a [treemap chart](https://observablehq.com/@liris/flatdir-treemap): `python -m flatdir . --tree > flatdir.json`

- Continuous observation within your directory by using Meta's [`watchman`](https://facebook.github.io/watchman/) tool with first `watchman watch` and then trigger the rebuild script matching any pattern changes `watchman-make -p '**/*' --run 'python -m flatdir . --output index.json'`

- Validate your file inventory with [Great Expectations](https://greatexpectations.io/): generate a flat JSON index with `python -m flatdir . --output index.json`, load it as a pandas DataFrame, and define expectations on file metadata (entry count, naming conventions, allowed extensions, size thresholds, etc.) to detect structural regressions in your dataset directories. See [`examples/validate_with_great_expectations.py`](examples/validate_with_great_expectations.py) for a ready-to-run example.

## Similar or related tools

- [jq](https://jqlang.org/) - A command-line JSON processor that can be used to manipulate and query JSON data, including file metadata.
- [Nginx Autoindex](https://nginx.org/en/docs/http/ngx_http_autoindex_module.html#autoindex_format) or [Apache mode_autoindex](https://httpd.apache.org/docs/current/mod/mod_autoindex.html) - For serving static files with directory listing capabilities as JSON.
- [gron](https://github.com/tomnomnom/gron) - A command-line tool that transforms JSON into a flat, line-oriented format, making it easier to grep and manipulate with other command-line tools.
- [dasel](https://github.com/TomWright/dasel) - A command-line tool for querying and manipulating data structures like JSON, YAML, and XML, to extract file metadata.
- [jo](https://github.com/jpmens/jo) - A command-line tool for creating JSON objects, to generate JSON metadata for files and directories.
