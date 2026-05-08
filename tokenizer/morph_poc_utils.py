#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable


SPECIAL_TOKENS = ["<PAD>", "<BOS>", "<EOS>", "<UNK>", "<RAW>"]
CANONICAL_ID_RE = re.compile(r"^([MTS])(\d{6})$")


@dataclass(frozen=True)
class FactorizationConfig:
    drop_feature_prefixes: set[str] = field(default_factory=lambda: {"DEEPEST_NODE"})
    drop_features: set[str] = field(default_factory=lambda: {"DIRECT"})
    keep_root_feature: bool = True
    use_explicit_s_ids: bool = False

    def to_json(self) -> dict:
        return {
            "drop_feature_prefixes": sorted(self.drop_feature_prefixes),
            "drop_features": sorted(self.drop_features),
            "keep_root_feature": self.keep_root_feature,
            "use_explicit_s_ids": self.use_explicit_s_ids,
        }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_surface(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()


def load_jsonl(path: Path | str, limit: int | None = None) -> list[dict]:
    rows = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
            if limit is not None and len(rows) >= limit:
                break
    return rows


def iter_jsonl(path: Path | str) -> Iterable[dict]:
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(path: Path | str, rows: Iterable[dict]) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def load_json(path: Path | str, default=None):
    path = Path(path)
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path | str, obj: object) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def append_jsonl(path: Path | str, row: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_registry(
    path: Path | str, value_key: str
) -> tuple[list[dict], dict[str, str], dict[str, str]]:
    items = load_json(path, default=[])
    id_to_value = {
        item["id"]: item[value_key]
        for item in items
        if isinstance(item, dict) and "id" in item and value_key in item
    }
    value_to_id = {value: key for key, value in id_to_value.items()}
    return items, id_to_value, value_to_id


def _parse_canonical_id(token: str) -> tuple[str, str] | None:
    match = CANONICAL_ID_RE.fullmatch(token)
    if not match:
        return None
    return match.group(1), match.group(2)


def is_dropped_feature(feature: str, config: FactorizationConfig) -> bool:
    if feature == "ROOT":
        return not config.keep_root_feature
    if feature in config.drop_features:
        return True
    return any(feature.startswith(prefix) for prefix in config.drop_feature_prefixes)


def tag_to_grammar_features(tag: str, config: FactorizationConfig) -> list[str]:
    inner = tag.strip()
    if inner.startswith("[") and inner.endswith("]"):
        inner = inner[1:-1]
    parts = [part for part in inner.split(":") if part]
    return [part for part in parts if not is_dropped_feature(part, config)]


def canonical_ids_to_factorized_tokens(
    canonical_output: str,
    id_to_tag: dict[str, str],
    id_to_subtag: dict[str, str],
    config: FactorizationConfig,
) -> list[str]:
    out: list[str] = []
    for token in canonical_output.split():
        parsed = _parse_canonical_id(token)
        if parsed is None:
            out.append(token)
            continue
        kind, digits = parsed
        if kind == "M":
            out.append(f"<M:{digits}>")
        elif kind == "T":
            tag = id_to_tag.get(token)
            if tag is None:
                out.append(f"<T_UNKNOWN:{digits}>")
                continue
            out.extend(
                f"<G:{feature}>" for feature in tag_to_grammar_features(tag, config)
            )
        elif kind == "S" and config.use_explicit_s_ids:
            subtag = id_to_subtag.get(token)
            if subtag and not is_dropped_feature(subtag, config):
                out.append(f"<G:{subtag}>")
    return out


def build_morph_rows(
    corpus_rows: list[dict],
    canonical_rows: list[dict],
    id_to_tag: dict[str, str],
    id_to_subtag: dict[str, str],
    config: FactorizationConfig,
) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    missing_corpus_metadata = 0
    for i, canonical in enumerate(canonical_rows):
        corpus = corpus_rows[i] if i < len(corpus_rows) else {}
        if not corpus:
            missing_corpus_metadata += 1
        target_tokens = canonical_ids_to_factorized_tokens(
            canonical.get("output", ""), id_to_tag, id_to_subtag, config
        )
        row = {
            "input": normalize_surface(str(canonical.get("input", ""))),
            "target": " ".join(target_tokens),
            "source": corpus.get("source", ""),
            "corpus": corpus.get("corpus", ""),
            "orth": corpus.get("orth", "NAVARRO"),
            "index": corpus.get("index", i),
        }
        for key in ("orth_source", "label_canon", "surface", "label"):
            if key in corpus:
                row[key] = corpus[key]
        rows.append(row)

    stats = {
        "rows": len(rows),
        "missing_corpus_metadata": missing_corpus_metadata,
        "canonical_rows": len(canonical_rows),
        "corpus_rows": len(corpus_rows),
    }
    return rows, stats


def morph_vocab_from_rows(rows: list[dict]) -> dict:
    target_tokens = sorted(
        {tok for row in rows for tok in row.get("target", "").split()}
    )
    m_tokens = sorted(tok for tok in target_tokens if tok.startswith("<M:"))
    g_tokens = sorted(tok for tok in target_tokens if tok.startswith("<G:"))
    tokens = SPECIAL_TOKENS + [
        tok for tok in target_tokens if tok not in SPECIAL_TOKENS
    ]
    return {
        "special_tokens": SPECIAL_TOKENS,
        "tokens": tokens,
        "m_tokens": m_tokens,
        "g_tokens": g_tokens,
        "token_to_id": {tok: i for i, tok in enumerate(tokens)},
    }


def count_by(rows: Iterable[dict], key: str, default: str = "") -> dict[str, int]:
    counts = Counter(str(row.get(key, default) or default) for row in rows)
    return dict(sorted(counts.items()))


def summarize_corpus_rows(corpus_rows: list[dict]) -> dict:
    orth_variant_rows = 0
    for row in corpus_rows:
        orth = row.get("orth")
        if orth and orth != "NAVARRO":
            orth_variant_rows += 1
    return {
        "corpus_rows": len(corpus_rows),
        "historic_rows": sum(
            1 for row in corpus_rows if row.get("corpus") == "historic"
        ),
        "synthetic_rows": sum(
            1 for row in corpus_rows if row.get("corpus") == "synthetic"
        ),
        "orthographic_variant_rows": orth_variant_rows,
        "by_corpus": count_by(corpus_rows, "corpus"),
        "by_source": count_by(corpus_rows, "source"),
        "by_orth": count_by(corpus_rows, "orth", "NAVARRO"),
    }


def write_morph_dataset(
    morph_io_path: Path | str,
    morph_vocab_path: Path | str,
    morph_meta_path: Path | str,
    morph_rows: list[dict],
    corpus_rows: list[dict],
    build_config: dict,
    factorization_config: FactorizationConfig,
) -> tuple[dict, dict]:
    write_jsonl(morph_io_path, morph_rows)
    vocab = morph_vocab_from_rows(morph_rows)
    write_json(morph_vocab_path, vocab)

    input_chars = sorted({ch for row in morph_rows for ch in row.get("input", "")})
    meta = {
        "timestamp": utc_now_iso(),
        "build_config": build_config,
        "factorization_config": factorization_config.to_json(),
        "row_count": len(morph_rows),
        "unique_input_char_count": len(input_chars),
        "m_token_count": len(vocab["m_tokens"]),
        "g_token_count": len(vocab["g_tokens"]),
        "dropped_features": {
            "drop_feature_prefixes": sorted(factorization_config.drop_feature_prefixes),
            "drop_features": sorted(factorization_config.drop_features),
            "keep_root_feature": factorization_config.keep_root_feature,
        },
        "counts": summarize_corpus_rows(corpus_rows),
    }
    write_json(morph_meta_path, meta)
    return vocab, meta


class MorphBaseline:
    def __init__(
        self,
        id_to_morpheme: dict[str, str],
        id_to_tag: dict[str, str],
        canonical_rows: list[dict],
        token_variants: list[dict],
        factorization_config: FactorizationConfig,
    ) -> None:
        self.id_to_morpheme = id_to_morpheme
        self.id_to_tag = id_to_tag
        self.config = factorization_config
        self.m_frequency: Counter[str] = Counter()
        self.m_to_featureseq_counts: dict[str, Counter[tuple[str, ...]]] = defaultdict(
            Counter
        )
        self.variant_id_to_canonical_id: dict[str, str] = {}
        self.surface_candidates: dict[str, set[str]] = defaultdict(set)
        self.known_surfaces_by_first: dict[str, list[str]] = defaultdict(list)
        self.stale_variant_rows = 0
        self._build_surface_candidates(token_variants)
        self._build_observed_feature_stats(canonical_rows)

    def _build_observed_feature_stats(self, canonical_rows: list[dict]) -> None:
        for row in canonical_rows:
            current_m = None
            current_features: list[str] = []

            def flush() -> None:
                if current_m is None:
                    return
                canonical_m = self.variant_id_to_canonical_id.get(current_m, current_m)
                self.m_frequency[canonical_m] += 1
                self.m_to_featureseq_counts[canonical_m][tuple(current_features)] += 1

            for token in str(row.get("output", "")).split():
                if token.startswith("M"):
                    flush()
                    current_m = token
                    current_features = []
                elif token.startswith("T") and current_m is not None:
                    tag = self.id_to_tag.get(token)
                    if tag:
                        current_features.extend(
                            tag_to_grammar_features(tag, self.config)
                        )
            flush()

    def _build_surface_candidates(self, token_variants: list[dict]) -> None:
        for mid, surface in self.id_to_morpheme.items():
            if surface:
                self.surface_candidates[surface].add(mid)

        for item in token_variants:
            variant = item.get("variant")
            canonical_id = item.get("canonical_id")
            variant_id = item.get("variant_id")
            target_id = None
            if canonical_id in self.id_to_morpheme:
                target_id = canonical_id
            elif variant_id in self.id_to_morpheme:
                target_id = variant_id
            else:
                self.stale_variant_rows += 1
            if variant and target_id:
                self.surface_candidates[variant].add(target_id)
            if variant_id in self.id_to_morpheme and target_id:
                self.variant_id_to_canonical_id[variant_id] = target_id

        for surface in self.surface_candidates:
            self.known_surfaces_by_first[surface[0]].append(surface)
        for first, surfaces in self.known_surfaces_by_first.items():
            surfaces.sort(key=lambda value: (len(value), value), reverse=True)

    def _best_mid_for_surface(self, surface: str) -> str | None:
        mids = self.surface_candidates.get(surface)
        if not mids:
            return None
        return max(
            mids,
            key=lambda mid: (
                self.m_frequency[mid],
                len(self.id_to_morpheme.get(mid, "")),
                mid,
            ),
        )

    def _longest_match_at(self, word: str, index: int) -> tuple[str, str] | None:
        for surface in self.known_surfaces_by_first.get(word[index], []):
            if word.startswith(surface, index):
                mid = self._best_mid_for_surface(surface)
                if mid:
                    return surface, self.variant_id_to_canonical_id.get(mid, mid)
        return None

    def _segment_word(self, word: str) -> list[str]:
        pieces: list[str] = []
        raw_buffer: list[str] = []
        i = 0

        def flush_raw() -> None:
            if raw_buffer:
                pieces.append("<RAW:" + "".join(raw_buffer) + ">")
                raw_buffer.clear()

        while i < len(word):
            match = self._longest_match_at(word, i)
            if match is None:
                raw_buffer.append(word[i])
                i += 1
                continue
            flush_raw()
            surface, mid = match
            pieces.append(mid)
            i += len(surface)
        flush_raw()
        return pieces

    def _best_feature_sequence(self, mid: str) -> tuple[str, ...]:
        counts = self.m_to_featureseq_counts.get(mid)
        if not counts:
            return ()
        return max(counts.items(), key=lambda item: (item[1], len(item[0]), item[0]))[0]

    def tokenize(self, text: str) -> list[str]:
        text = normalize_surface(text)
        output: list[str] = []
        for word in text.split(" ") if text else []:
            for piece in self._segment_word(word):
                if piece.startswith("<RAW:"):
                    output.append(piece)
                    continue
                output.append(f"<M:{piece[1:]}>")
                output.extend(
                    f"<G:{feature}>" for feature in self._best_feature_sequence(piece)
                )
        return output

    def tokenize_batch(self, texts: list[str]) -> list[list[str]]:
        return [self.tokenize(text) for text in texts]

    @staticmethod
    def raw_rate(tokens: list[str]) -> float:
        morpheme_like = [
            tok for tok in tokens if tok.startswith("<M:") or tok.startswith("<RAW:")
        ]
        if not morpheme_like:
            return 0.0
        return sum(1 for tok in morpheme_like if tok.startswith("<RAW:")) / len(
            morpheme_like
        )


def inspect_tokens(tokens: list[str], id_to_morpheme: dict[str, str]) -> list[dict]:
    groups: list[dict] = []
    current: dict | None = None

    def flush() -> None:
        nonlocal current
        if current is not None:
            groups.append(current)
            current = None

    for token in tokens:
        if token.startswith("<M:") and token.endswith(">"):
            flush()
            mid = "M" + token[3:-1]
            current = {
                "token": token,
                "surface": id_to_morpheme.get(mid, mid),
                "grammar": [],
                "raw": False,
            }
        elif token.startswith("<RAW:") and token.endswith(">"):
            flush()
            groups.append(
                {
                    "token": token,
                    "surface": token[5:-1],
                    "grammar": [],
                    "raw": True,
                }
            )
        elif token.startswith("<G:") and token.endswith(">"):
            if current is None:
                current = {"token": None, "surface": None, "grammar": [], "raw": False}
            current["grammar"].append(token[3:-1])
        else:
            flush()
            groups.append(
                {"token": token, "surface": token, "grammar": [], "raw": False}
            )
    flush()
    return groups


def token_prf(pred: list[str], gold: list[str]) -> tuple[float, float, float]:
    pred_counter = Counter(pred)
    gold_counter = Counter(gold)
    overlap = sum((pred_counter & gold_counter).values())
    precision = overlap / max(1, sum(pred_counter.values()))
    recall = overlap / max(1, sum(gold_counter.values()))
    f1 = (
        0.0
        if precision + recall == 0
        else 2 * precision * recall / (precision + recall)
    )
    return precision, recall, f1


def token_accuracy(pred: list[str], gold: list[str]) -> float:
    denom = max(len(pred), len(gold), 1)
    return sum(1 for a, b in zip(pred, gold) if a == b) / denom


def filter_token_type(tokens: list[str], prefix: str) -> list[str]:
    return [tok for tok in tokens if tok.startswith(prefix)]


def evaluate_prediction_fn(
    name: str,
    pred_fn: Callable[[str], list[str]],
    examples: list[dict],
) -> dict:
    exact = []
    accuracy = []
    token_f1 = []
    token_precision = []
    token_recall = []
    m_precision = []
    m_recall = []
    m_f1 = []
    g_precision = []
    g_recall = []
    g_f1 = []
    raw_rates = []

    for row in examples:
        gold = str(row["target"]).split()
        pred = pred_fn(str(row["input"]))
        exact.append(float(pred == gold))
        accuracy.append(token_accuracy(pred, gold))
        p, r, f1 = token_prf(pred, gold)
        token_precision.append(p)
        token_recall.append(r)
        token_f1.append(f1)
        m_p, m_r, m_score = token_prf(
            filter_token_type(pred, "<M:"), filter_token_type(gold, "<M:")
        )
        g_p, g_r, g_score = token_prf(
            filter_token_type(pred, "<G:"), filter_token_type(gold, "<G:")
        )
        m_precision.append(m_p)
        m_recall.append(m_r)
        m_f1.append(m_score)
        g_precision.append(g_p)
        g_recall.append(g_r)
        g_f1.append(g_score)
        raw_rates.append(MorphBaseline.raw_rate(pred))

    n = len(examples)
    return {
        "model": name,
        "n": n,
        "exact": sum(exact) / max(1, n),
        "token_accuracy": sum(accuracy) / max(1, n),
        "token_precision": sum(token_precision) / max(1, n),
        "token_recall": sum(token_recall) / max(1, n),
        "token_f1": sum(token_f1) / max(1, n),
        "m_precision": sum(m_precision) / max(1, n),
        "m_recall": sum(m_recall) / max(1, n),
        "m_f1": sum(m_f1) / max(1, n),
        "g_precision": sum(g_precision) / max(1, n),
        "g_recall": sum(g_recall) / max(1, n),
        "g_f1": sum(g_f1) / max(1, n),
        "raw_rate": sum(raw_rates) / max(1, n),
    }


def format_metrics_table(metrics: list[dict]) -> str:
    headers = ["model", "exact", "token_acc", "token_f1", "m_f1", "g_f1", "raw_rate"]
    rows = [headers]
    for metric in metrics:
        rows.append(
            [
                str(metric.get("model", "")),
                f"{metric.get('exact', 0.0):.3f}",
                f"{metric.get('token_accuracy', 0.0):.3f}",
                f"{metric.get('token_f1', 0.0):.3f}",
                f"{metric.get('m_f1', 0.0):.3f}",
                f"{metric.get('g_f1', 0.0):.3f}",
                f"{metric.get('raw_rate', 0.0):.3f}",
            ]
        )
    widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    lines = []
    for row in rows:
        lines.append("  ".join(value.ljust(widths[i]) for i, value in enumerate(row)))
    return "\n".join(lines)


def mismatch_summary(pred: list[str], gold: list[str], max_items: int = 8) -> str:
    if pred == gold:
        return "exact match"
    parts = []
    for i, (p_tok, g_tok) in enumerate(zip(pred, gold)):
        if p_tok != g_tok:
            parts.append(f"@{i}: pred={p_tok} gold={g_tok}")
            if len(parts) >= max_items:
                break
    if len(pred) != len(gold) and len(parts) < max_items:
        parts.append(f"length pred={len(pred)} gold={len(gold)}")
    return "; ".join(parts) if parts else "same prefix, different length"
