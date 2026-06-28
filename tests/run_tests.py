from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
import time
import traceback
import unittest
from pathlib import Path


class SlimTextTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions: bool, verbosity: int, show_tracebacks: bool) -> None:
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

    def addSubTest(self, test: unittest.TestCase, subtest: unittest.TestCase, err) -> None:
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
        for test, err in self._raw_failures or self.failures:
            self._write_issue("FAIL", test, err)
        for test, err in self._raw_errors or self.errors:
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
            self.stream, self.descriptions, self.verbosity, self.show_tracebacks
        )


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the test suite.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show failure tracebacks.")
    parser.add_argument("-s", "--start-directory", default="tests", help="Directory to discover tests from.")
    parser.add_argument("-p", "--pattern", default="*_test.py", help="Pattern to match test files.")
    parser.add_argument("--skip-tokenizer", action="store_true", help="Skip tokenizer artifact regeneration.")
    parser.add_argument("--tokenizer-out-dir", default="tokenizer/output")
    parser.add_argument("--tokenizer-out-jsonl", default="canonical_io.jsonl")
    parser.add_argument("--tokenizer-corpus-json", default="")
    parser.add_argument("--tokenizer-verbose", action="store_true")
    parser.add_argument("--tokenizer-log-every", type=int, default=0)
    parser.add_argument("--tokenizer-label-from-annotated", action="store_true")
    parser.add_argument("--tokenizer-tqdm", action="store_true")
    parser.add_argument("--tokenizer-orth-expand", nargs="*", default=[])
    parser.add_argument("--tokenizer-orth-expand-all", action="store_true")
    parser.add_argument("--tokenizer-orth-workers", type=int, default=1)
    parser.add_argument("--tokenizer-orth-batch-size", type=int, default=200)
    parser.add_argument("--tokenizer-include-synthetic", action="store_true")
    parser.add_argument("--include-synthetic", action="store_true", help="Include synthetic tests.")
    parser.add_argument("--timings", action="store_true", help="Print timing information.")
    return parser.parse_args(argv)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _regenerate_tokens(args: argparse.Namespace) -> None:
    root = _project_root()
    out_dir = Path(args.tokenizer_out_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    debug_args: list[str] = []
    if args.tokenizer_verbose:
        debug_args.append("--debug")
    if args.tokenizer_log_every:
        debug_args.extend(["--log-every", str(args.tokenizer_log_every)])
    env = dict(os.environ)
    if args.tokenizer_verbose:
        env.setdefault("PYTHONUNBUFFERED", "1")

    if args.tokenizer_corpus_json:
        corpus_json = Path(args.tokenizer_corpus_json)
        if not corpus_json.is_absolute():
            corpus_json = root / corpus_json
    else:
        corpus_json = out_dir / "corpus.jsonl"
        command = [
            sys.executable,
            str(root / "tokenizer" / "build_corpus_json.py"),
            "--out_jsonl",
            str(corpus_json),
            *debug_args,
        ]
        if args.tokenizer_tqdm:
            command.append("--tqdm")
        if args.tokenizer_label_from_annotated:
            command.append("--label-from-annotated")
        if args.tokenizer_orth_expand:
            command.extend(["--orth-expand", *args.tokenizer_orth_expand])
        if args.tokenizer_orth_expand_all:
            command.append("--orth-expand-all")
        if args.tokenizer_orth_workers:
            command.extend(["--orth-workers", str(args.tokenizer_orth_workers)])
        if args.tokenizer_orth_batch_size:
            command.extend(["--orth-batch-size", str(args.tokenizer_orth_batch_size)])
        if args.tokenizer_include_synthetic:
            command.append("--include-synthetic")
        subprocess.run(command, check=True, cwd=str(root), env=env)

    subprocess.run(
        [
            sys.executable,
            str(root / "tokenizer" / "rawgrammarpair.py"),
            "--in_json",
            str(corpus_json),
            "--out_dir",
            str(out_dir),
            "--out_jsonl",
            args.tokenizer_out_jsonl,
            *debug_args,
        ],
        check=True,
        cwd=str(root),
        env=env,
    )


def _filter_out_synthetic(suite: unittest.TestSuite) -> unittest.TestSuite:
    filtered = unittest.TestSuite()
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            nested = _filter_out_synthetic(item)
            if nested.countTestCases():
                filtered.addTest(nested)
            continue
        module = getattr(item.__class__, "__module__", "")
        test_id = getattr(item, "id", lambda: "")()
        if module.endswith("synthetic_test") or "synthetic_test" in test_id:
            continue
        filtered.addTest(item)
    return filtered


def _discover_tests_excluding_synthetic(
    loader: unittest.TestLoader, start_directory: str, pattern: str
) -> unittest.TestSuite:
    start_path = Path(start_directory).resolve()
    suite = unittest.TestSuite()
    for path in sorted(start_path.rglob(pattern)):
        if path.name == "synthetic_test.py" or path.name.startswith("_"):
            continue
        module_name = f"_codex_test_{path.stem}_{abs(hash(path))}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        suite.addTests(loader.loadTestsFromModule(module))
    return suite


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    started = time.perf_counter()
    loader = unittest.TestLoader()
    suite = (
        loader.discover(args.start_directory, pattern=args.pattern)
        if args.include_synthetic
        else _discover_tests_excluding_synthetic(loader, args.start_directory, args.pattern)
    )
    if args.timings:
        print(f"[timing] discovery: {time.perf_counter() - started:.3f}s", file=sys.stderr)
    tests_started = time.perf_counter()
    result = SlimTextTestRunner(verbosity=2 if args.verbose else 0, show_tracebacks=args.verbose).run(suite)
    if args.timings:
        print(f"[timing] tests: {time.perf_counter() - tests_started:.3f}s", file=sys.stderr)
    if not result.wasSuccessful():
        return 1
    if args.skip_tokenizer:
        return 0
    try:
        _regenerate_tokens(args)
    except subprocess.CalledProcessError as exc:
        print(f"Tokenizer regeneration failed (exit {exc.returncode}).", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Tokenizer regeneration failed: {exc}.", file=sys.stderr)
        return 1
    if args.timings:
        print(f"[timing] total: {time.perf_counter() - started:.3f}s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
