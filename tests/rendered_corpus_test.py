from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dictionary.utils import (
    expression_to_line_record,
    iter_historic_sources,
    parse_annotated_chunks,
)


def _first_historic_line_record() -> dict[str, object]:
    source_name, expressions, corpus_label = next(iter_historic_sources())
    return expression_to_line_record(
        source_name=source_name,
        corpus_label=corpus_label,
        expression_index=0,
        expression=expressions[0],
    )


class RenderedCorpusMorphemeMetadataTest(unittest.TestCase):
    def test_line_record_emits_metadata_for_each_tagged_morpheme(self) -> None:
        line_record = _first_historic_line_record()
        tagged_chunks = [
            chunk
            for chunk in parse_annotated_chunks(line_record["annotated"])
            if chunk["tags"]
        ]
        self.assertEqual(len(line_record["morphemes"]), len(tagged_chunks))

    def test_line_record_uses_sentence_local_definition_for_morpheme_tooltips(
        self,
    ) -> None:
        line_record = _first_historic_line_record()
        tagged_chunks = [
            chunk
            for chunk in parse_annotated_chunks(line_record["annotated"])
            if chunk["tags"]
        ]
        paired = list(zip(tagged_chunks, line_record["morphemes"]))

        postposition = next(
            (meta for chunk, meta in paired if chunk["text"].strip() == "suí"),
            None,
        )
        self.assertIsNotNone(postposition)
        self.assertEqual(postposition["headword"], "suí")
        self.assertIsNotNone(postposition["definition"])
        self.assertIn("from", postposition["definition"]["raw"])

    def test_line_record_emits_nested_syntax_spans(self) -> None:
        source_name, expressions, corpus_label = next(
            item
            for item in iter_historic_sources()
            if item[0] == "araujo_catecismo_1686"
        )
        line_record = expression_to_line_record(
            source_name=source_name,
            corpus_label=corpus_label,
            expression_index=18,
            expression=expressions[18],
        )
        spans = {(span["start"], span["end"]) for span in line_record["syntax_spans"]}

        self.assertIn((5, 7), spans)
        self.assertIn((5, 8), spans)


if __name__ == "__main__":
    unittest.main()
