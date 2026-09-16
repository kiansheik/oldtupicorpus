from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from authoring import service
from authoring.records import GroundTruthRecord, write_records
from tests.ground_truth_cases import GroundTruthCase


class FakeExpression:
    def __init__(self, text: str) -> None:
        self.text = text

    def eval(self) -> str:
        return self.text


class CommitGroundTruthTest(unittest.TestCase):
    def _make_case(
        self, expressions: list[str], records: list[GroundTruthRecord]
    ) -> GroundTruthCase:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        record_path = Path(tmpdir.name) / "sample.jsonl"
        write_records(record_path, records)
        return GroundTruthCase(
            name="sample",
            record_path=record_path,
            expressions=[FakeExpression(text) for text in expressions],
            kind="historic",
        )

    def test_commit_appends_the_next_unaccounted_record(self) -> None:
        case = self._make_case(["alpha", "beta"], [])
        with patch.object(service, "get_case", return_value=case):
            result = service.commit_ground_truth("sample", 1)
        self.assertEqual(
            result, {"source": "sample", "ordinal": 1, "committed_surface": "alpha"}
        )
        records = service.get_case_records(case)
        self.assertEqual([r.surface for r in records], ["alpha"])
        self.assertIsNone(records[0].normalized_target)

    def test_commit_refuses_to_skip_ahead_of_unaccounted_records(self) -> None:
        case = self._make_case(["alpha", "beta"], [])
        with patch.object(service, "get_case", return_value=case):
            with self.assertRaises(ValueError):
                service.commit_ground_truth("sample", 2)

    def test_commit_refreshes_a_stale_record_with_no_declared_target(self) -> None:
        stale = GroundTruthRecord(
            id="sample:0001",
            source="sample",
            kind="historic",
            ordinal=1,
            surface="old-render",
        )
        case = self._make_case(["new-render"], [stale])
        with patch.object(service, "get_case", return_value=case):
            result = service.commit_ground_truth("sample", 1)
        self.assertEqual(result["committed_surface"], "new-render")
        records = service.get_case_records(case)
        self.assertEqual(records[0].surface, "new-render")

    def test_commit_refuses_to_overwrite_an_unmatched_declared_target(self) -> None:
        declared = GroundTruthRecord(
            id="sample:0001",
            source="sample",
            kind="historic",
            ordinal=1,
            surface="old-render",
            normalized_target="linguist-approved-form",
        )
        case = self._make_case(["still-wrong-render"], [declared])
        with patch.object(service, "get_case", return_value=case):
            with self.assertRaises(ValueError):
                service.commit_ground_truth("sample", 1)
        # The declared target must survive the refused attempt untouched.
        records = service.get_case_records(case)
        self.assertEqual(records[0].normalized_target, "linguist-approved-form")

    def test_commit_allows_refresh_once_rendering_matches_declared_target(self) -> None:
        declared = GroundTruthRecord(
            id="sample:0001",
            source="sample",
            kind="historic",
            ordinal=1,
            surface="old-render",
            normalized_target="fixed-render",
        )
        case = self._make_case(["fixed-render"], [declared])
        with patch.object(service, "get_case", return_value=case):
            result = service.commit_ground_truth("sample", 1)
        self.assertEqual(result["committed_surface"], "fixed-render")
        records = service.get_case_records(case)
        self.assertEqual(records[0].normalized_target, "fixed-render")


class ReloadEngineTest(unittest.TestCase):
    def test_reload_engine_evicts_only_pydicate_and_tupi_modules(self) -> None:
        sys.modules["pydicate"] = object()  # type: ignore[assignment]
        sys.modules["pydicate.lang.tupilang"] = object()  # type: ignore[assignment]
        sys.modules["tupi"] = object()  # type: ignore[assignment]
        sys.modules["tupidoesnotcount"] = object()  # type: ignore[assignment]
        self.addCleanup(sys.modules.pop, "tupidoesnotcount", None)

        result = service.reload_engine()

        self.assertIn("pydicate", result["reloaded_modules"])
        self.assertIn("pydicate.lang.tupilang", result["reloaded_modules"])
        self.assertIn("tupi", result["reloaded_modules"])
        self.assertNotIn("pydicate", sys.modules)
        self.assertNotIn("tupi", sys.modules)
        self.assertIn("tupidoesnotcount", sys.modules)


if __name__ == "__main__":
    unittest.main()
