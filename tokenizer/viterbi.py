# --- Drop-in notebook cell: Viterbi-based canonicalizer (no neural training) ---
# Uses your existing files:
#   - canonical_io.jsonl: for morpheme bigram/unigram probabilities AND true P(T|M) counts
#   - annotated_tokens.json: for M#### -> morpheme surface strings (lexicon)
#   - annotated_tags.json / annotated_subtags.json: for T/S ids and tag expansions
#   - annotated_token_pairs.json (optional): fallback prior if canonical counts missing
#
# Produces: canonical stream for new inputs: "M#### T#### (optional)" tokens.
#
# Notes:
# - This baseline does NOT handle heavy spelling noise (edit distance) yet.
# - It segments within whitespace tokens + optionally tries to join adjacent tokens if that improves score.
# - It ignores S subtags by default for speed; you can add them back later.

import json, os, re, math
from collections import Counter, defaultdict
from pathlib import Path

data_base_path = "/Users/kian/code/oldtupicorpus/tokenizer/output"
CORPUS_JSONL = data_base_path + "/corpus.jsonl"
CORPUS_JSON = data_base_path + "/corpus.json"
CANONICAL_IO = data_base_path + "/canonical_io.jsonl"
TOKENS_JSON = data_base_path + "/annotated_tokens.json"  # M######
TAGS_JSON = data_base_path + "/annotated_tags.json"  # T######
SUBTAGS_JSON = data_base_path + "/annotated_subtags.json"  # S######
TOKEN_PAIRS_JSON = (
    data_base_path + "/annotated_token_pairs.json"
)  # (value, tag) list; optional fallback
VARIANT_MAP_JSON = data_base_path + "/annotated_token_variants.json"

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

print(
    "Exists?",
    *(
        os.path.exists(p)
        for p in [
            CORPUS_JSONL,
            CORPUS_JSON,
            CANONICAL_IO,
            TOKENS_JSON,
            TAGS_JSON,
            SUBTAGS_JSON,
            VARIANT_MAP_JSON,
        ]
    ),
)


def _read_first_corpus_row():
    if os.path.exists(CORPUS_JSONL):
        with open(CORPUS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    return json.loads(line)
        return None
    if os.path.exists(CORPUS_JSON):
        with open(CORPUS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data[0] if data else None
    return None


first_row = _read_first_corpus_row()
if first_row:
    print("sample keys:", first_row.keys())
    print("sample label:", str(first_row.get("label", ""))[:120])
    print("sample anotated:", str(first_row.get("anotated", ""))[:120])


# --------------------------
# Helpers: load registries
# --------------------------
def load_registry_id_to_value(path: str, value_key: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    return {it["id"]: it[value_key] for it in items}


def load_registry_value_to_id(path: str, value_key: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    return {it[value_key]: it["id"] for it in items}


M_ID_TO_SURF = load_registry_id_to_value(
    TOKENS_JSON, "value"
)  # M#### -> surface morpheme string
T_ID_TO_TAG = load_registry_id_to_value(TAGS_JSON, "tag")  # T#### -> "[TAG:...]" (full)
TAG_TO_T_ID = load_registry_value_to_id(TAGS_JSON, "tag")
S_ID_TO_SUBTAG = load_registry_id_to_value(SUBTAGS_JSON, "subtag")
SUBTAG_TO_S_ID = load_registry_value_to_id(SUBTAGS_JSON, "subtag")

# Variant map: variant M -> canonical M (Navarro)
VARIANT_TO_CANON_ID = {}
if os.path.exists(VARIANT_MAP_JSON):
    with open(VARIANT_MAP_JSON, "r", encoding="utf-8") as f:
        items = json.load(f)
    for it in items:
        vid = it.get("variant_id")
        cid = it.get("canonical_id")
        if vid and cid and vid not in VARIANT_TO_CANON_ID:
            VARIANT_TO_CANON_ID[vid] = cid

# Build surface->possible M IDs (usually 1-1, but keep general)
SURF_TO_M_IDS = defaultdict(list)
for mid, surf in M_ID_TO_SURF.items():
    SURF_TO_M_IDS[surf].append(mid)

print("Lexicon size (M IDs):", len(M_ID_TO_SURF))
print("Unique morpheme strings:", len(SURF_TO_M_IDS))


# --------------------------
# Read canonical_io.jsonl and build morpheme LM + true tag stats
# --------------------------
def iter_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


# We build LM over M-tokens only (drop T/S) because segmentation depends on morpheme sequence.
# For tags we compute P(T|M) from true sequences, and also the most frequent tag *sequence* per M.
M_unigram = Counter()
M_bigram = Counter()
M_occurrences = Counter()
M_TO_T_COUNTS = defaultdict(Counter)  # M -> Counter(T)
M_TO_TAGSEQ_COUNTS = defaultdict(Counter)  # M -> Counter(tuple[T...])
BOS = "<BOS>"
EOS = "<EOS>"

total_lines = 0
for ex in iter_jsonl(CANONICAL_IO):
    toks = ex["output"].split()
    # Parse M + attached T sequence per morpheme
    ms = []
    current_m = None
    current_tags = []

    def flush_current():
        if current_m is None:
            return
        ms.append(current_m)
        M_occurrences[current_m] += 1
        if current_tags:
            for tid in current_tags:
                M_TO_T_COUNTS[current_m][tid] += 1
        M_TO_TAGSEQ_COUNTS[current_m][tuple(current_tags)] += 1

    for tok in toks:
        if tok.startswith("M"):
            flush_current()
            current_m = tok
            current_tags = []
        elif tok.startswith("T"):
            if current_m is not None:
                current_tags.append(tok)
        else:
            # S-subtags are derived from T; skip for counting
            continue
    flush_current()

    if not ms:
        continue
    total_lines += 1
    seq = [BOS] + ms + [EOS]
    for m in ms:
        M_unigram[m] += 1
    for a, b in zip(seq, seq[1:]):
        M_bigram[(a, b)] += 1

print("LM trained on lines:", total_lines)
print("M unigram:", len(M_unigram), "M bigram:", len(M_bigram))
print(
    "Tag stats from canonical_io:", sum(sum(c.values()) for c in M_TO_T_COUNTS.values())
)


# --------------------------
# Optional fallback P(T|M) prior from token_pairs
# --------------------------
has_pairs = os.path.exists(TOKEN_PAIRS_JSON)
if has_pairs:
    with open(TOKEN_PAIRS_JSON, "r", encoding="utf-8") as f:
        pairs = json.load(f)
    # This file is usually UNIQUE pairs (not weighted). Use only to fill missing Ms.
    for p in pairs:
        surf = p["value"]
        tag = p["tag"]
        for mid in SURF_TO_M_IDS.get(surf, []):
            if mid in M_TO_T_COUNTS:
                continue
            tid = TAG_TO_T_ID.get(tag)
            if tid:
                M_TO_T_COUNTS[mid][tid] += 1
                M_TO_TAGSEQ_COUNTS[mid][(tid,)] += 1

print("Has token_pairs?", has_pairs)


def best_T_for_M(mid: str) -> str | None:
    """Return best single T#### for a given M####."""
    counts = M_TO_T_COUNTS.get(mid)
    if not counts:
        return None
    return max(counts.items(), key=lambda x: (x[1], x[0]))[0]


def best_tag_sequence_for_M(mid: str) -> tuple[str, ...]:
    """Return most frequent tag sequence (tuple of T####) for a given M####."""
    counts = M_TO_TAGSEQ_COUNTS.get(mid)
    if not counts:
        return ()
    return max(counts.items(), key=lambda x: (x[1], len(x[0]), x[0]))[0]


# --------------------------
# Optional: expand T -> S subtags
# --------------------------
def tag_to_subtags(tag: str) -> list[str]:
    inner = tag.strip()[1:-1]
    if not inner:
        return []
    return [p for p in inner.split(":") if p]


def subtags_for_T_id(tid: str) -> list[str]:
    tag = T_ID_TO_TAG.get(tid)
    if not tag:
        return []
    out = []
    for sub in tag_to_subtags(tag):
        sid = SUBTAG_TO_S_ID.get(sub)
        if sid:
            out.append(sid)
    return out


# --------------------------
# Scoring: smoothed log probs
# --------------------------
# Simple add-k smoothing for bigrams
K = 0.5
V = len(M_unigram) + 2  # + BOS/EOS


def logP_bigram(prev: str, cur: str) -> float:
    num = M_bigram[(prev, cur)] + K
    den = (M_unigram[prev] if prev not in (BOS, EOS) else total_lines) + K * V
    return math.log(num) - math.log(den)


def logP_unigram(m: str) -> float:
    # backoff unigram (also smoothed)
    num = M_unigram[m] + K
    den = sum(M_unigram.values()) + K * V
    return math.log(num) - math.log(den)


# --------------------------
# Viterbi segmenter for a single token (no spaces)
# --------------------------
# Build prefix index for fast candidate lookup
# We can segment strings like "xerera" into ["xe","rera"] if both morphemes exist.
prefix_map = defaultdict(
    list
)  # prefix -> list of morpheme strings that start with prefix
all_morphemes = list(SURF_TO_M_IDS.keys())
for s in all_morphemes:
    if s:
        prefix_map[s[0]].append(s)


def candidates_at(text: str, i: int) -> list[str]:
    """Return morpheme strings that match text starting at i."""
    if i >= len(text):
        return []
    cands = []
    first = text[i]
    for m in prefix_map.get(first, []):
        if text.startswith(m, i):
            cands.append(m)
    # prefer longer matches first (helps pruning)
    cands.sort(key=len, reverse=True)
    return cands


def viterbi_segment_word(word: str) -> list[str]:
    """
    Returns best segmentation as list of morpheme strings.
    Falls back to [word] if cannot segment.
    """
    n = len(word)
    # dp[i] = (score, prev_i, morpheme_str)
    # score is segmentation-internal; we use unigram as proxy inside a word.
    dp = [None] * (n + 1)
    dp[0] = (0.0, -1, None)

    for i in range(n):
        if dp[i] is None:
            continue
        base_score = dp[i][0]
        cands = candidates_at(word, i)
        for m in cands:
            j = i + len(m)
            # pick best M-id for this surface by unigram (in case multiple)
            # (normally 1)
            best_mid = max(SURF_TO_M_IDS[m], key=lambda mid: M_unigram[mid])
            score = base_score + logP_unigram(best_mid)
            cur = dp[j]
            if cur is None or score > cur[0]:
                dp[j] = (score, i, m)

    if dp[n] is None:
        return [word]

    # backtrack
    parts = []
    i = n
    while i > 0:
        score, prev_i, m = dp[i]
        parts.append(m)
        i = prev_i
    parts.reverse()
    return parts


# --------------------------
# Phrase-level: segment tokens + optional join across spaces
# --------------------------
def normalize_surface(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s


def word_to_mids(word: str) -> list[str]:
    """Segment one whitespace token into M-ids (best guess)."""
    seg = viterbi_segment_word(word)
    mids = []
    for m in seg:
        if m in SURF_TO_M_IDS:
            # choose most frequent M id for that surface
            mid = max(SURF_TO_M_IDS[m], key=lambda x: M_unigram[x])
            mids.append(mid)
        else:
            # OOV: passthrough as RAW marker with content (kept separate)
            mids.append(f"<RAW:{m}>")
    return mids


def score_mid_sequence(mids: list[str]) -> float:
    """Score a sequence of M ids (and RAW tokens) using bigram LM (RAW gets backoff)."""
    seq = [BOS] + mids + [EOS]
    s = 0.0
    prev = seq[0]
    for cur in seq[1:]:
        if cur.startswith("<RAW:"):
            # Penalize unknowns but don't kill it
            s += -8.0
        else:
            s += logP_bigram(prev if not prev.startswith("<RAW:") else BOS, cur)
        prev = cur
    return s


def _emit_canonical_from_mids(mids: list[str]) -> str:
    # Modes:
    # - "sequence": most frequent tag sequence per M from canonical_io
    # - "single": most frequent single tag per M
    # - "none": emit M only
    TAG_MODE = "sequence"
    INCLUDE_SUBTAGS = True

    out = []
    for m in mids:
        if m.startswith("<RAW:"):
            out.append(m)
            continue
        out.append(m)
        if TAG_MODE == "single":
            tid = best_T_for_M(m)
            if tid:
                out.append(tid)
                if INCLUDE_SUBTAGS:
                    out.extend(subtags_for_T_id(tid))
        elif TAG_MODE == "sequence":
            tags = best_tag_sequence_for_M(m)
            for tid in tags:
                out.append(tid)
                if INCLUDE_SUBTAGS:
                    out.extend(subtags_for_T_id(tid))

    return " ".join(out)


def _raw_from_token(tok: str) -> str:
    if tok.startswith("<RAW:") and tok.endswith(">"):
        return tok[len("<RAW:") : -1]
    if tok.startswith("<RAW:"):
        return tok[len("<RAW:") :]
    return tok


def _canonical_mid(mid: str) -> str:
    return VARIANT_TO_CANON_ID.get(mid, mid)


def _word_from_mids(mids: list[str], normalize: bool) -> str:
    parts = []
    for m in mids:
        if m.startswith("<RAW:"):
            parts.append(_raw_from_token(m))
            continue
        use_mid = _canonical_mid(m) if normalize else m
        parts.append(M_ID_TO_SURF.get(use_mid, use_mid))
    return "".join(parts)


def canonicalize_with_surfaces(
    text: str, allow_join_across_space: bool = True
) -> tuple[str, str, str]:
    text = normalize_surface(text)
    words = text.split()

    # First pass: segment each word independently
    mids_per_word = [word_to_mids(w) for w in words]

    # Optionally consider joining adjacent words if that yields a better morpheme sequence
    if allow_join_across_space and len(words) >= 2:
        i = 0
        new_mids = []
        while i < len(words):
            if i + 1 < len(words):
                w1, w2 = words[i], words[i + 1]
                mids_sep = mids_per_word[i] + mids_per_word[i + 1]
                score_sep = score_mid_sequence(mids_sep)

                joined = w1 + w2
                mids_join = word_to_mids(joined)
                score_join = score_mid_sequence(mids_join)

                raw_sep = sum(1 for m in mids_sep if m.startswith("<RAW:"))
                raw_join = sum(1 for m in mids_join if m.startswith("<RAW:"))
                allow_join = False
                if raw_join < raw_sep:
                    allow_join = True
                elif raw_join == 0 and raw_sep == 0:
                    allow_join = True

                if allow_join and score_join > score_sep + 0.5:
                    new_mids.extend(mids_join)
                    i += 2
                    continue
            new_mids.extend(mids_per_word[i])
            i += 1
        mids = new_mids
    else:
        mids = [m for sub in mids_per_word for m in sub]

    canon = _emit_canonical_from_mids(mids)
    surface_input = " ".join(
        _word_from_mids(mw, normalize=False) for mw in mids_per_word
    )
    surface_nav = " ".join(_word_from_mids(mw, normalize=True) for mw in mids_per_word)
    return canon, surface_input, surface_nav


def canonicalize_stats(text: str, allow_join_across_space: bool = True) -> str:
    canon, _surface_in, _surface_nav = canonicalize_with_surfaces(
        text, allow_join_across_space=allow_join_across_space
    )
    return canon


# --------------------------
# Utility: detokenize to surface (M only)
# --------------------------
def surface_from_canonical(canon: str) -> str:
    out = []
    for t in canon.split():
        if t.startswith("M"):
            out.append(M_ID_TO_SURF.get(t, t))
        elif t.startswith("<RAW:"):
            out.append(t[len("<RAW:") : -1] if t.endswith(">") else t)
    return " ".join(out)


# --------------------------
# Quick tests
# --------------------------
tests = [
    "amém",
    "tuba ta'yra Espírito Santo rera pupé",
    (str(first_row.get("label", "")) if first_row else ""),
    "xe rera",
    "xerera",
    "Kian xe rera",
    "aîpotar nde kûara",
    "ajpotar nde kûara",
]


for t in tests:
    if not t:
        continue
    canon, surf_in, surf_nav = canonicalize_with_surfaces(
        t, allow_join_across_space=True
    )
    print("\nIN:   ", t)
    print("CANON:", canon[:200], "..." if len(canon) > 200 else "")
    print("SURF_IN:  ", surf_in)
    print("SURF_NAV: ", surf_nav)
