"""Plugin: extracts a sequence_id from a prefix like 00_ or 01_.

Provides field: sequence_id.
"""

from __future__ import annotations

import re
from pathlib import Path

_cache: dict[Path, int | None] = {}


def sequence_id(path: Path, root: Path) -> int | None:
    """Return the sequence ID parsed from the beginning of the name (e.g. 01_ -> 1).
    
    Supports up to 10 zero left padding.
    """
    if path in _cache:
        return _cache[path]
        
    match = re.search(r'^([0-9]+)_', path.name)
    if not match:
        _cache[path] = None
        return None
        
    raw_str = match.group(1)
    
    # Calculate number of leading zeros
    if raw_str == '0' * len(raw_str):
        # e.g., "00" has 1 leading zero before the actual "0" value
        leading_zeros = max(0, len(raw_str) - 1)
    else:
        leading_zeros = len(raw_str) - len(raw_str.lstrip('0'))
        
    if leading_zeros > 10:
        _cache[path] = None
        return None
        
    res = int(raw_str)
    _cache[path] = res
    return res
