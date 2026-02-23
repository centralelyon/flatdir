"""Load custom field functions from a user-provided Python file.

A fields file is a plain Python module where each **public** function
(i.e. whose name does not start with ``_``) is treated as a field provider.

Each function must accept a single :class:`pathlib.Path` argument (the file
being listed) and return a JSON-serialisable value. The function name becomes
the field key in the output.
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Callable

FieldFunc = Callable[[Path], object]


def load_fields_file(filepath: str) -> dict[str, FieldFunc]:
    """Import *filepath* as a module and return its public callables.

    Returns a ``{name: func}`` mapping for every public, non-class callable
    defined in the file.
    """
    path = Path(filepath).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"fields file not found: {filepath}")

    # import the file as a temporary module
    spec = importlib.util.spec_from_file_location("_flatdir_fields", str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load fields file: {filepath}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["_flatdir_fields"] = module
    spec.loader.exec_module(module)

    fields: dict[str, FieldFunc] = {}
    for name, obj in inspect.getmembers(module, callable):
        # skip private names, classes, and imported builtins
        if name.startswith("_"):
            continue
        if inspect.isclass(obj):
            continue
        # only keep functions actually defined in this file
        if getattr(obj, "__module__", None) != "_flatdir_fields":
            continue
        fields[name] = obj

    return fields
