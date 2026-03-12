from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

# Central registry of historic primary sources. Load each source module by path so
# historic/*.tu.py files work the same way legacy *.py files did.

__all__ = []

CURRENT_DIR = Path(__file__).resolve().parent
SUPPORT_FILES = {
    "__init__.py",
    "lexicon.py",
    "lexicon.tu.py",
    "primary_sources.py",
}


def _source_name(path: Path) -> str | None:
    if path.name in SUPPORT_FILES or path.name.startswith("_") or not path.is_file():
        return None
    if path.name.endswith(".tu.py"):
        return path.name[: -len(".tu.py")]
    if path.suffix == ".py":
        return path.stem
    return None


def _module_name(source_name: str) -> str:
    return f"{__package__}._source_{source_name}"


def _load_module(path: Path, source_name: str):
    module_name = _module_name(source_name)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load historic source module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


source_paths: dict[str, Path] = {}
for path in sorted(CURRENT_DIR.iterdir()):
    source_name = _source_name(path)
    if source_name is None:
        continue
    existing = source_paths.get(source_name)
    if existing is None or path.name.endswith(".tu.py"):
        source_paths[source_name] = path

for source_name in sorted(source_paths):
    module = _load_module(source_paths[source_name], source_name)
    if hasattr(module, source_name):
        globals()[source_name] = getattr(module, source_name)
        __all__.append(source_name)
