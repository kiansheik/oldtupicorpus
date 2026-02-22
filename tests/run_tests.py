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
            "Optional path to corpus JSON/JSONL input. If omitted, the corpus is built "
            "from primary sources."
        ),
    )
    parser.add_argument(
        "--tokenizer-verbose",
        action="store_true",
        help="Print debug output while regenerating tokenizer artifacts.",
    )
    parser.add_argument(
        "--tokenizer-log-every",
        type=int,
        default=0,
        help="If set, emit tokenizer progress logs every N rows.",
    )
    parser.add_argument(
        "--tokenizer-label-from-annotated",
        action="store_true",
        help="Use annotated strings to derive labels when missing (faster).",
    )
    parser.add_argument(
        "--tokenizer-tqdm",
        action="store_true",
        help="Show a tqdm progress bar during corpus generation.",
    )
    parser.add_argument(
        "--tokenizer-orth-expand",
        nargs="*",
        default=[],
        help="Generate orthography variants in the corpus (e.g. POTIGUARA TUPINAMBA).",
    )
    parser.add_argument(
        "--tokenizer-orth-expand-all",
        action="store_true",
        help="Generate orthography variants for all known orthographies.",
    )
    parser.add_argument(
        "--tokenizer-orth-workers",
        type=int,
        default=1,
        help="Number of worker processes for orthography expansion.",
    )
    parser.add_argument(
        "--tokenizer-orth-batch-size",
        type=int,
        default=200,
        help="Batch size for orthography expansion workers.",
    )
    parser.add_argument(
        "--tokenizer-include-synthetic",
        action="store_true",
        help="Include synthetic sources when building the tokenizer corpus.",
    )
    parser.add_argument(
        "--include-synthetic",
        action="store_true",
        help="Include synthetic tests in the test run.",
    )
    parser.add_argument(
        "--timings",
        action="store_true",
        help="Print timing information for discovery, tests, and tokenizer steps.",
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
    debug_args = []
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
        build_script = root / "tokenizer" / "build_corpus_json.py"
        print(
            f"[tokenizer] {time.strftime('%H:%M:%S')} build corpus -> {corpus_json}",
            file=sys.stderr,
        )
        build_cmd = [
            sys.executable,
            str(build_script),
            "--out_jsonl",
            str(corpus_json),
            *debug_args,
        ]
        if args.tokenizer_tqdm:
            build_cmd.append("--tqdm")
        if args.tokenizer_label_from_annotated:
            build_cmd.append("--label-from-annotated")
        if args.tokenizer_orth_expand:
            build_cmd.append("--orth-expand")
            build_cmd.extend(args.tokenizer_orth_expand)
        if args.tokenizer_orth_expand_all:
            build_cmd.append("--orth-expand-all")
        if args.tokenizer_orth_workers:
            build_cmd.extend(["--orth-workers", str(args.tokenizer_orth_workers)])
        if args.tokenizer_orth_batch_size:
            build_cmd.extend(["--orth-batch-size", str(args.tokenizer_orth_batch_size)])
        if args.tokenizer_include_synthetic:
            build_cmd.append("--include-synthetic")
        subprocess.run(
            build_cmd,
            check=True,
            cwd=str(root),
            env=env,
        )

    tokenizer_script = root / "tokenizer" / "rawgrammarpair.py"
    print(
        f"[tokenizer] {time.strftime('%H:%M:%S')} build canonical io + registries",
        file=sys.stderr,
    )
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
            *debug_args,
        ],
        check=True,
        cwd=str(root),
        env=env,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    t0 = time.perf_counter()
    loader = unittest.TestLoader()
    if args.include_synthetic:
        suite = loader.discover(args.start_directory, pattern=args.pattern)
    else:
        suite = _discover_tests_excluding_synthetic(
            loader, args.start_directory, args.pattern
        )
    if args.timings:
        dt = time.perf_counter() - t0
        print(f"[timing] discovery: {dt:.3f}s", file=sys.stderr)
    t1 = time.perf_counter()
    verbosity = 2 if args.verbose else 0
    runner = SlimTextTestRunner(verbosity=verbosity, show_tracebacks=args.verbose)
    result = runner.run(suite)
    if args.timings:
        dt = time.perf_counter() - t1
        print(f"[timing] tests: {dt:.3f}s", file=sys.stderr)
    if not result.wasSuccessful():
        return 1
    if args.skip_tokenizer:
        return 0
    t2 = time.perf_counter()
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
    if args.timings:
        dt = time.perf_counter() - t2
        print(f"[timing] tokenizer: {dt:.3f}s", file=sys.stderr)
        total = time.perf_counter() - t0
        print(f"[timing] total: {total:.3f}s", file=sys.stderr)
    return 0


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
        if path.name == "synthetic_test.py":
            continue
        if path.name.startswith("_"):
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


if __name__ == "__main__":
    raise SystemExit(main())
