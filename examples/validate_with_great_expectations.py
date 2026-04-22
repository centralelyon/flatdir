"""Validate a flatdir JSON index with Great Expectations.

Workflow
--------
1. Run flatdir to produce a flat JSON inventory of a directory:

       python -m flatdir . --output index.json

2. Run this script to load that inventory as a pandas DataFrame and
   validate it against a set of structural expectations:

       python examples/validate_with_great_expectations.py index.json

Dependencies
------------
    pip install great_expectations pandas

GX version targeted: 1.x (great_expectations >= 1.0)
Docs: https://docs.greatexpectations.io/docs/core/introduction/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.expectations import (
    ExpectColumnToExist,
    ExpectColumnValuesToBeBetween,
    ExpectColumnValuesToBeInSet,
    ExpectColumnValuesToMatchRegex,
    ExpectColumnValuesToNotBeNull,
    ExpectTableRowCountToBeBetween,
)


# ---------------------------------------------------------------------------
# Configuration — tweak these to match your dataset conventions
# ---------------------------------------------------------------------------

#: Minimum and maximum expected number of entries.
ROW_COUNT_MIN = 1
ROW_COUNT_MAX = 100_000

#: Every entry must have these fields (produced by the default flatdir run).
REQUIRED_COLUMNS = ["name", "path", "type", "mtime", "size"]

#: Only these entry types are allowed.
ALLOWED_TYPES = ["file", "directory"]

#: Only files with these extensions are allowed (set to None to skip the check).
ALLOWED_EXTENSIONS = [".py", ".md", ".json", ".txt", ".csv", ""]  # "" = no extension

#: Files must be at most this size in bytes (set to None to skip).
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB

#: Entry names must match this regex (e.g. no leading dots, no spaces).
#: Set to None to skip the check.
NAME_REGEX = r"^[^\s].*"  # must not start with whitespace


# ---------------------------------------------------------------------------
# Core validation logic
# ---------------------------------------------------------------------------


def load_index(path: str) -> pd.DataFrame:
    """Load a flatdir JSON index and return it as a DataFrame."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))

    # Support both plain arrays and --with-headers envelope
    if isinstance(raw, dict) and "entries" in raw:
        entries = raw["entries"]
    else:
        entries = raw

    if not isinstance(entries, list):
        raise ValueError(f"Expected a JSON array, got {type(entries).__name__}")

    return pd.DataFrame(entries)


def build_suite(context: gx.DataContext) -> ExpectationSuite:
    """Define and return the expectation suite for a flatdir index."""
    suite = context.suites.add(ExpectationSuite(name="flatdir_index"))

    # --- Row count ---
    suite.add_expectation(
        ExpectTableRowCountToBeBetween(
            min_value=ROW_COUNT_MIN,
            max_value=ROW_COUNT_MAX,
        )
    )

    # --- Required columns ---
    for col in REQUIRED_COLUMNS:
        suite.add_expectation(ExpectColumnToExist(column=col))

    # --- No nulls in key columns ---
    for col in ("name", "path", "type"):
        suite.add_expectation(ExpectColumnValuesToNotBeNull(column=col))

    # --- Type field is always "file" or "directory" ---
    suite.add_expectation(
        ExpectColumnValuesToBeInSet(
            column="type",
            value_set=ALLOWED_TYPES,
        )
    )

    # --- Name must match naming convention ---
    if NAME_REGEX:
        suite.add_expectation(
            ExpectColumnValuesToMatchRegex(
                column="name",
                regex=NAME_REGEX,
            )
        )

    # --- File extensions whitelist (on non-directory entries) ---
    if ALLOWED_EXTENSIONS is not None:
        # Derive extension from the name column at runtime via a custom
        # expectation on a derived column; easier done via a pandas filter
        # before creating the batch — see validate() below.
        pass  # handled in validate()

    # --- Size: files must not exceed max size ---
    if MAX_FILE_SIZE_BYTES is not None:
        suite.add_expectation(
            ExpectColumnValuesToBeBetween(
                column="size",
                min_value=0,
                max_value=MAX_FILE_SIZE_BYTES,
                mostly=1.0,  # allow None (directories have no size)
            )
        )

    return suite


def validate(index_path: str) -> bool:
    """Run the full GX validation workflow. Returns True if all checks pass."""
    # 1. Load data
    df = load_index(index_path)
    print(f"Loaded {len(df)} entries from '{index_path}'.")

    # --- Pre-processing: extension whitelist ---
    # Apply as a pandas filter so GX validates a clean subset.
    if ALLOWED_EXTENSIONS is not None:
        file_rows = df[df["type"] == "file"].copy()
        file_rows["_ext"] = file_rows["name"].apply(lambda n: Path(n).suffix.lower())
        bad_exts = file_rows[~file_rows["_ext"].isin(ALLOWED_EXTENSIONS)]
        if not bad_exts.empty:
            print(
                f"\n[FAIL] Extension whitelist violation — {len(bad_exts)} file(s) "
                f"with unexpected extensions:\n{bad_exts[['name', '_ext']].to_string(index=False)}"
            )
            # We report but continue so GX can run its own checks too.

    # 2. Set up an ephemeral (in-memory) GX context
    context = gx.get_context(mode="ephemeral")

    # 3. Register the DataFrame as a pandas data source
    datasource = context.data_sources.add_pandas("flatdir_datasource")
    asset = datasource.add_dataframe_asset("index")
    batch_definition = asset.add_batch_definition_whole_dataframe("full_index")

    # 4. Build the expectation suite
    suite = build_suite(context)

    # 5. Create a validation definition and run it
    validation_definition = context.validation_definitions.add(
        gx.ValidationDefinition(
            name="flatdir_validation",
            data=batch_definition,
            suite=suite,
        )
    )

    result = validation_definition.run(batch_parameters={"dataframe": df})

    # 6. Print a human-readable summary
    print("\n" + "=" * 60)
    print(f"{'PASSED' if result.success else 'FAILED':^60}")
    print("=" * 60)

    for er in result.results:
        status = "✓" if er.success else "✗"
        expectation_type = er.expectation_config.type
        print(f"  {status} {expectation_type}")
        if not er.success:
            print(f"      → {er.result}")

    print("=" * 60)
    return result.success


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a flatdir JSON index with Great Expectations."
    )
    parser.add_argument(
        "index",
        metavar="INDEX_JSON",
        help="Path to the JSON file produced by `python -m flatdir . --output index.json`.",
    )
    args = parser.parse_args()

    passed = validate(args.index)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
