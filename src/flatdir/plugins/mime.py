"""Plugin to extract the MIME type of a file based on its extension."""

from __future__ import annotations

import mimetypes
from pathlib import Path

# Initialize standard system mimes (reads from common OS locations)
mimetypes.init()

def mime_type(path: Path, root: Path) -> str | None:
    """Return the MIME type based on the file extension. Returns None for directories."""
    if path.is_dir():
        return None
        
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"
