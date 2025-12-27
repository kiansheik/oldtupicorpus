from __future__ import annotations

# Central registry of primary sources. Import each source list here so tests
# can resolve by filename stem (ground_truth/<name>.txt -> <name> list).

from bettendorff_compendio import bettendorff_compendio

__all__ = [
    "bettendorff_compendio",
]
