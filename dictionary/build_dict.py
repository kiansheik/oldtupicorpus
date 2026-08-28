from __future__ import annotations

import argparse
from pathlib import Path

from .build_entries import build_entries
from .build_rendered_corpus import build_rendered_corpus
from .utils import DATA_DIR, write_json_artifact


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build all static dictionary artifacts for local serving or deployment."
    )
    parser.add_argument(
        "--out-dir",
        default=str(DATA_DIR),
        help="Directory where dictionary data artifacts should be written.",
    )
    parser.add_argument(
        "--include-navarro",
        action="store_true",
        help="Include optional Navarro-derived supplemental entries from ../nhe-enga.",
    )
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (Path.cwd() / out_dir).resolve()

    rendered_corpus = build_rendered_corpus()
    entries = build_entries(
        rendered_corpus,
        include_navarro=args.include_navarro,
    )

    rendered_json, rendered_gz = write_json_artifact(
        out_dir / "rendered_corpus.json", rendered_corpus
    )
    entries_json, entries_gz = write_json_artifact(
        out_dir / "dictionary_entries.json", entries
    )
    for stale_artifact in (
        out_dir / "navarro_dict.json",
        out_dir / "navarro_dict.json.gz",
    ):
        stale_artifact.unlink(missing_ok=True)

    print(
        "Built dictionary site data: "
        f"{rendered_corpus['meta']['line_count']} rendered lines, "
        f"{entries['meta']['entry_count']} entries."
    )
    print(f"Wrote {rendered_json}")
    print(f"Wrote {rendered_gz}")
    print(f"Wrote {entries_json}")
    print(f"Wrote {entries_gz}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
