from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from historic.navarro_lexicon import (
    NavarroLexiconError,
    load_navarro_registry,
    navarro_lexeme,
)


def registry_document(entries: list[dict]) -> dict:
    shared = sum(entry["status"] == "shared_existing" for entry in entries)
    constructors: dict[str, int] = {}
    for entry in entries:
        constructors[entry["constructor"]] = (
            constructors.get(entry["constructor"], 0) + 1
        )
    return {
        "schema_version": 1,
        "source": {"dataset_fingerprint": "sha256:test"},
        "coverage": {
            "total_rows": len(entries),
            "tupi_source_rows": len(entries),
            "supported_source_rows": len(entries),
            "unresolved_source_rows": 0,
            "registry_entries": len(entries),
            "shared_existing_entries": shared,
            "dictionary_only_entries": len(entries) - shared,
            "entries_by_constructor": constructors,
            "unresolved_by_reason": {},
        },
        "entries": entries,
        "unresolved": [],
    }


def noun_entry(**changes) -> dict:
    entry = {
        "registry_id": "navarro:test:aba",
        "name": "aba_navarro_test",
        "constructor": "Noun",
        "values": {"value": "abá", "definition": "(s.) pessoa"},
        "headword": "abá",
        "definition": "(s.) pessoa",
        "status": "dictionary_only",
    }
    entry.update(changes)
    return entry


class NavarroLexiconTest(unittest.TestCase):
    def write_registry(self, document: dict, directory: str) -> Path:
        path = Path(directory) / "navarro_lexicon.json"
        path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
        return path

    def test_lookup_by_id_or_name_and_fresh_instantiation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_registry(registry_document([noun_entry()]), temporary)
            registry = load_navarro_registry(path)
            self.assertEqual(
                registry.lookup("navarro:test:aba").name, "aba_navarro_test"
            )
            self.assertEqual(registry.lookup("aba_navarro_test").headword, "abá")

            first = navarro_lexeme("navarro:test:aba", registry_path=path)
            second = navarro_lexeme("aba_navarro_test", registry_path=path)

        self.assertIsNot(first, second)
        self.assertEqual(first.verbete, "abá")
        self.assertEqual(first.definition, "(s.) pessoa")
        first.definition = "changed"
        self.assertEqual(second.definition, "(s.) pessoa")

    def test_shared_entry_requires_explicit_existing_name(self) -> None:
        entry = noun_entry(status="shared_existing")
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_registry(registry_document([entry]), temporary)
            with self.assertRaisesRegex(NavarroLexiconError, "shared_name is required"):
                load_navarro_registry(path)

    def test_duplicate_identity_unsupported_constructor_and_nested_value_fail(
        self,
    ) -> None:
        cases = [
            (
                registry_document(
                    [noun_entry(), noun_entry(name="other_navarro_test")]
                ),
                "Duplicate registry_id",
            ),
            (
                registry_document([noun_entry(constructor="__import__")]),
                "unsupported",
            ),
            (
                registry_document([noun_entry(values={"value": ["abá"]})]),
                "JSON scalar",
            ),
            (
                registry_document([noun_entry(values={"unknown": "abá"})]),
                "do not match Noun",
            ),
        ]
        for document, message in cases:
            with self.subTest(
                message=message
            ), tempfile.TemporaryDirectory() as temporary:
                path = self.write_registry(document, temporary)
                with self.assertRaisesRegex(NavarroLexiconError, message):
                    load_navarro_registry(path)

    def test_coverage_invariants_are_validated(self) -> None:
        document = registry_document([noun_entry()])
        document["coverage"]["dictionary_only_entries"] = 0
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_registry(document, temporary)
            with self.assertRaisesRegex(NavarroLexiconError, "shared/dictionary-only"):
                load_navarro_registry(path)

    def test_runtime_values_cannot_diverge_from_printed_metadata(self) -> None:
        cases = [
            (
                noun_entry(values={"value": "aîpo", "definition": "(s.) pessoa"}),
                "entry headword",
            ),
            (
                noun_entry(values={"value": "abá", "definition": "other"}),
                "entry definition",
            ),
        ]
        for entry, message in cases:
            with self.subTest(
                message=message
            ), tempfile.TemporaryDirectory() as temporary:
                path = self.write_registry(registry_document([entry]), temporary)
                with self.assertRaisesRegex(NavarroLexiconError, message):
                    load_navarro_registry(path)

    def test_unresolved_rows_require_unique_indices_and_reasons(self) -> None:
        document = registry_document([])
        document["coverage"].update(
            total_rows=2,
            tupi_source_rows=2,
            supported_source_rows=0,
            unresolved_source_rows=2,
            unresolved_by_reason={"ambiguous": 2},
        )
        document["unresolved"] = [
            {"entry_index": 4, "reasons": ["ambiguous"]},
            {"entry_index": 4, "reasons": ["ambiguous"]},
        ]
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_registry(document, temporary)
            with self.assertRaisesRegex(NavarroLexiconError, "Duplicate unresolved"):
                load_navarro_registry(path)

    def test_unresolved_reason_summary_must_match_rows(self) -> None:
        document = registry_document([])
        document["coverage"].update(
            total_rows=1,
            tupi_source_rows=1,
            supported_source_rows=0,
            unresolved_source_rows=1,
            unresolved_by_reason={"different": 1},
        )
        document["unresolved"] = [
            {"entry_index": 4, "reasons": ["ambiguous"]},
        ]
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_registry(document, temporary)
            with self.assertRaisesRegex(NavarroLexiconError, "unresolved_by_reason"):
                load_navarro_registry(path)


if __name__ == "__main__":
    unittest.main()
