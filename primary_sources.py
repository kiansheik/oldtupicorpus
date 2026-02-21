from __future__ import annotations

import importlib

# Compatibility aggregator for historic + synthetic primary sources.
# Prefer importing from historic.primary_sources or synthetic.primary_sources directly.

__all__ = []


def _merge_sources(module) -> None:
    names = getattr(module, "__all__", [])
    for name in names:
        if hasattr(module, name):
            globals()[name] = getattr(module, name)
            __all__.append(name)


historic_sources = importlib.import_module("historic.primary_sources")
_merge_sources(historic_sources)

try:
    synthetic_sources = importlib.import_module("synthetic.primary_sources")
except ModuleNotFoundError:
    synthetic_sources = None

if synthetic_sources is not None:
    _merge_sources(synthetic_sources)
