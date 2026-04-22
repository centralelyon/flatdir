"""Runtime options shared by optional flatdir plugins."""

from __future__ import annotations

subfolders_whitelist: tuple[str, ...] = ()
subfolders_separator = ","
pattern_id_separator = "-"


def set_options(
    *,
    subfolders_whitelist: str | None = None,
    subfolders_separator: str = ",",
    pattern_id_separator: str = "-",
) -> None:
    globals()["subfolders_separator"] = subfolders_separator
    globals()["pattern_id_separator"] = pattern_id_separator
    globals()["subfolders_whitelist"] = split_values(
        subfolders_whitelist,
        subfolders_separator,
    )


def split_values(value: str | None, separator: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if separator == "":
        return (value.strip(),) if value.strip() else ()
    return tuple(part.strip() for part in value.split(separator) if part.strip())
