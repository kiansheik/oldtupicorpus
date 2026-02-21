from __future__ import annotations

import importlib
import os

# Central registry of historic primary sources. Dynamically import each source list here
# so tests can resolve by filename stem (ground_truth/historic/<name>.txt -> <name> list).

__all__ = []

current_dir = os.path.dirname(__file__)
current_file = os.path.splitext(os.path.basename(__file__))[0]

for fname in os.listdir(current_dir):
    if fname.endswith(".py") and not fname.startswith("_"):
        mod_name = os.path.splitext(fname)[0]
        if mod_name != current_file:
            module = importlib.import_module(f"{__package__}.{mod_name}")
            if hasattr(module, mod_name):
                globals()[mod_name] = getattr(module, mod_name)
                __all__.append(mod_name)
