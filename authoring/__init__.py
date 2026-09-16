"""Human-led source authoring helpers for the Old Tupi corpus.

The package deliberately keeps corpus truth, rendering, and MCP tooling in the
repository rather than in any individual editor or AI client.
"""

from .records import GroundTruthRecord

__all__ = ["GroundTruthRecord"]
