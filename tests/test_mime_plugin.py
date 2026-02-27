from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main

def test_mime_plugin(tmp_path: Path, capsys):
    (tmp_path / "image.png").write_text("fake png")
    (tmp_path / "script.js").write_text("console.log('test');")
    (tmp_path / "unknown.xyz123").write_text("binary data")
    (tmp_path / "folder").mkdir()
    
    # Run flatdir with the new mime plugin
    code = main([
        str(tmp_path),
        "--fields", "src/flatdir/plugins/mime.py",
        "--sort", "name"
    ])
    
    assert code == 0
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    assert len(data) == 4
    
    folder = next(d for d in data if d["name"] == "folder")
    png = next(d for d in data if d["name"] == "image.png")
    js = next(d for d in data if d["name"] == "script.js")
    unknown = next(d for d in data if d["name"] == "unknown.xyz123")
    
    assert "mime_type" not in folder  # Directories return None
    assert png["mime_type"] == "image/png"
    assert js["mime_type"] in ("application/javascript", "text/javascript") # specific matching depends on OS mimetypes library registry
    assert unknown["mime_type"] == "application/octet-stream"
