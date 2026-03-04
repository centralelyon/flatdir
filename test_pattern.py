from pathlib import Path

def name(path: Path, root: Path) -> str:
    # return the name without '01_' prefix
    return path.name.split("_", 1)[-1]
