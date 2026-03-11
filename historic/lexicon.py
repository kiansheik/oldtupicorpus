from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

# Compatibility wrapper so `from historic.lexicon import ...` still works while
# the canonical shared lexicon lives at historic/lexicon.tu.py.

_LEXICON_PATH = Path(__file__).with_name("lexicon.tu.py")
_MODULE_NAME = f"{__package__}._lexicon_tu" if __package__ else "_lexicon_tu"

_module = sys.modules.get(_MODULE_NAME)
if _module is None:
    spec = importlib.util.spec_from_file_location(_MODULE_NAME, _LEXICON_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load historic lexicon from {_LEXICON_PATH}")
    _module = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_NAME] = _module
    try:
        spec.loader.exec_module(_module)
    except Exception:
        sys.modules.pop(_MODULE_NAME, None)
        raise

__all__ = list(getattr(_module, "__all__", []))
if "load_lexicon" not in __all__ and hasattr(_module, "load_lexicon"):
    __all__.append("load_lexicon")

for name, value in vars(_module).items():
    if name.startswith("__") and name not in {"__all__"}:
        continue
    globals()[name] = value
