from __future__ import annotations
import os
import importlib

# Central registry of primary sources. Dynamically import each source list here so tests
# can resolve by filename stem (ground_truth/<name>.txt -> <name> list).

__all__ = []

current_dir = os.path.dirname(__file__)
current_file = os.path.splitext(os.path.basename(__file__))[0]

for fname in os.listdir(current_dir):
    if fname.endswith(".py") and not fname.startswith("_"):
        mod_name = os.path.splitext(fname)[0]
        if mod_name != current_file:
            # Import sibling modules when this file is loaded as a top-level module.
            module = importlib.import_module(mod_name)
            if hasattr(module, mod_name):
                globals()[mod_name] = getattr(module, mod_name)
                __all__.append(mod_name)
