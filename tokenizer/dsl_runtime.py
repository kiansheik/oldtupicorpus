#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lightweight runtime helpers for canonical_dsl output.

This keeps the DSL executable without forcing a full pydicate parse.
You can mix Tok() with pydicate predicates inside Seq().
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Any


@dataclass(frozen=True)
class Tok:
    surface: str
    tag: str = ""

    def eval(self, annotated: bool = False) -> str:
        return f"{self.surface}{self.tag if annotated else ''}"


def _eval_item(item: Any, annotated: bool) -> str:
    if hasattr(item, "eval"):
        return item.eval(annotated=annotated)
    return str(item)


@dataclass
class Seq:
    items: Iterable[Any]

    def eval(self, annotated: bool = False) -> str:
        parts = [_eval_item(x, annotated) for x in self.items]
        return " ".join(p for p in parts if p).strip()

    def __str__(self) -> str:
        return self.eval(annotated=False)
