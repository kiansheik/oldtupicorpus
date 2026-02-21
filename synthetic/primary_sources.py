from __future__ import annotations

from .verb_generator import build_verbs, estimate_verb_count

# Synthetic corpus list(s). Add more lists and include them in __all__ as needed.
# Keep deterministic so outputs are stable across runs.


def verb():
    return build_verbs()


verb.estimated_size = estimate_verb_count

__all__ = [
    "verb",
]
