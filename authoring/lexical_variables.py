"""AST checks for unnamed lexical constructors in historic passages."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

LEXICAL_CONSTRUCTORS = frozenset(
    {
        "Noun",
        "ProperNoun",
        "Pronoun",
        "Verb",
        "Adverb",
        "Postposition",
        "Interjection",
        "Number",
        "Particle",
        "Conjunction",
        "Demonstrative",
        "Copula",
        "SizeSuffix",
    }
)


@dataclass(frozen=True, order=True)
class DirectLexicalConstructorCall:
    path: Path
    line: int
    column: int
    constructor: str

    def diagnostic(self) -> str:
        return (
            f"{self.path}:{self.line}:{self.column + 1}: "
            f"raw {self.constructor} constructor reference"
        )


def direct_lexical_constructor_calls(
    source_path: Path, *, source_name: str | None = None
) -> tuple[DirectLexicalConstructorCall, ...]:
    """Return every raw lexical-constructor reference in a historic module.

    The check is structural and never imports or executes the contributor source.
    The ``source_name`` argument remains for caller compatibility but does not
    narrow the scan: a passage can otherwise hide an unnamed lexeme in a helper
    assignment or constructor alias and refer to it from the source collection.
    Direct names, module attributes and explicitly imported constructor names are
    rejected. Grammatical helpers such as ``cop()``, ``v()``, ``n()`` and
    predicate methods remain valid.
    """

    text = source_path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(source_path))
    findings: dict[tuple[int, int, str], DirectLexicalConstructorCall] = {}
    for node in ast.walk(tree):
        references: list[tuple[str, int, int]] = []
        if (
            isinstance(node, ast.Name)
            and isinstance(node.ctx, ast.Load)
            and node.id in LEXICAL_CONSTRUCTORS
        ):
            references.append((node.id, node.lineno, node.col_offset))
        elif isinstance(node, ast.Attribute) and node.attr in LEXICAL_CONSTRUCTORS:
            references.append((node.attr, node.lineno, node.col_offset))
        elif isinstance(node, ast.ImportFrom):
            references.extend(
                (alias.name, alias.lineno, alias.col_offset)
                for alias in node.names
                if alias.name in LEXICAL_CONSTRUCTORS
            )
        for constructor, line, column in references:
            key = (line, column, constructor)
            findings[key] = DirectLexicalConstructorCall(
                path=source_path,
                line=line,
                column=column,
                constructor=constructor,
            )
    return tuple(sorted(findings.values()))


def historic_direct_lexical_constructor_calls(
    historic_dir: Path,
) -> tuple[DirectLexicalConstructorCall, ...]:
    findings: list[DirectLexicalConstructorCall] = []
    for source_path in sorted(historic_dir.glob("*.tu.py")):
        if source_path.name == "lexicon.tu.py":
            continue
        findings.extend(direct_lexical_constructor_calls(source_path))
    return tuple(sorted(findings))


__all__ = [
    "DirectLexicalConstructorCall",
    "LEXICAL_CONSTRUCTORS",
    "direct_lexical_constructor_calls",
    "historic_direct_lexical_constructor_calls",
]
