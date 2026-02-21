#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import primary_sources as sources


ANNOTATED_ATTRS = (
    "anotated",
    "annotated",
    "anotated_string",
    "annotated_string",
)

LABEL_ATTRS = (
    "label",
    "surface",
    "orth",
)


def _value_from_attr(obj: object, attr: str) -> Optional[str]:
    if not hasattr(obj, attr):
        return None
    value = getattr(obj, attr)
    if callable(value):
        try:
            value = value()
        except TypeError:
            return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _get_annotated(expr: object) -> Optional[str]:
    for attr in ANNOTATED_ATTRS:
        value = _value_from_attr(expr, attr)
        if value:
            return value
    eval_fn = getattr(expr, "eval", None)
    if callable(eval_fn):
        try:
            value = eval_fn(annotated=True)
        except TypeError:
            value = None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
    return None


def _get_label(expr: object) -> Optional[str]:
    for attr in LABEL_ATTRS:
        value = _value_from_attr(expr, attr)
        if value:
            return value
    eval_fn = getattr(expr, "eval", None)
    if callable(eval_fn):
        try:
            value = eval_fn(annotated=False)
        except TypeError:
            value = None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
    return None


def _iter_primary_sources() -> Iterable[tuple[str, Iterable[object]]]:
    names = getattr(sources, "__all__", [])
    for name in names:
        expressions = getattr(sources, name, None)
        if expressions is None:
            continue
        yield name, expressions


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a corpus JSON file from primary sources."
    )
    parser.add_argument(
        "--out_json",
        default="tokenizer/output/corpus.json",
        help="Path to write the corpus JSON file.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    out_path = Path(args.out_json)
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    skipped = 0
    for name, expressions in _iter_primary_sources():
        for idx, expr in enumerate(expressions):
            annotated = _get_annotated(expr)
            if not annotated:
                skipped += 1
                continue
            row: dict[str, object] = {
                "source": name,
                "index": idx,
                "anotated": annotated,
            }
            label = _get_label(expr)
            if label:
                row["label"] = label
            rows.append(row)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(rows)} rows to {out_path}.")
    if skipped:
        print(f"Skipped {skipped} expressions without annotated text.")
    if not rows:
        print("Warning: corpus is empty.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
