#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Iterable, Optional
import importlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from historic import primary_sources as sources

SYNTHETIC_MODULE_PATH = "synthetic.primary_sources"


ANNOTATED_ATTRS = (
    "anotated",
    "annotated",
    "anotated_string",
    "annotated_string",
)

LABEL_ATTRS = (
    "label",
    "surface",
    "orth",
)

TAG_STRIP_RE = re.compile(r"\[.*?\]")


def strip_tags_to_surface(s: str) -> str:
    s2 = TAG_STRIP_RE.sub("", s)
    s2 = re.sub(r"\s+", " ", s2).strip()
    return s2


def _normalize_orth_list(orth_list: list[str], expand_all: bool) -> list[str]:
    if not orth_list and not expand_all:
        return []
    try:
        from tupi.orth import ALT_ORTS
    except Exception:
        return []
    orths = set(o.upper() for o in orth_list)
    if expand_all:
        orths.update(ALT_ORTS.keys())
    orths.discard("NAVARRO")
    return sorted(orths)


def _value_from_attr(obj: object, attr: str) -> Optional[str]:
    if not hasattr(obj, attr):
        return None
    value = getattr(obj, attr)
    if callable(value):
        try:
            value = value()
        except TypeError:
            return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _get_annotated(expr: object) -> Optional[str]:
    for attr in ANNOTATED_ATTRS:
        value = _value_from_attr(expr, attr)
        if value:
            return value
    eval_fn = getattr(expr, "eval", None)
    if callable(eval_fn):
        try:
            value = eval_fn(annotated=True)
        except TypeError:
            value = None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
    return None


def _get_label(
    expr: object, *, annotated: Optional[str], prefer_annotated: bool
) -> Optional[str]:
    for attr in LABEL_ATTRS:
        value = _value_from_attr(expr, attr)
        if value:
            return value
    if prefer_annotated and annotated:
        return strip_tags_to_surface(annotated)
    eval_fn = getattr(expr, "eval", None)
    if callable(eval_fn):
        try:
            value = eval_fn(annotated=False)
        except TypeError:
            value = None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
    return None


def _iter_sources_from_module(
    module, corpus_label: str, *, debug: bool = False
) -> Iterable[tuple[str, object, str, Optional[int]]]:
    names = getattr(module, "__all__", [])
    for name in names:
        expressions = getattr(module, name, None)
        if expressions is None:
            continue
        size = None
        if callable(expressions):
            size_fn = getattr(expressions, "estimated_size", None)
            if callable(size_fn):
                t0 = time.perf_counter()
                size = size_fn()
                if debug:
                    dt = time.perf_counter() - t0
                    print(
                        f"[corpus] size estimate source={name} count={size} took={dt:.3f}s"
                    )
        else:
            size = len(expressions) if hasattr(expressions, "__len__") else None
        yield name, expressions, corpus_label, size


def _iter_primary_sources(
    debug: bool = False,
    include_synthetic: bool = False,
) -> Iterable[tuple[str, Iterable[object], str, Optional[int]]]:
    yield from _iter_sources_from_module(sources, "historic", debug=debug)
    if not include_synthetic:
        if debug:
            print("[corpus] synthetic sources skipped")
        return
    t0 = time.perf_counter()
    try:
        synthetic_module = importlib.import_module(SYNTHETIC_MODULE_PATH)
    except ModuleNotFoundError:
        synthetic_module = None
    if debug:
        dt = time.perf_counter() - t0
        print(f"[corpus] import synthetic: {dt:.3f}s")
    if synthetic_module is not None:
        yield from _iter_sources_from_module(synthetic_module, "synthetic", debug=debug)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a corpus JSONL file from primary sources."
    )
    parser.add_argument(
        "--out_jsonl",
        default="tokenizer/output/corpus.jsonl",
        help="Path to write the corpus JSONL file.",
    )
    parser.add_argument(
        "--out_json",
        default="",
        help="Optional path to write the corpus JSON array file.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print progress while building the corpus.",
    )
    parser.add_argument(
        "--log-every",
        type=int,
        default=0,
        help="If set, emit progress every N rows.",
    )
    parser.add_argument(
        "--tqdm",
        action="store_true",
        help="Use a tqdm progress bar instead of log lines.",
    )
    parser.add_argument(
        "--orth-expand",
        nargs="*",
        default=[],
        help=(
            "Generate extra rows with labels mapped to these orthographies "
            "(e.g. POTIGUARA TUPINAMBA SEM_DIACRITICO)."
        ),
    )
    parser.add_argument(
        "--orth-expand-all",
        action="store_true",
        help="Generate extra rows for all known orthographies (excluding NAVARRO).",
    )
    parser.add_argument(
        "--label-from-annotated",
        action="store_true",
        help="Use annotated string to derive label when label is missing (faster).",
    )
    parser.add_argument(
        "--include-synthetic",
        action="store_true",
        help="Include synthetic sources in the corpus output.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    orth_list = _normalize_orth_list(args.orth_expand, args.orth_expand_all)
    tupi_mapper = None
    if orth_list:
        try:
            tupi_path = (ROOT / ".." / "nhe-enga" / "tupi").resolve()
            if str(tupi_path) not in sys.path:
                sys.path.insert(0, str(tupi_path))
            from tupi.tupi import TupiAntigo
        except Exception as exc:
            print(f"[corpus] failed to import TupiAntigo: {exc}")
            orth_list = []
        else:
            tupi_mapper = TupiAntigo()
    try:
        from tqdm import tqdm  # type: ignore
    except ModuleNotFoundError:
        tqdm = None
        if args.tqdm:
            print("[corpus] tqdm requested but not installed; falling back to logs.")
    out_jsonl_path = Path(args.out_jsonl) if args.out_jsonl else None
    out_json_path = Path(args.out_json) if args.out_json else None
    if out_jsonl_path is not None and not out_jsonl_path.is_absolute():
        out_jsonl_path = ROOT / out_jsonl_path
    if out_json_path is not None and not out_json_path.is_absolute():
        out_json_path = ROOT / out_json_path
    if out_jsonl_path is not None:
        out_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    if out_json_path is not None:
        out_json_path.parent.mkdir(parents=True, exist_ok=True)

    jsonl_f = None
    json_f = None
    first_json = True
    if out_jsonl_path is not None:
        jsonl_f = out_jsonl_path.open("w", encoding="utf-8")
    if out_json_path is not None:
        json_f = out_json_path.open("w", encoding="utf-8")
        json_f.write("[\n")

    sources = list(
        _iter_primary_sources(
            debug=args.debug,
            include_synthetic=args.include_synthetic,
        )
    )
    total_size = 0
    unknown_sources = []
    for name, _expr, _label, size in sources:
        if size is None:
            unknown_sources.append(name)
        else:
            total_size += size * (1 + len(orth_list))

    pbar = None
    if args.tqdm and tqdm is not None:
        total = total_size if not unknown_sources else None
        pbar = tqdm(total=total, desc="corpus", unit="rows")
        if unknown_sources and args.debug:
            print(f"[corpus] tqdm total unknown for: {unknown_sources}")

    skipped = 0
    emitted = 0
    variants = 0
    for name, expressions, corpus_label, size in sources:
        if args.debug:
            size_str = str(size) if size is not None else "unknown"
            type_str = type(expressions).__name__
            print(
                f"[corpus] source={name} corpus={corpus_label} type={type_str} size={size_str} "
                f"at {time.strftime('%H:%M:%S')}"
            )
        source_start = time.perf_counter()
        source_rows = 0
        source_emitted = 0
        source_skipped = 0
        source_missing_label = 0
        source_variants = 0
        time_annotated = 0.0
        time_label = 0.0
        if callable(expressions):
            if args.debug:
                print(f"[corpus] building source={name} (callable) ...")
            t0 = time.perf_counter()
            expressions = expressions()
            if args.debug:
                dt = time.perf_counter() - t0
                print(f"[corpus] built source={name} in {dt:.3f}s")
        for idx, expr in enumerate(expressions):
            t_annot = time.perf_counter()
            annotated = _get_annotated(expr)
            time_annotated += time.perf_counter() - t_annot
            if not annotated:
                skipped += 1
                source_skipped += 1
                continue
            row: dict[str, object] = {
                "source": name,
                "corpus": corpus_label,
                "index": idx,
                "anotated": annotated,
            }
            t_label = time.perf_counter()
            label = _get_label(
                expr,
                annotated=annotated,
                prefer_annotated=args.label_from_annotated,
            )
            time_label += time.perf_counter() - t_label
            if label:
                row["label"] = label
            else:
                source_missing_label += 1
            if orth_list:
                row["orth"] = "NAVARRO"
                row["orth_source"] = "NAVARRO"
            if jsonl_f is not None:
                jsonl_f.write(json.dumps(row, ensure_ascii=False) + "\n")
            if json_f is not None:
                if not first_json:
                    json_f.write(",\n")
                json_f.write(json.dumps(row, ensure_ascii=False))
                first_json = False
            emitted += 1
            source_emitted += 1
            source_rows += 1
            if pbar is not None:
                pbar.update(1)
            elif args.log_every and emitted % args.log_every == 0:
                elapsed = time.perf_counter() - source_start
                rate = emitted / elapsed if elapsed > 0 else 0.0
                print(f"[corpus] rows={emitted} skipped={skipped} rate={rate:.1f}/s")
            if orth_list and tupi_mapper is not None:
                base_label = label or strip_tags_to_surface(annotated)
                for orth in orth_list:
                    try:
                        mapped_annotated = tupi_mapper.map_orthography(
                            annotated, orth=orth
                        )
                        mapped_label = strip_tags_to_surface(mapped_annotated)
                    except Exception as exc:
                        if args.debug:
                            print(f"[corpus] orth map failed {orth}: {exc}")
                        continue
                    if not mapped_label or mapped_label == base_label:
                        continue
                    variant = {
                        "source": name,
                        "corpus": corpus_label,
                        "index": idx,
                        "anotated": mapped_annotated,
                        "label": mapped_label,
                        "anotated_canon": annotated,
                        "label_canon": base_label,
                        "orth": orth,
                        "orth_source": "NAVARRO",
                    }
                    if jsonl_f is not None:
                        jsonl_f.write(json.dumps(variant, ensure_ascii=False) + "\n")
                    if json_f is not None:
                        json_f.write(",\n")
                        json_f.write(json.dumps(variant, ensure_ascii=False))
                    first_json = False
                    emitted += 1
                    variants += 1
                    source_variants += 1
                    if pbar is not None:
                        pbar.update(1)
                    elif args.log_every and emitted % args.log_every == 0:
                        elapsed = time.perf_counter() - source_start
                        rate = emitted / elapsed if elapsed > 0 else 0.0
                        print(
                            f"[corpus] rows={emitted} skipped={skipped} rate={rate:.1f}/s"
                        )
        if args.debug:
            print(
                f"[corpus] done source={name} rows={source_rows} emitted={source_emitted} "
                f"skipped={source_skipped} missing_label={source_missing_label} "
                f"variants={source_variants} took={time.perf_counter() - source_start:.3f}s "
                f"annotated_time={time_annotated:.3f}s label_time={time_label:.3f}s"
            )

    if json_f is not None:
        json_f.write("\n]\n")
        json_f.close()
    if jsonl_f is not None:
        jsonl_f.close()
    if pbar is not None:
        pbar.close()

    if out_jsonl_path is not None:
        print(f"Wrote {emitted} rows to {out_jsonl_path}.")
    if out_json_path is not None:
        print(f"Wrote {emitted} rows to {out_json_path}.")
    if variants:
        print(f"Wrote {variants} orthography variants.")
    if skipped:
        print(f"Skipped {skipped} expressions without annotated text.")
    if emitted == 0:
        print("Warning: corpus is empty.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
