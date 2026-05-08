from __future__ import annotations

import gzip
import inspect
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, NamedTuple

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
ANNOTATED_CHUNK_RE = re.compile(r"([^\[]*)\[([^\]]+)\]")
DEEPEST_NODE_RE = re.compile(r"^DEEPEST_NODE_(\d+)$")


class HierarchyNode(NamedTuple):
    node_id: int
    parent_id: int | None
    depth: int
    relation: str
    kind: str
    node: object


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


def parse_annotated_chunks(annotated: str) -> list[dict[str, object]]:
    chunks: list[dict[str, object]] = []
    last_index = 0
    for match in ANNOTATED_CHUNK_RE.finditer(annotated):
        tags = [tag for tag in match.group(2).split(":") if tag]
        chunks.append({"text": match.group(1), "tags": tags})
        last_index = match.end()
    if last_index < len(annotated):
        chunks.append({"text": annotated[last_index:], "tags": []})
    return chunks


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
        "morphemes": build_annotated_morpheme_metadata(annotated, expression),
        "syntax_spans": build_annotated_syntax_spans(annotated, expression),
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


def iter_hierarchy_node_records(root: object) -> Iterator[HierarchyNode]:
    if not is_expression_node(root):
        return

    counter = 0

    def visit(
        node: object,
        *,
        parent_id: int | None,
        depth: int,
        relation: str,
        kind: str,
    ) -> Iterator[HierarchyNode]:
        nonlocal counter
        if not is_expression_node(node):
            return
        counter += 1
        node_id = counter
        yield HierarchyNode(
            node_id=node_id,
            parent_id=parent_id,
            depth=depth,
            relation=relation,
            kind=kind,
            node=node,
        )

        for child in getattr(node, "arguments", []) or []:
            yield from visit(
                child,
                parent_id=node_id,
                depth=depth + 1,
                relation="*",
                kind="argument",
            )
        for child in getattr(node, "pre_adjuncts", []) or []:
            yield from visit(
                child,
                parent_id=node_id,
                depth=depth + 1,
                relation="+",
                kind="pre_adjunct",
            )
        for child in getattr(node, "post_adjuncts", []) or []:
            yield from visit(
                child,
                parent_id=node_id,
                depth=depth + 1,
                relation="+",
                kind="post_adjunct",
            )

    yield from visit(root, parent_id=None, depth=0, relation="-", kind="root")


def iter_hierarchical_nodes(root: object) -> Iterator[object]:
    for record in iter_hierarchy_node_records(root):
        yield record.node


def build_hierarchy_node_lookup(expression: object) -> dict[int, dict[str, object]]:
    lookup: dict[int, dict[str, object]] = {}
    for record in iter_hierarchy_node_records(expression):
        definition_raw = get_string_attr(record.node, "definition")
        lookup[record.node_id] = {
            "node_id": record.node_id,
            "parent_id": record.parent_id,
            "depth": record.depth,
            "relation": record.relation,
            "kind": record.kind,
            "headword": extract_headword(record.node),
            "definition": (
                parse_gloss_definition(definition_raw) if definition_raw else None
            ),
        }
    return lookup


def build_annotated_morpheme_metadata(
    annotated: str, expression: object
) -> list[dict[str, object]]:
    node_lookup = build_hierarchy_node_lookup(expression)

    morphemes: list[dict[str, object]] = []
    for chunk in parse_annotated_chunks(annotated):
        tags = chunk["tags"]
        if not tags:
            continue

        deepest_node_id = None
        for tag in tags:
            match = DEEPEST_NODE_RE.match(tag)
            if match:
                deepest_node_id = int(match.group(1))
                break

        node_meta = node_lookup.get(deepest_node_id or -1, {})
        morphemes.append(
            {
                "deepest_node_id": deepest_node_id,
                "headword": node_meta.get("headword"),
                "definition": node_meta.get("definition"),
            }
        )

    return morphemes


def _is_contiguous(indices: list[int]) -> bool:
    return bool(indices) and indices == list(range(indices[0], indices[-1] + 1))


def build_annotated_syntax_spans(
    annotated: str, expression: object
) -> list[dict[str, object]]:
    node_lookup = build_hierarchy_node_lookup(expression)
    if not node_lookup:
        return []

    children_by_parent: dict[int | None, list[int]] = {}
    for node_id, node_meta in node_lookup.items():
        parent_id = node_meta["parent_id"]
        children_by_parent.setdefault(parent_id, []).append(node_id)

    descendants_cache: dict[int, set[int]] = {}

    def descendants(node_id: int) -> set[int]:
        if node_id in descendants_cache:
            return descendants_cache[node_id]
        output = {node_id}
        for child_id in children_by_parent.get(node_id, []):
            output.update(descendants(child_id))
        descendants_cache[node_id] = output
        return output

    deepest_by_morpheme: list[int | None] = []
    for chunk in parse_annotated_chunks(annotated):
        tags = chunk["tags"]
        if not tags:
            continue

        deepest_node_id = None
        for tag in tags:
            match = DEEPEST_NODE_RE.match(tag)
            if match:
                deepest_node_id = int(match.group(1))
                break
        deepest_by_morpheme.append(deepest_node_id)

    morpheme_count = len(deepest_by_morpheme)
    if morpheme_count < 2:
        return []

    spans: list[dict[str, object]] = []
    seen_ranges: set[tuple[int, int]] = set()

    def add_span(
        *,
        node_id: int,
        indices: list[int],
        span_kind: str,
    ) -> None:
        if len(indices) < 2:
            return
        indices = sorted(indices)
        if not _is_contiguous(indices):
            return
        start = indices[0]
        end = indices[-1]
        if start == 0 and end == morpheme_count - 1:
            return
        range_key = (start, end)
        if range_key in seen_ranges:
            return
        seen_ranges.add(range_key)

        node_meta = node_lookup[node_id]
        spans.append(
            {
                "node_id": node_id,
                "parent_id": node_meta["parent_id"],
                "depth": node_meta["depth"],
                "relation": node_meta["relation"],
                "kind": node_meta["kind"],
                "span_kind": span_kind,
                "label": node_meta["headword"],
                "start": start,
                "end": end,
            }
        )

    for node_id in sorted(node_lookup):
        own_indices = [
            index
            for index, deepest_node_id in enumerate(deepest_by_morpheme)
            if deepest_node_id == node_id
        ]
        add_span(node_id=node_id, indices=own_indices, span_kind="node")

        subtree_ids = descendants(node_id)
        subtree_indices = [
            index
            for index, deepest_node_id in enumerate(deepest_by_morpheme)
            if deepest_node_id in subtree_ids
        ]
        add_span(node_id=node_id, indices=subtree_indices, span_kind="subtree")

    spans.sort(
        key=lambda span: (
            int(span["end"]) - int(span["start"]),
            -int(span["depth"]),
            int(span["start"]),
            int(span["node_id"]),
        )
    )
    return spans


def source_sort_key(line_id: str) -> tuple[str, int]:
    source_name, _, index = line_id.partition(":")
    try:
        numeric_index = int(index)
    except ValueError:
        numeric_index = 0
    return source_name, numeric_index
