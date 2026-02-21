#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
build_token_tag_registry_and_io.py

Extends the previous script by additionally generating:
1) Full input/output training data (JSONL):
   - input  : surface/orthographic string (row["label"] or row["surface"] or fallback)
   - output : canonical token stream using stable IDs for:
              - morphemes (M######)
              - full tags (T######)
              - sub-tags (S######) derived by splitting tag contents on ":" (more richness)

2) Stable registries (JSON):
   - annotated_tags.json         : full bracket tags -> T######
   - annotated_subtags.json      : subtags (split on ":") -> S######
   - annotated_tokens.json       : surface morphemes -> M######
   - annotated_token_pairs.json  : unique (value, tag) list (like before)

Assumptions:
- Input JSON contains list of objects with at least "anotated".
- Surface input for training is taken from:
    row["label"] (preferred) or row["surface"] or row["orth"] or fallback to the annotated string stripped of tags.
- Tags like [MAIN_VERB] and [SUB_VERB] are ignored if unattached (i.e., appear with no adjacent surface).
"""

import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple


TAG_RE = re.compile(r"^\[.*\]$")
UNITS_RE = re.compile(r"\[.*?\]|[^\s\[\]]+")

DEFAULT_EXCLUDE_TAG_SUBSTRINGS = [
    "DIRECT",
    "ROOT",
]

DEFAULT_CONTEXT_TAGS = {
    "[MAIN_VERB]",
    "[SUB_VERB]",
}


def is_tag(tok: str) -> bool:
    return bool(TAG_RE.match(tok))


def tokenize_annotated_string(s: str) -> List[str]:
    return UNITS_RE.findall(s)


def strip_tags_to_surface(s: str) -> str:
    # Remove bracket tags, collapse spaces
    s2 = re.sub(r"\[.*?\]", " ", s)
    s2 = re.sub(r"\s+", " ", s2).strip()
    return s2


def should_exclude_tag(tag: str, exclude_tag_substrings: Iterable[str]) -> bool:
    return any(sub in tag for sub in exclude_tag_substrings)


def tag_to_subparts(tag: str) -> List[str]:
    """
    "[SUBJECT:2pp:OBJECT_1P]" -> ["SUBJECT", "2pp", "OBJECT_1P"]
    "[MAIN_VERB]" -> ["MAIN_VERB"]
    """
    inner = tag.strip()[1:-1]  # remove [ ]
    # empty safety
    if not inner:
        return []
    return [p for p in inner.split(":") if p]


@dataclass(frozen=True)
class SurfaceWithTags:
    surface: str
    tags: Tuple[str, ...]  # full tags like "[OBJECT:1ps]"


def extract_surfaces_with_attached_tags(
    annotated: str,
    *,
    context_tags: Set[str],
    exclude_tag_substrings: Iterable[str],
) -> List[SurfaceWithTags]:
    """
    Returns an ordered list of surfaces, each with 0..N attached full tags.

    Attachment rules:
    - Tags before a surface attach to the next surface (prefix).
    - Tags after a surface attach to the previous surface (suffix).
    - Excluded tags are removed.
    - Unattached tags at the end are dropped (including context tags).
    - Context tags in the middle are only preserved if they attach to a surface (adjacent).
    """
    units = tokenize_annotated_string(annotated)
    out: List[SurfaceWithTags] = []

    pending_prefix_tags: List[str] = []
    i = 0
    while i < len(units):
        u = units[i]

        if is_tag(u):
            # We'll treat it as prefix by default; may end up suffix by adjacency later.
            pending_prefix_tags.append(u)
            i += 1
            continue

        # Surface token
        surface = u
        attached: List[str] = []

        # Attach prefix tags
        if pending_prefix_tags:
            attached.extend(pending_prefix_tags)
            pending_prefix_tags = []

        # Attach suffix tags (immediately following tags)
        j = i + 1
        while j < len(units) and is_tag(units[j]):
            attached.append(units[j])
            j += 1

        # Filter tags:
        filtered: List[str] = []
        for t in attached:
            if should_exclude_tag(t, exclude_tag_substrings):
                continue
            # Keep context tags ONLY if attached to a surface (they are, here)
            filtered.append(t)

        out.append(SurfaceWithTags(surface=surface, tags=tuple(filtered)))
        i = j if j > i + 1 else i + 1

    # Any leftover pending tags at end are unattached -> drop.
    # This automatically ignores context tags that have nothing next to them.
    return out


def load_registry(path: str) -> Dict[str, str]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    mapping: Dict[str, str] = {}
    for it in items:
        if "tag" in it:
            mapping[it["tag"]] = it["id"]
        elif "subtag" in it:
            mapping[it["subtag"]] = it["id"]
        elif "value" in it:
            mapping[it["value"]] = it["id"]
    return mapping


def next_id(prefix: str, existing_ids: Iterable[str]) -> str:
    mx = 0
    for _id in existing_ids:
        if _id.startswith(prefix):
            try:
                mx = max(mx, int(_id[len(prefix) :]))
            except ValueError:
                pass
    return f"{prefix}{mx+1:06d}"


def write_registry_items(path: str, items: List[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in_json",
        required=True,
        help="JSON or JSONL file with rows containing 'anotated'",
    )
    ap.add_argument("--out_dir", default=".", help="Where to write outputs")
    ap.add_argument(
        "--out_jsonl",
        default="canonical_io.jsonl",
        help="Training pairs JSONL filename (inside out_dir)",
    )

    ap.add_argument(
        "--exclude_tag_substrings",
        nargs="*",
        default=DEFAULT_EXCLUDE_TAG_SUBSTRINGS,
        help=f"Drop any tag containing these substrings. Default: {DEFAULT_EXCLUDE_TAG_SUBSTRINGS}",
    )
    ap.add_argument(
        "--context_tags",
        nargs="*",
        default=sorted(DEFAULT_CONTEXT_TAGS),
        help=f"Context tags to ignore if unattached. Default: {sorted(DEFAULT_CONTEXT_TAGS)}",
    )
    ap.add_argument(
        "--debug",
        action="store_true",
        help="Print progress while building tokenizer outputs.",
    )
    ap.add_argument(
        "--log-every",
        type=int,
        default=0,
        help="If set, emit progress every N rows.",
    )

    args = ap.parse_args()

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)

    tags_path = os.path.join(out_dir, "annotated_tags.json")
    subtags_path = os.path.join(out_dir, "annotated_subtags.json")
    toks_path = os.path.join(out_dir, "annotated_tokens.json")
    pairs_path = os.path.join(out_dir, "annotated_token_pairs.json")
    variant_map_path = os.path.join(out_dir, "annotated_token_variants.json")
    io_path = os.path.join(out_dir, args.out_jsonl)

    # Load corpus
    def iter_corpus_rows(path: str):
        if path.endswith(".jsonl"):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    yield json.loads(line)
        else:
            with open(path, "r", encoding="utf-8") as f:
                rows = json.load(f)
            for row in rows:
                yield row

    if args.debug:
        print(f"[tokenizer] loading corpus from {args.in_json}")

    # Load existing registries (stable across runs)
    tag2id = load_registry(tags_path)  # full tags -> T######
    subtag2id = load_registry(subtags_path)  # subparts -> S######
    tok2id = load_registry(toks_path)  # surfaces -> M######

    context_tags = set(args.context_tags)
    exclude_tag_substrings = list(args.exclude_tag_substrings)

    # For token-pair export
    token_tag_pairs_set: Set[Tuple[str, str]] = set()
    variant_map_set: Set[Tuple[str, str, str, str, str, str, str, str]] = set()

    # Build training IO (JSONL)
    num_rows = 0
    with open(io_path, "w", encoding="utf-8") as out_f:
        for row in iter_corpus_rows(args.in_json):
            annotated = (
                row.get("anotated")
                or row.get("annotated")
                or row.get("anotated_string")
            )
            if not annotated or not isinstance(annotated, str):
                continue
            annotated_canon = (
                row.get("anotated_canon")
                or row.get("annotated_canon")
                or row.get("anotated_nav")
            )

            # Surface input preference order
            surface_in = (
                row.get("label")
                or row.get("surface")
                or row.get("orth")
                or strip_tags_to_surface(annotated)
            )

            swt = extract_surfaces_with_attached_tags(
                annotated,
                context_tags=context_tags,
                exclude_tag_substrings=exclude_tag_substrings,
            )

            # Update registries and build canonical output stream
            out_tokens: List[str] = []
            for item in swt:
                # morpheme token id
                if item.surface not in tok2id:
                    tok2id[item.surface] = next_id("M", tok2id.values())
                out_tokens.append(tok2id[item.surface])

                # attach full tags + subtags
                for full_tag in item.tags:
                    if full_tag not in tag2id:
                        tag2id[full_tag] = next_id("T", tag2id.values())
                    out_tokens.append(tag2id[full_tag])

                    # subtags from splitting on ":"
                    for sub in tag_to_subparts(full_tag):
                        if sub not in subtag2id:
                            subtag2id[sub] = next_id("S", subtag2id.values())
                        out_tokens.append(subtag2id[sub])

                    token_tag_pairs_set.add((item.surface, full_tag))

            # Write training example
            out_obj = {
                "input": surface_in,
                "output": " ".join(out_tokens),
            }
            out_f.write(json.dumps(out_obj, ensure_ascii=False) + "\n")
            num_rows += 1
            if args.log_every and num_rows % args.log_every == 0:
                print(
                    f"[tokenizer] rows={num_rows} tokens={len(tok2id)} "
                    f"tags={len(tag2id)} subtags={len(subtag2id)}"
                )

            if annotated_canon and isinstance(annotated_canon, str):
                swt_canon = extract_surfaces_with_attached_tags(
                    annotated_canon,
                    context_tags=context_tags,
                    exclude_tag_substrings=exclude_tag_substrings,
                )
                if len(swt_canon) == len(swt):
                    orth = row.get("orth") or ""
                    orth_source = row.get("orth_source") or ""
                    for item_var, item_can in zip(swt, swt_canon):
                        if item_can.surface not in tok2id:
                            tok2id[item_can.surface] = next_id("M", tok2id.values())
                        var_id = tok2id[item_var.surface]
                        can_id = tok2id[item_can.surface]
                        if item_var.tags:
                            for full_tag in item_var.tags:
                                tag_id = tag2id.get(full_tag, "")
                                variant_map_set.add(
                                    (
                                        item_var.surface,
                                        var_id,
                                        item_can.surface,
                                        can_id,
                                        full_tag,
                                        tag_id,
                                        orth,
                                        orth_source,
                                    )
                                )
                        else:
                            variant_map_set.add(
                                (
                                    item_var.surface,
                                    var_id,
                                    item_can.surface,
                                    can_id,
                                    "",
                                    "",
                                    orth,
                                    orth_source,
                                )
                            )

    # Write registries (sorted for stability)
    tag_items = [{"id": tag2id[t], "tag": t} for t in sorted(tag2id.keys())]
    subtag_items = [{"id": subtag2id[s], "subtag": s} for s in sorted(subtag2id.keys())]
    tok_items = [{"id": tok2id[v], "value": v} for v in sorted(tok2id.keys())]

    write_registry_items(tags_path, tag_items)
    write_registry_items(subtags_path, subtag_items)
    write_registry_items(toks_path, tok_items)

    # token-tag pairs export (like before)
    pair_items = [
        {"value": v, "tag": t, "translation": ""}
        for (v, t) in sorted(token_tag_pairs_set, key=lambda x: (x[1], x[0]))
    ]
    write_registry_items(pairs_path, pair_items)

    if variant_map_set:
        variant_items = [
            {
                "variant": v,
                "variant_id": vid,
                "canonical": c,
                "canonical_id": cid,
                "tag": tag,
                "tag_id": tid,
                "orth": orth,
                "orth_source": orth_source,
            }
            for (v, vid, c, cid, tag, tid, orth, orth_source) in sorted(
                variant_map_set, key=lambda x: (x[7], x[6], x[2], x[0], x[4])
            )
        ]
        write_registry_items(variant_map_path, variant_items)

    print("Done.")
    print(f"Wrote training IO: {io_path} (rows={num_rows})")
    print(
        f"Wrote registries:\n  {tags_path}\n  {subtags_path}\n  {toks_path}\n  {pairs_path}"
    )
    print(
        f"Counts: tokens={len(tok2id)} tags={len(tag2id)} subtags={len(subtag2id)} pairs={len(token_tag_pairs_set)}"
    )
    if variant_map_set:
        print(f"Wrote variant map: {variant_map_path} (rows={len(variant_map_set)})")


if __name__ == "__main__":
    main()
