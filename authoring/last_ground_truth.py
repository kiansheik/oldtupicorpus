"""Show trailing saved ground truth beside its historic source expressions."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

from authoring.records import load_records, record_path
from authoring.source_annotations import (
    _append_values,
    _initial_collection,
    _is_append_to,
)

ROOT = Path(__file__).resolve().parents[1]


def choose_source(root: Path, requested: str) -> Path:
    historic = root / "historic"
    if requested:
        source = Path(requested).name
        if source.endswith(".tu.py"):
            name = source[: -len(".tu.py")]
        elif "." not in source:
            name = source
        else:
            raise ValueError("SOURCE must be a .tu.py file or source name")
        path = historic / f"{name}.tu.py"
        if not path.is_file() or path.name == "lexicon.tu.py":
            raise ValueError(f"Unknown historic source: {requested}")
        return path

    candidates = [
        path for path in historic.glob("*.tu.py") if path.name != "lexicon.tu.py"
    ]
    if not candidates:
        raise ValueError("No historic .tu.py source files found")
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name))


def source_commands(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    collection, initial = _initial_collection(tree, path, path.name[: -len(".tu.py")])
    commands = [
        (node.lineno, ast.get_source_segment(text, node).strip())
        for node in initial.elts
    ]
    for statement in tree.body:
        if _is_append_to(statement, collection):
            values = _append_values(statement.value)
            if len(values) == 1:
                commands.append(
                    (statement.lineno, ast.get_source_segment(text, statement).strip())
                )
            else:
                commands.extend(
                    (
                        statement.lineno,
                        f"{collection} += {ast.get_source_segment(text, value).strip()}",
                    )
                    for value in values
                )
    return commands


def display(root: Path, requested: str = "", count: int = 3) -> str:
    if count < 1:
        raise ValueError("N must be a positive integer")
    path = choose_source(root, requested)
    name = path.name[: -len(".tu.py")]
    records_file = record_path(root, kind="historic", source=name)
    if not records_file.is_file():
        raise ValueError(f"No generated ground truth for {path.relative_to(root)}")
    records = load_records(records_file, source=name, kind="historic")
    commands = source_commands(path)
    if len(records) > len(commands):
        raise ValueError(
            f"{path.relative_to(root)} has fewer commands than ground-truth records"
        )

    output = [f"{path.relative_to(root)} — {records_file.relative_to(root)}"]
    for record in records[-count:]:
        line, command = commands[record.ordinal - 1]
        output.append(f"\n{record.id}  {path.relative_to(root)}:{line}")
        output.append(command)
        output.append(f"  → {record.expected_surface}")
    if len(commands) > len(records):
        gap = len(commands) - len(records)
        output.append(f"\n{gap} source command(s) have no saved ground-truth record.")
    return "\n".join(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="")
    parser.add_argument("--count", type=int, default=3)
    args = parser.parse_args()
    try:
        print(display(ROOT, args.source, args.count))
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
