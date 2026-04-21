from __future__ import annotations

import argparse
from pathlib import Path

from .utils import (
    DATA_DIR,
    expression_to_line_record,
    generated_at_iso,
    iter_historic_sources,
    write_json_artifact,
)


def build_rendered_corpus() -> dict[str, object]:
    sources_payload: dict[str, object] = {}
    total_lines = 0
    skipped_lines = 0
    for source_name, expressions, corpus_label in iter_historic_sources():
        lines = []
        for expression_index, expression in enumerate(expressions):
            line_record = expression_to_line_record(
                source_name=source_name,
                corpus_label=corpus_label,
                expression_index=expression_index,
                expression=expression,
            )
            if line_record is None:
                skipped_lines += 1
                continue
            lines.append(line_record)
        total_lines += len(lines)
        sources_payload[source_name] = {
            "title": source_name,
            "corpus": corpus_label,
            "line_count": len(lines),
            "lines": lines,
        }
    return {
        "meta": {
            "generated_at": generated_at_iso(),
            "source_count": len(sources_payload),
            "line_count": total_lines,
            "skipped_line_count": skipped_lines,
        },
        "sources": sources_payload,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build structured rendered corpus artifacts for the dictionary site."
    )
    parser.add_argument(
        "--out",
        default=str(DATA_DIR / "rendered_corpus.json"),
        help="Path to the uncompressed rendered corpus JSON artifact.",
    )
    args = parser.parse_args(argv)
    payload = build_rendered_corpus()
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (Path.cwd() / out_path).resolve()
    json_path, gz_path = write_json_artifact(out_path, payload)
    print(
        f"Rendered corpus: {payload['meta']['line_count']} lines across "
        f"{payload['meta']['source_count']} sources."
    )
    print(f"Wrote {json_path}")
    print(f"Wrote {gz_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
