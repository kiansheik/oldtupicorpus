from __future__ import annotations

import argparse
import subprocess
import sys
import traceback
import unittest
from pathlib import Path


class SlimTextTestResult(unittest.TextTestResult):
    def __init__(
        self,
        stream,
        descriptions: bool,
        verbosity: int,
        show_tracebacks: bool,
    ) -> None:
        super().__init__(stream, descriptions, verbosity)
        self.show_tracebacks = show_tracebacks
        self._raw_failures: list[tuple[unittest.TestCase, tuple]] = []
        self._raw_errors: list[tuple[unittest.TestCase, tuple]] = []

    def addFailure(self, test: unittest.TestCase, err) -> None:
        self._raw_failures.append((test, err))
        super().addFailure(test, err)

    def addError(self, test: unittest.TestCase, err) -> None:
        self._raw_errors.append((test, err))
        super().addError(test, err)

    def addSubTest(
        self, test: unittest.TestCase, subtest: unittest.TestCase, err
    ) -> None:
        super().addSubTest(test, subtest, err)
        if err is None:
            return
        if issubclass(err[0], test.failureException):
            self._raw_failures.append((subtest, err))
        else:
            self._raw_errors.append((subtest, err))

    def printErrors(self) -> None:
        if self.show_tracebacks:
            super().printErrors()
            return
        if not self.failures and not self.errors:
            return
        failures = self._raw_failures or self.failures
        errors = self._raw_errors or self.errors
        for test, err in failures:
            self._write_issue("FAIL", test, err)
        for test, err in errors:
            self._write_issue("ERROR", test, err)

    def _write_issue(self, label: str, test: unittest.TestCase, err) -> None:
        self.stream.writeln(f"{label}: {self.getDescription(test)}")
        if isinstance(err, tuple) and len(err) == 3:
            details = "".join(traceback.format_exception_only(err[0], err[1])).rstrip()
        else:
            details = str(err).rstrip()
        if details:
            self.stream.writeln(details)


class SlimTextTestRunner(unittest.TextTestRunner):
    def __init__(self, *args, show_tracebacks: bool, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.show_tracebacks = show_tracebacks

    def _makeResult(self) -> SlimTextTestResult:
        return SlimTextTestResult(
            self.stream,
            self.descriptions,
            self.verbosity,
            self.show_tracebacks,
        )


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run test suite.")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show failure tracebacks.",
    )
    parser.add_argument(
        "-s",
        "--start-directory",
        default="tests",
        help="Directory to discover tests from.",
    )
    parser.add_argument(
        "-p",
        "--pattern",
        default="*_test.py",
        help="Pattern to match test files.",
    )
    parser.add_argument(
        "--skip-tokenizer",
        action="store_true",
        help="Skip regenerating tokenizer outputs after successful tests.",
    )
    parser.add_argument(
        "--tokenizer-out-dir",
        default="tokenizer/output",
        help="Directory to write tokenizer outputs.",
    )
    parser.add_argument(
        "--tokenizer-out-jsonl",
        default="canonical_io.jsonl",
        help="Training pairs JSONL filename (inside tokenizer output dir).",
    )
    parser.add_argument(
        "--tokenizer-corpus-json",
        default="",
        help=(
            "Optional path to corpus JSON input. If omitted, the corpus is built "
            "from primary sources."
        ),
    )
    return parser.parse_args(argv)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _regenerate_tokens(args: argparse.Namespace) -> None:
    root = _project_root()
    out_dir = Path(args.tokenizer_out_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    corpus_json: Path
    if args.tokenizer_corpus_json:
        corpus_json = Path(args.tokenizer_corpus_json)
        if not corpus_json.is_absolute():
            corpus_json = root / corpus_json
    else:
        corpus_json = out_dir / "corpus.json"
        build_script = root / "tokenizer" / "build_corpus_json.py"
        subprocess.run(
            [sys.executable, str(build_script), "--out_json", str(corpus_json)],
            check=True,
            cwd=str(root),
        )

    tokenizer_script = root / "tokenizer" / "rawgrammarpair.py"
    subprocess.run(
        [
            sys.executable,
            str(tokenizer_script),
            "--in_json",
            str(corpus_json),
            "--out_dir",
            str(out_dir),
            "--out_jsonl",
            args.tokenizer_out_jsonl,
        ],
        check=True,
        cwd=str(root),
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    loader = unittest.TestLoader()
    suite = loader.discover(args.start_directory, pattern=args.pattern)
    verbosity = 2 if args.verbose else 0
    runner = SlimTextTestRunner(verbosity=verbosity, show_tracebacks=args.verbose)
    result = runner.run(suite)
    if not result.wasSuccessful():
        return 1
    if args.skip_tokenizer:
        return 0
    try:
        _regenerate_tokens(args)
    except subprocess.CalledProcessError as exc:
        print(
            f"Tokenizer regeneration failed (exit {exc.returncode}).", file=sys.stderr
        )
        return 1
    except OSError as exc:
        print(f"Tokenizer regeneration failed: {exc}.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
