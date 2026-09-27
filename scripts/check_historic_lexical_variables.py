#!/usr/bin/env python3
"""Reject raw Pydicate lexical constructors in historic source modules."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from authoring.lexical_variables import historic_direct_lexical_constructor_calls


def main() -> int:
    findings = historic_direct_lexical_constructor_calls(ROOT / "historic")
    for finding in findings:
        print(finding.diagnostic())
    if findings:
        print(
            "Historic source modules must use shared lexical variables; "
            "declare the constructor in historic/lexicon.tu.py first.",
            file=sys.stderr,
        )
        return 1
    print("Historic source modules use named lexical variables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
