#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
compile_to_dsl.py

Best-effort compiler: canonical token stream -> annotated string -> morpheme+tag AST
-> Pydicate-ish DSL string (plus a literal fallback that always preserves
the annotated surface).

This is intentionally conservative: it prefers Tok(...) for affixes/unknown
tags, and only emits Pydicate constructors when a clear POS tag is present.
"""

from __future__ import annotations

import argparse
import code
import textwrap
import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Iterable, List, Tuple

from rawgrammarpair import (
    extract_surfaces_with_attached_tags,
    strip_tags_to_surface,
)


def load_registry_id_to_value(path: str, value_key: str) -> dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    return {it["id"]: it[value_key] for it in items}


def iter_jsonl(path: str) -> Iterable[dict]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def canonical_to_annotated(
    canon: str, mid_to_surf: dict[str, str], tid_to_tag: dict[str, str]
) -> str:
    out: list[str] = []
    for tok in canon.split():
        if tok.startswith("M"):
            out.append(mid_to_surf.get(tok, tok))
        elif tok.startswith("T"):
            out.append(tid_to_tag.get(tok, tok))
        else:
            # S subtags are derived from T; skip for annotated string
            continue
    return "".join(out)


def annotated_to_ast(annotated: str) -> list[dict]:
    ast = []
    for item in extract_surfaces_with_attached_tags(
        annotated, context_tags=set(), exclude_tag_substrings=[]
    ):
        ast.append(
            {
                "surface": item.surface,
                "tags": list(item.tags),
            }
        )
    return ast


@dataclass(frozen=True)
class TagInfo:
    raw: str
    base: str
    parts: Tuple[str, ...]


POS_PRIORITY = [
    "PROPER_NOUN",
    "INTERJECTION",
    "POSTPOSITION",
    "ADVERB",
    "CONJUNCTION",
    "DEMONSTRATIVE",
    "NUMBER",
    "NOUN",
    "VERB",
    "PRONOUN",
    "PARTICLE",
    "COPULA",
    "COMPOSITION",
]

POS_CTORS = {
    "PROPER_NOUN": "ProperNoun",
    "INTERJECTION": "Interjection",
    "POSTPOSITION": "Postposition",
    "ADVERB": "Adverb",
    "CONJUNCTION": "Conjunction",
    "DEMONSTRATIVE": "Demonstrative",
    "NUMBER": "Number",
    "NOUN": "Noun",
    "VERB": "Verb",
    "PRONOUN": "Pronoun",
    "PARTICLE": "Particle",
    "COPULA": "Copula",
    "COMPOSITION": "Composition",
}

PRONOUN_TAG_BASES = {
    "PRONOUN",
    "POSSESSIVE_PRONOUN",
    "OBJECT",
    "SUBJECT",
    "OBJECT_MARKER",
    "SUBJECT_PREFIX",
    "OBJECT_PREFIX",
}

LEXICAL_POS = {
    "PROPER_NOUN",
    "INTERJECTION",
    "POSTPOSITION",
    "ADVERB",
    "CONJUNCTION",
    "DEMONSTRATIVE",
    "NUMBER",
    "NOUN",
    "VERB",
    "PRONOUN",
    "PARTICLE",
    "COPULA",
    "COMPOSITION",
}


def _parse_tag(tag: str) -> TagInfo:
    content = tag[1:-1] if tag.startswith("[") and tag.endswith("]") else tag
    parts = tuple(p for p in content.split(":") if p)
    base = parts[0] if parts else content
    return TagInfo(raw=tag, base=base, parts=parts[1:] if len(parts) > 1 else ())


def _primary_pos(tag_infos: list[TagInfo]) -> str | None:
    bases = {ti.base for ti in tag_infos}
    for pos in POS_PRIORITY:
        if pos in bases:
            return pos
    if any(ti.base in PRONOUN_TAG_BASES for ti in tag_infos):
        return "PRONOUN"
    return None


def _tag_features(tag_infos: list[TagInfo]) -> dict:
    bases = [ti.base for ti in tag_infos]
    is_prefix = any("PREFIX" in b for b in bases)
    is_suffix = any("SUFFIX" in b for b in bases)
    is_root = any("ROOT" in b for b in bases)
    is_affix = is_prefix or is_suffix
    return {
        "bases": bases,
        "is_prefix": is_prefix,
        "is_suffix": is_suffix,
        "is_root": is_root,
        "is_affix": is_affix,
    }


def _attrs_from_tag_infos(tag_infos: list[TagInfo]) -> dict:
    attrs: dict = {}
    flags: set[str] = set()
    mood_hints: set[str] = set()
    for ti in tag_infos:
        base = ti.base
        parts = list(ti.parts)
        if base in ("SUBJECT", "SUBJECT_PREFIX") and parts:
            attrs["subject"] = parts[0]
        elif base in ("OBJECT", "OBJECT_PREFIX", "OBJECT_MARKER") and parts:
            attrs["object"] = parts[0]
        elif base == "POSSESSIVE_PRONOUN" and parts:
            attrs["possessor"] = parts[0]
        elif base == "PRONOUN":
            if parts:
                attrs["pronoun"] = parts[0]
        elif base == "PLURIFORM_PREFIX" and parts:
            attrs["pluriform"] = parts[0]
        elif base in ("NEGATION_PREFIX", "NEGATION_SUFFIX"):
            attrs["negated"] = True
        elif base in (
            "PERMISSIVE_PREFIX",
            "IMPERATIVE_PREFIX",
            "GERUNDIO",
            "CONJUNTIVO",
            "INDICATIVO",
        ):
            mood_hints.add(base)
        elif base == "POSTPOSITION" and parts:
            attrs["postposition"] = parts[0]
        elif base == "NOUN" and parts:
            attrs["noun_role"] = parts[0]
        elif base == "VOCATIVE":
            attrs["vocative"] = True

        if base not in LEXICAL_POS:
            flags.add(base)

    if mood_hints:
        attrs["mood_hints"] = sorted(mood_hints)
    if flags:
        attrs["flags"] = sorted(flags)
    return attrs


def _node_meta_from_ast(ast: list[dict]) -> list[dict]:
    meta: list[dict] = []
    for node in ast:
        tag_infos = [_parse_tag(t) for t in node["tags"]]
        pos = _primary_pos(tag_infos)
        features = _tag_features(tag_infos)
        attrs = _attrs_from_tag_infos(tag_infos)
        meta.append(
            {
                "pos": pos,
                "tag_bases": features["bases"],
                "features": features,
                "attrs": attrs,
            }
        )
    return meta


def _roots_from_nodes(ast: list[dict], meta: list[dict]) -> list[dict]:
    roots: list[dict] = []
    for i, node in enumerate(ast):
        info = meta[i]
        features = info["features"]
        pos = info["pos"]
        is_root = features["is_root"] or (
            pos in LEXICAL_POS and not features["is_affix"]
        )
        if not is_root:
            continue
        roots.append(
            {
                "index": i,
                "surface": node["surface"],
                "tags": node["tags"],
                "pos": pos,
            }
        )
    return roots


def _group_morphemes(ast: list[dict], meta: list[dict]) -> list[dict]:
    groups: list[dict] = []
    pending_prefixes: list[int] = []
    current: dict | None = None

    def _flush():
        nonlocal current
        if current is None:
            return
        idxs = current["prefixes"] + [current["root"]] + current["suffixes"]
        current["indices"] = idxs
        current["surface"] = " ".join(ast[i]["surface"] for i in idxs)
        current["tags"] = [t for i in idxs for t in ast[i]["tags"]]
        current["pos"] = meta[current["root"]]["pos"]
        groups.append(current)
        current = None

    for i, node in enumerate(ast):
        info = meta[i]
        features = info["features"]
        pos = info["pos"]
        is_affix = features["is_affix"]
        is_root = features["is_root"] or (pos in LEXICAL_POS and not is_affix)

        if is_root:
            _flush()
            current = {"prefixes": pending_prefixes, "root": i, "suffixes": []}
            pending_prefixes = []
            continue

        if is_affix and features["is_prefix"] and current is None:
            pending_prefixes.append(i)
            continue

        if current is not None:
            current["suffixes"].append(i)
            continue

        # Standalone token with no clear root; emit as its own group.
        current = {"prefixes": [], "root": i, "suffixes": []}
        _flush()

    _flush()
    return groups


def _state_trace(ast: list[dict], meta: list[dict]) -> tuple[list[dict], dict]:
    state: dict = {}
    changes: list[dict] = []

    def _apply(attrs: dict) -> dict:
        delta: dict = {}
        for key, val in attrs.items():
            if val is None:
                continue
            if key == "mood_hints":
                existing = set(state.get(key, []))
                incoming = set(val)
                if not incoming.issubset(existing):
                    merged = sorted(existing | incoming)
                    state[key] = merged
                    delta[key] = merged
                continue
            if key == "flags":
                existing = set(state.get(key, []))
                incoming = set(val)
                if not incoming.issubset(existing):
                    merged = sorted(existing | incoming)
                    state[key] = merged
                    delta[key] = merged
                continue
            if state.get(key) != val:
                state[key] = val
                delta[key] = val
        return delta

    for i, node in enumerate(ast):
        attrs = meta[i]["attrs"]
        delta = _apply(attrs)
        if delta:
            changes.append(
                {
                    "index": i,
                    "surface": node["surface"],
                    "tags": node["tags"],
                    "set": delta,
                }
            )
    return changes, state


def _code_for_ctor(ctor: str, surface: str, tag_str: str) -> str:
    if ctor == "Tok":
        return f"Tok({surface!r}, {tag_str!r})" if tag_str else f"Tok({surface!r})"
    if ctor == "Particle":
        return (
            f"Particle({surface!r}, tag={tag_str!r})"
            if tag_str
            else f"Particle({surface!r})"
        )
    # Pydicate constructors generally accept a tag kwarg; we pass it to preserve
    # the annotated surface when possible.
    return (
        f"{ctor}({surface!r}, tag={tag_str!r})" if tag_str else f"{ctor}({surface!r})"
    )


def ast_to_dsl(ast: list[dict]) -> tuple[str, str, dict]:
    """
    Build a best-effort Pydicate-ish DSL expression plus a literal fallback.
    Returns (dsl, dsl_fallback, stats).
    """
    codes: list[str] = []
    fallbacks: list[str] = []
    stats = {
        "total": 0,
        "pydicate": 0,
        "tok_fallback": 0,
        "affix_fallback": 0,
        "unknown_pos": 0,
    }

    for node in ast:
        surface = node["surface"]
        tags = node["tags"]
        tag_infos = [_parse_tag(t) for t in tags]
        tag_str = "".join(tags)
        primary = _primary_pos(tag_infos)
        features = _tag_features(tag_infos)

        ctor = "Tok"
        if primary:
            ctor = POS_CTORS.get(primary, "Tok")
        else:
            stats["unknown_pos"] += 1

        if features["is_affix"]:
            ctor = "Tok"
            stats["affix_fallback"] += 1

        code = _code_for_ctor(ctor, surface, tag_str)
        fallback = _code_for_ctor("Tok", surface, tag_str)

        codes.append(code)
        fallbacks.append(fallback)

        stats["total"] += 1
        if ctor == "Tok":
            stats["tok_fallback"] += 1
        else:
            stats["pydicate"] += 1

    dsl = f"Seq([{', '.join(codes)}])"
    dsl_fallback = f"Seq([{', '.join(fallbacks)}])"
    return dsl, dsl_fallback, stats


class DSLExplorer:
    def __init__(self, path: Path):
        self.path = Path(path)

    def _iter(self):
        return iter_jsonl(str(self.path))

    def head(self, n: int = 5) -> list[dict]:
        rows = []
        for i, row in enumerate(self._iter()):
            rows.append(row)
            if i + 1 >= n:
                break
        return rows

    def tail(self, n: int = 5) -> list[dict]:
        from collections import deque

        dq = deque(maxlen=n)
        for row in self._iter():
            dq.append(row)
        return list(dq)

    def get(self, index: int) -> dict | None:
        if index < 0:
            return None
        for i, row in enumerate(self._iter()):
            if i == index:
                return row
        return None

    def find(self, substring: str, limit: int = 5) -> list[tuple[int, dict]]:
        hits: list[tuple[int, dict]] = []
        needle = substring.lower()
        for i, row in enumerate(self._iter()):
            hay = (
                f"{row.get('input','')} {row.get('annotated','')} {row.get('surface','')}"
            ).lower()
            if needle in hay:
                hits.append((i, row))
                if len(hits) >= limit:
                    break
        return hits

    def pretty(self, row: dict, width: int = 96) -> str:
        def _wrap(label: str, value: str) -> str:
            if value is None:
                value = ""
            wrapped = textwrap.fill(
                value,
                width=width,
                subsequent_indent=" " * (len(label) + 1),
            )
            return f"{label} {wrapped}"

        parts = [
            _wrap("INPUT:", row.get("input", "")),
            _wrap("SURF :", row.get("surface", "")),
            _wrap("ANNO :", row.get("annotated", "")),
            _wrap("DSL  :", row.get("dsl", "")),
        ]
        return "\n".join(parts)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile canonical token streams into a Pydicate-style DSL."
    )
    parser.add_argument(
        "--in_jsonl",
        default="tokenizer/output/canonical_io.jsonl",
        help="Input canonical IO JSONL file.",
    )
    parser.add_argument(
        "--out_jsonl",
        default="tokenizer/output/canonical_dsl.jsonl",
        help="Output JSONL with annotated+AST+DSL.",
    )
    parser.add_argument(
        "--tokens",
        default="tokenizer/output/annotated_tokens.json",
        help="annotated_tokens.json path.",
    )
    parser.add_argument(
        "--tags",
        default="tokenizer/output/annotated_tags.json",
        help="annotated_tags.json path.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of rows for debugging.",
    )
    parser.add_argument(
        "--meta_out",
        default="tokenizer/output/canonical_dsl_meta.json",
        help="Write DSL metadata (imports, runtime hints).",
    )
    parser.add_argument(
        "--no-structure",
        action="store_true",
        help="Skip emitting structure/roots/trace metadata.",
    )
    parser.add_argument(
        "--repl",
        action="store_true",
        help="Drop into a REPL after writing outputs.",
    )
    parser.add_argument(
        "--no-repl",
        action="store_true",
        help="Do not drop into a REPL (useful for batch runs).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    root = Path(__file__).resolve().parents[1]

    in_path = Path(args.in_jsonl)
    if not in_path.is_absolute():
        in_path = root / in_path
    out_path = Path(args.out_jsonl)
    if not out_path.is_absolute():
        out_path = root / out_path
    tokens_path = Path(args.tokens)
    if not tokens_path.is_absolute():
        tokens_path = root / tokens_path
    tags_path = Path(args.tags)
    if not tags_path.is_absolute():
        tags_path = root / tags_path
    meta_path = Path(args.meta_out)
    if not meta_path.is_absolute():
        meta_path = root / meta_path

    mid_to_surf = load_registry_id_to_value(str(tokens_path), "value")
    tid_to_tag = load_registry_id_to_value(str(tags_path), "tag")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for row in iter_jsonl(str(in_path)):
            canon = row.get("output", "")
            if not canon:
                continue
            annotated = canonical_to_annotated(canon, mid_to_surf, tid_to_tag)
            ast = annotated_to_ast(annotated)
            dsl, dsl_fallback, dsl_stats = ast_to_dsl(ast)
            out_row = {
                "input": row.get("input", ""),
                "output": canon,
                "annotated": annotated,
                "surface": strip_tags_to_surface(annotated),
                "ast": ast,
                "dsl": dsl,
                "dsl_fallback": dsl_fallback,
                "dsl_stats": dsl_stats,
            }
            if not args.no_structure:
                meta = _node_meta_from_ast(ast)
                roots = _roots_from_nodes(ast, meta)
                groups = _group_morphemes(ast, meta)
                changes, final_state = _state_trace(ast, meta)
                out_row["structure"] = {
                    "nodes": meta,
                    "roots": roots,
                    "groups": groups,
                    "state_changes": changes,
                    "state_final": final_state,
                }
            f.write(json.dumps(out_row, ensure_ascii=False) + "\n")
            count += 1
            if args.limit and count >= args.limit:
                break
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "imports": [
            "from tokenizer.dsl_runtime import Seq, Tok",
            "from pydicate.lang.tupilang import *",
            "from pydicate.lang.tupilang.pos import *",
        ],
        "runtime": "tokenizer/dsl_runtime.py",
        "dsl_fields": ["dsl", "dsl_fallback", "dsl_stats"],
        "notes": [
            "dsl uses pydicate constructors when a POS tag is clear and the token is not an affix.",
            "dsl_fallback uses Tok(...) for every token to preserve exact annotated surfaces.",
            "structure includes node metadata, roots, grouped morphemes, and a light state change trace.",
        ],
    }
    with meta_path.open("w", encoding="utf-8") as meta_f:
        json.dump(meta, meta_f, ensure_ascii=False, indent=2)
    print(f"Wrote {count} rows to {out_path}.")
    if args.repl or not args.no_repl:
        explorer = DSLExplorer(out_path)
        banner = "\n".join(
            [
                "DSL REPL ready.",
                f"File: {out_path}",
                "Helpers: exp.head(n), exp.tail(n), exp.get(i), exp.find(substr), exp.pretty(row)",
                "Example: print(exp.pretty(exp.get(0)))",
            ]
        )
        code.interact(banner=banner, local={"exp": explorer})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
