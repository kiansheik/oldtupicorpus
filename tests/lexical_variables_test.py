from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from authoring.lexical_variables import (
    direct_lexical_constructor_calls,
    historic_direct_lexical_constructor_calls,
)


ROOT = Path(__file__).resolve().parents[1]


class LexicalVariablesTest(unittest.TestCase):
    def test_checked_in_passages_have_no_direct_lexical_constructors(self) -> None:
        findings = historic_direct_lexical_constructor_calls(ROOT / "historic")
        self.assertEqual([], [finding.diagnostic() for finding in findings])

    def test_bad_fixture_finds_constructors_in_helpers_and_passage_expressions(
        self,
    ) -> None:
        source = """\
helper = Noun("outside")
l = [
    Noun("abá"),
    cop() * known,
]
l += (Verb("só") * known)
another_helper = Postposition("outside")
"""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.tu.py"
            path.write_text(source, encoding="utf-8")
            findings = direct_lexical_constructor_calls(path)

        self.assertEqual(
            [(finding.constructor, finding.line) for finding in findings],
            [("Noun", 1), ("Noun", 3), ("Verb", 6), ("Postposition", 7)],
        )

    def test_constructor_aliases_attributes_and_import_aliases_are_rejected(
        self,
    ) -> None:
        source = """\
Alias = Noun
l = [Alias("abá")]
l += pos.Postposition("supé")
from pydicate.lang.tupilang.pos import Verb as V
l += V("só")
"""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "aliases.tu.py"
            path.write_text(source, encoding="utf-8")
            findings = direct_lexical_constructor_calls(path)

        self.assertEqual(
            [(finding.constructor, finding.line) for finding in findings],
            [("Noun", 1), ("Postposition", 3), ("Verb", 4)],
        )


if __name__ == "__main__":
    unittest.main()
