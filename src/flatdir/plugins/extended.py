"""Extended file metadata plugin covering core identity, timestamps, and security hashing.

Note: Many cloud-specific fields (e.g., bucket, cdn_url) or media fields (e.g., duration, codec)
are omitted here as they cannot be natively extracted from standard OS file properties without
external tools (like ffmpeg or API requests).
"""

from __future__ import annotations

import mimetypes
import uuid
import hashlib
import datetime
from pathlib import Path

# Initialize standard mimes
mimetypes.init()


def file_uuid(path: Path, root: Path) -> str:
    """Return a randomly generated UUID (UUID4) for the node during this mapping run."""
    return str(uuid.uuid4())


def extension(path: Path, root: Path) -> str | None:
    """Return the file extension without the dot."""
    if path.is_dir():
        return None
    ext = path.suffix
    return ext.lstrip(".") if ext else ""


def mime_type(path: Path, root: Path) -> str | None:
    """Return the MIME type based on the file extension."""
    if path.is_dir():
        return None
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def created_at(path: Path, root: Path) -> str | None:
    """Creation time in strict ISO 8601 format."""
    try:
        st = path.stat()
        # st_birthtime is available on macOS/Windows. Fallback to ctime on Linux.
        ctime = getattr(st, 'st_birthtime', st.st_ctime)
        dt = datetime.datetime.fromtimestamp(ctime, datetime.timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")
    except OSError:
        return None


def modified_at(path: Path, root: Path) -> str | None:
    """Modification time in strict ISO 8601 format."""
    try:
        st = path.stat()
        dt = datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")
    except OSError:
        return None


def sha256(path: Path, root: Path) -> str | None:
    """SHA-256 cryptographic hash of the file.
    
    Reads in 8KB chunks. Capped at reading the first 100MB to prevent the 
    directory mapper from freezing when encountering massive video files.
    """
    if path.is_dir():
        return None
        
    try:
        MAX_READ = 100 * 1024 * 1024  # 100 MB limit
        hasher = hashlib.sha256()
        read_so_far = 0
        
        with open(path, 'rb') as f:
            chunk = f.read(8192)
            while chunk and read_so_far < MAX_READ:
                hasher.update(chunk)
                read_so_far += len(chunk)
                chunk = f.read(8192)
                
        return hasher.hexdigest()
    except OSError:
        return None


def signature(path: Path, root: Path) -> str | None:
    """Alias for the SHA-256 hash checksum."""
    return sha256(path, root)


def permissions(path: Path, root: Path) -> str | None:
    """File permissions mapped in CHMOD octal format (e.g. '755', '644')."""
    try:
        st = path.stat()
        return oct(st.st_mode)[-3:]
    except OSError:
        return None


def owner_id(path: Path, root: Path) -> int | None:
    """Operating System User UID string bounding ownership."""
    try:
        return path.stat().st_uid
    except OSError:
        return None
