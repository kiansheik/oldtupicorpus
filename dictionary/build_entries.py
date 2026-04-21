from __future__ import annotations

import argparse
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

from historic.lexicon import load_lexicon

from .navarro_import import load_navarro_entries
from .utils import (
    DATA_DIR,
    compact_whitespace,
    extract_headword,
    generated_at_iso,
    iter_expression_nodes,
    iter_historic_sources,
    normalize_text,
    parse_gloss_definition,
    source_sort_key,
    write_json_artifact,
)


def _entry_digest(category: str | None, headword: str, definition: str) -> str:
    return hashlib.sha1(
        f"{category or ''}|{headword}|{definition}".encode("utf-8")
    ).hexdigest()[:10]


def _build_lexicon_entries(
    rendered_corpus: dict[str, object],
) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    lexicon = load_lexicon()
    grouped_entries: dict[tuple[str, str, str], dict[str, object]] = {}

    for symbol_name, node in lexicon.items():
        headword = extract_headword(node)
        definition = compact_whitespace(getattr(node, "definition", ""))
        if not headword:
            continue
        type_name = type(node).__name__
        group_key = (type_name, headword, definition)
        category = getattr(node, "category", None)
        tag = getattr(node, "tag", None)
        base_entry = grouped_entries.setdefault(
            group_key,
            {
                "entry_id": "",
                "dataset": "lexicon",
                "headword": headword,
                "normalized_headword": normalize_text(headword),
                "aliases": set(),
                "part_of_speech": {
                    "kind": type_name,
                    "category": category,
                    "tag": tag,
                },
                "definition": parse_gloss_definition(definition),
                "attestation_count": 0,
                "attestations": [],
                "source_counts": [],
                "search": {
                    "headword": normalize_text(headword),
                    "aliases": [],
                    "glosses": [],
                    "fulltext": "",
                },
                "metadata": {
                    "symbols": set(),
                    "definition_missing": not bool(definition),
                },
            },
        )
        base_entry["metadata"]["symbols"].add(symbol_name)
        if symbol_name != headword and "_" not in symbol_name:
            base_entry["aliases"].add(symbol_name)

    entries = []
    entry_index: dict[str, dict[str, object]] = {}
    for _, entry in sorted(
        grouped_entries.items(),
        key=lambda item: (
            item[1]["normalized_headword"],
            item[1]["part_of_speech"]["category"] or "",
            item[1]["definition"]["raw"],
        ),
    ):
        headword = entry["headword"]
        category = entry["part_of_speech"]["category"]
        definition = entry["definition"]["raw"]
        digest = _entry_digest(category, headword, definition)
        entry_id = f"lexicon:{category or 'entry'}:{normalize_text(headword)}:{digest}"
        aliases = sorted(entry["aliases"], key=normalize_text)
        entry["entry_id"] = entry_id
        entry["aliases"] = aliases
        entry["metadata"]["symbols"] = sorted(entry["metadata"]["symbols"])
        gloss_terms = [
            normalize_text(gloss) for gloss in entry["definition"]["glosses"]
        ]
        fulltext_parts = [headword, *aliases, entry["definition"]["raw"]]
        entry["search"] = {
            "headword": entry["normalized_headword"],
            "aliases": [normalize_text(alias) for alias in aliases if alias],
            "glosses": [term for term in gloss_terms if term],
            "fulltext": normalize_text(" ".join(fulltext_parts)),
        }
        entries.append(entry)
        entry_index[entry_id] = entry

    line_lookup = {}
    for source_payload in rendered_corpus["sources"].values():
        for line in source_payload["lines"]:
            line_lookup[line["line_id"]] = line

    headword_lookup: dict[str, list[str]] = defaultdict(list)
    category_lookup: dict[tuple[str, str], list[str]] = defaultdict(list)
    for entry in entries:
        headword_lookup[entry["normalized_headword"]].append(entry["entry_id"])
        category = entry["part_of_speech"]["category"]
        if category:
            category_lookup[(entry["normalized_headword"], category)].append(
                entry["entry_id"]
            )

    entry_to_line_ids: dict[str, set[str]] = defaultdict(set)
    for source_name, expressions, _corpus_label in iter_historic_sources():
        for expression_index, expression in enumerate(expressions):
            line_id = f"{source_name}:{expression_index}"
            matched_entry_ids: set[str] = set()
            for node in iter_expression_nodes(expression):
                headword = extract_headword(node)
                normalized_headword = normalize_text(headword)
                if not normalized_headword:
                    continue
                category = getattr(node, "category", None)
                candidates = []
                if category:
                    candidates = category_lookup.get(
                        (normalized_headword, category), []
                    )
                if not candidates:
                    candidates = headword_lookup.get(normalized_headword, [])
                matched_entry_ids.update(candidates)
            for entry_id in matched_entry_ids:
                entry_to_line_ids[entry_id].add(line_id)

    for entry in entries:
        line_ids = sorted(
            entry_to_line_ids.get(entry["entry_id"], ()), key=source_sort_key
        )
        entry["attestations"] = [
            {
                "line_id": line_id,
                "source": line_lookup[line_id]["source"],
                "expression_index": line_lookup[line_id]["expression_index"],
            }
            for line_id in line_ids
            if line_id in line_lookup
        ]
        entry["attestation_count"] = len(entry["attestations"])
        source_counts = Counter(item["source"] for item in entry["attestations"])
        entry["source_counts"] = [
            {"source": source_name, "count": count}
            for source_name, count in sorted(source_counts.items())
        ]
        preview_surfaces = []
        for attestation in entry["attestations"][:5]:
            line = line_lookup.get(attestation["line_id"])
            if line:
                preview_surfaces.append(line["surface"])
        entry["search"]["fulltext"] = normalize_text(
            " ".join(
                [
                    entry["headword"],
                    *entry["aliases"],
                    entry["definition"]["raw"],
                    *preview_surfaces,
                ]
            )
        )

    filtered_entries = [
        entry
        for entry in entries
        if entry["definition"]["raw"] or entry["attestation_count"] > 0
    ]
    filtered_index = {entry["entry_id"]: entry for entry in filtered_entries}
    return filtered_entries, filtered_index


def build_entries(
    rendered_corpus: dict[str, object],
    *,
    include_navarro: bool = False,
) -> dict[str, object]:
    lexicon_entries, _entry_index = _build_lexicon_entries(rendered_corpus)
    navarro_entries = load_navarro_entries() if include_navarro else []
    entries = sorted(
        [*lexicon_entries, *navarro_entries],
        key=lambda entry: (
            0 if entry["dataset"] == "lexicon" else 1,
            entry["normalized_headword"],
            entry["headword"],
        ),
    )
    dataset_counts = Counter(entry["dataset"] for entry in entries)
    return {
        "meta": {
            "generated_at": generated_at_iso(),
            "entry_count": len(entries),
            "dataset_counts": dict(sorted(dataset_counts.items())),
            "includes_navarro": include_navarro and bool(navarro_entries),
        },
        "entries": entries,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build structured dictionary entries for the static dictionary site."
    )
    parser.add_argument(
        "--rendered-corpus",
        default=str(DATA_DIR / "rendered_corpus.json"),
        help="Path to the rendered corpus JSON artifact.",
    )
    parser.add_argument(
        "--out",
        default=str(DATA_DIR / "dictionary_entries.json"),
        help="Path to the uncompressed dictionary entries JSON artifact.",
    )
    parser.add_argument(
        "--include-navarro",
        action="store_true",
        help="Include optional Navarro-derived supplemental entries from ../nhe-enga.",
    )
    args = parser.parse_args(argv)
    rendered_corpus_path = Path(args.rendered_corpus)
    if not rendered_corpus_path.is_absolute():
        rendered_corpus_path = (Path.cwd() / rendered_corpus_path).resolve()
    rendered_corpus = __import__("json").loads(
        rendered_corpus_path.read_text(encoding="utf-8")
    )
    payload = build_entries(
        rendered_corpus,
        include_navarro=args.include_navarro,
    )
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (Path.cwd() / out_path).resolve()
    json_path, gz_path = write_json_artifact(out_path, payload)
    print(
        f"Dictionary entries: {payload['meta']['entry_count']} total "
        f"({payload['meta']['dataset_counts']})."
    )
    print(f"Wrote {json_path}")
    print(f"Wrote {gz_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
