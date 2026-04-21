from __future__ import annotations

import argparse
import json
from pathlib import Path

from .utils import NHE_ENGA_DIR, compact_whitespace, normalize_text, split_glosses

DEFAULT_NAVARRO_PATH = NHE_ENGA_DIR / "docs" / "tupi_dict_navarro.json"


def _parse_navarro_definition(raw_definition: str | None) -> dict[str, object]:
    raw = compact_whitespace(raw_definition)
    if not raw:
        return {"raw": "", "qualifiers": [], "equivalents": [], "notes": []}

    prefix, separator, remainder = raw.partition("-")
    qualifier_text = compact_whitespace(prefix) if separator else ""
    body = compact_whitespace(remainder) if separator else raw

    qualifiers = [qualifier_text] if qualifier_text else []
    equivalents = split_glosses(body)
    return {
        "raw": raw,
        "qualifiers": qualifiers,
        "equivalents": equivalents,
        "notes": [],
    }


def load_navarro_entries(path: Path | None = None) -> list[dict[str, object]]:
    source_path = path or DEFAULT_NAVARRO_PATH
    if not source_path.exists():
        return []
    raw_entries = json.loads(source_path.read_text(encoding="utf-8"))
    entries: list[dict[str, object]] = []
    for index, raw_entry in enumerate(raw_entries):
        headword = compact_whitespace(raw_entry.get("first_word"))
        if not headword:
            continue
        structured_definition = _parse_navarro_definition(raw_entry.get("definition"))
        normalized_headword = normalize_text(headword)
        equivalents = structured_definition["equivalents"]
        search_terms = [normalized_headword]
        search_terms.extend(normalize_text(item) for item in equivalents)
        entry_id = f"navarro:{normalized_headword}:{index}"
        entries.append(
            {
                "entry_id": entry_id,
                "dataset": "navarro_index",
                "headword": headword,
                "normalized_headword": normalized_headword,
                "aliases": [],
                "part_of_speech": {
                    "kind": None,
                    "category": None,
                    "tag": None,
                },
                "definition": {
                    "raw": structured_definition["raw"],
                    "qualifiers": structured_definition["qualifiers"],
                    "glosses": equivalents,
                },
                "attestation_count": 0,
                "attestations": [],
                "source_counts": [],
                "search": {
                    "headword": normalized_headword,
                    "aliases": [],
                    "glosses": [item for item in search_terms[1:] if item],
                    "fulltext": normalize_text(
                        " ".join([headword, structured_definition["raw"], *equivalents])
                    ),
                },
                "metadata": {
                    "optional_number": compact_whitespace(
                        raw_entry.get("optional_number")
                    ),
                    "import_source": str(source_path),
                },
            }
        )
    return entries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect structured Navarro index entries available for import."
    )
    parser.add_argument(
        "--path",
        default=str(DEFAULT_NAVARRO_PATH),
        help="Path to the Navarro JSON file exported from nhe-enga.",
    )
    args = parser.parse_args(argv)
    entries = load_navarro_entries(Path(args.path))
    print(f"Loaded {len(entries)} Navarro entries from {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
