from __future__ import annotations

import gzip
import inspect
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from historic import primary_sources as historic_sources
from tokenizer.build_corpus_json import (
    _get_annotated,
    _get_label,
    strip_tags_to_surface,
)

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "site"
DATA_DIR = SITE_DIR / "data"
NHE_ENGA_DIR = ROOT.parent / "nhe-enga"

NODE_CHILD_ATTRS = ("principal", "verb", "noun")
NODE_LIST_ATTRS = (
    "arguments",
    "compositions",
    "pre_adjuncts",
    "post_adjuncts",
    "v_adjuncts",
    "v_adjuncts_pre",
)

NON_SEARCH_RE = re.compile(r"[^0-9A-Za-zÀ-ÿ'’\- ]+")
WHITESPACE_RE = re.compile(r"\s+")


def generated_at_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def compact_whitespace(text: str | None) -> str:
    if not text:
        return ""
    return WHITESPACE_RE.sub(" ", text).strip()


def normalize_text(text: str | None) -> str:
    compact = compact_whitespace(text)
    if not compact:
        return ""
    decomposed = unicodedata.normalize("NFD", compact.casefold())
    stripped = "".join(
        char for char in decomposed if unicodedata.category(char) != "Mn"
    )
    stripped = stripped.replace("’", "'")
    stripped = NON_SEARCH_RE.sub(" ", stripped)
    return compact_whitespace(stripped)


def split_leading_qualifiers(text: str | None) -> tuple[list[str], str]:
    remaining = compact_whitespace(text)
    qualifiers: list[str] = []
    while remaining.startswith("("):
        depth = 0
        end_index = None
        for index, char in enumerate(remaining):
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    end_index = index
                    break
        if end_index is None:
            break
        qualifiers.append(remaining[: end_index + 1].strip())
        remaining = remaining[end_index + 1 :].lstrip(" ,;:-")
    return qualifiers, compact_whitespace(remaining)


def split_glosses(text: str | None) -> list[str]:
    compact = compact_whitespace(text)
    if not compact:
        return []
    glosses = [
        compact_whitespace(part)
        for part in re.split(r"[;,]", compact)
        if compact_whitespace(part)
    ]
    return glosses or [compact]


def parse_gloss_definition(raw_definition: str | None) -> dict[str, object]:
    raw = compact_whitespace(raw_definition)
    qualifiers, remainder = split_leading_qualifiers(raw)
    glosses = split_glosses(remainder or raw)
    return {
        "raw": raw,
        "qualifiers": qualifiers,
        "glosses": glosses,
    }


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json_artifact(path: Path, payload: object) -> tuple[Path, Path]:
    ensure_directory(path.parent)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    path.write_text(text + "\n", encoding="utf-8")
    gz_path = path.with_suffix(path.suffix + ".gz")
    with gzip.open(gz_path, "wt", encoding="utf-8") as handle:
        handle.write(text)
        handle.write("\n")
    return path, gz_path


def iter_historic_sources():
    for source_name in sorted(historic_sources.__all__):
        expressions = getattr(historic_sources, source_name)
        if callable(expressions):
            expressions = expressions()
        yield source_name, expressions, "historic"


def expression_to_line_record(
    *,
    source_name: str,
    corpus_label: str,
    expression_index: int,
    expression: object,
) -> dict[str, object] | None:
    annotated = _get_annotated(expression)
    if not annotated:
        return None
    surface = _get_label(
        expression,
        annotated=annotated,
        prefer_annotated=True,
    ) or strip_tags_to_surface(annotated)
    return {
        "line_id": f"{source_name}:{expression_index}",
        "source": source_name,
        "corpus": corpus_label,
        "expression_index": expression_index,
        "surface": surface,
        "annotated": annotated,
        "normalized": normalize_text(surface),
    }


def is_expression_node(value: object) -> bool:
    if value is None or isinstance(value, (str, bytes, int, float, bool)):
        return False
    if inspect.ismethod(value) or inspect.isfunction(value) or inspect.isbuiltin(value):
        return False
    if inspect.ismodule(value):
        return False
    return hasattr(value, "__dict__")


def iter_expression_nodes(root: object) -> Iterator[object]:
    seen: set[int] = set()
    stack = [root]
    while stack:
        node = stack.pop()
        if not is_expression_node(node):
            continue
        node_id = id(node)
        if node_id in seen:
            continue
        seen.add(node_id)
        yield node
        for attr in NODE_CHILD_ATTRS:
            child = getattr(node, attr, None)
            if child is not None and child is not node:
                stack.append(child)
        for attr in NODE_LIST_ATTRS:
            children = getattr(node, attr, None)
            if isinstance(children, (list, tuple)):
                stack.extend(children)


def get_string_attr(node: object, attr: str) -> str | None:
    if not hasattr(node, attr):
        return None
    value = getattr(node, attr)
    if callable(value):
        try:
            value = value()
        except TypeError:
            return None
    if isinstance(value, str):
        compact = compact_whitespace(value)
        return compact or None
    return None


def extract_headword(node: object) -> str | None:
    for attr in ("verbete", "label", "surface"):
        value = get_string_attr(node, attr)
        if value:
            return value
    return None


def source_sort_key(line_id: str) -> tuple[str, int]:
    source_name, _, index = line_id.partition(":")
    try:
        numeric_index = int(index)
    except ValueError:
        numeric_index = 0
    return source_name, numeric_index
