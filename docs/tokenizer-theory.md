# Tokenizer Theory And Current Passes

Last updated: 2026-05-11

This document explains the tokenizer/canonicalizer as it exists now. It is not a
general NLP tokenizer like BPE or WordPiece. It is closer to a supervised
morphological transduction pipeline:

```text
surface Old Tupi text
  -> segmented morpheme identities
  -> grammatical feature tags
  -> optional canonical/lexical representation
```

The current system has two layers:

- Deterministic data builders in `tokenizer/*.py`.
- A proof-of-concept ML notebook in `tokenizer/notebooks/morph_tokenizer_poc.ipynb`
  that turns those deterministic artifacts into a factorized training target,
  baselines, and a small neural seq2seq experiment.

## Main Idea

The repo already contains a hand-built linguistic analysis in the Pydicate source
expressions under `historic/` and `synthetic/`. The tokenizer does not discover
Old Tupi morphology from raw text from scratch. Instead, it treats those
Pydicate expressions as a teacher.

The learning problem is:

```text
input:  rendered surface text
target: a linearized analysis derived from the source expression
```

For example, an input line like:

```text
tuba ta'yra Espirito Santo rera pupe
```

is mapped to a target sequence made from stable IDs:

```text
M000... T000... S000... M000... ...
```

or, in the notebook's factorized representation:

```text
<M:000...> <G:NOUN> <G:SUBSTANTIVE_SUFFIX> ...
```

The core computer-science move is to turn a rich tree-ish linguistic object into
a sequence. Once the target is a sequence, normal sequence models and dynamic
programming baselines can operate on it.

## Vocabulary

- `surface`: the plain rendered text a model would see as input.
- `annotated`: a rendered string with bracketed tags attached to morphemes.
- `M######`: stable ID for an observed morpheme surface.
- `T######`: stable ID for a full bracket tag, such as `[POSTPOSITION]` or a
  richer colon-separated tag.
- `S######`: stable ID for one subtag created by splitting a `T` tag on `:`.
- `<M:######>`: notebook factorized morpheme token derived from an `M######` ID.
- `<G:FEATURE>`: notebook grammar feature derived from a `T######` tag.
- `<LEX:NAVARRO:...>`: optional Navarro dictionary lexeme token used by the
  notebook lexicon-aware baseline and augmentation.
- `<RAW:...>`: fallback chunk for text that cannot be segmented into known
  morphemes or lexemes.

## Pass 0: Linguistic Source Data

Files:

- `historic/*.tu.py`
- `synthetic/*.py`
- `historic/primary_sources.py`
- `synthetic/primary_sources.py`
- `historic/lexicon.tu.py`

Goal:

Create the supervised teacher signal. Each source expression can render a plain
surface string and, when available, an annotated string with morpheme-level tags.

Theory:

This is supervised learning with a symbolic teacher. The gold labels come from
the Pydicate analysis, not from an unsupervised statistical tokenizer. That is
good because the model can learn linguistically meaningful targets. It is risky
because the model inherits every inconsistency, shortcut, and ambiguity in the
hand-built analysis.

Assumptions:

- The Pydicate expressions are the highest-quality available analysis.
- A rendered line and its annotated form are aligned enough to become a training
  example.
- Synthetic data is useful, but it can dominate the distribution if included at
  large scale.

## Pass 1: Build Corpus Rows

File:

- `tokenizer/build_corpus_json.py`

Typical command:

```bash
python3 tokenizer/build_corpus_json.py --out_jsonl tokenizer/output/corpus.jsonl
```

Output:

- `tokenizer/output/corpus.jsonl`

Each row is roughly:

```json
{
  "source": "araujo_catecismo_1686",
  "corpus": "historic",
  "index": 0,
  "anotated": "...[TAG]...",
  "label": "plain surface text"
}
```

What happens:

1. Historic sources are discovered from `historic/primary_sources.py`.
2. Synthetic sources are optionally imported from `synthetic.primary_sources`.
3. For each expression, the script tries several methods/attributes to get the
   annotated string.
4. It gets a surface label from `label`, `surface`, `orth`, or an unannotated
   eval call.
5. If requested, it generates orthographic variants through `../nhe-enga/tupi`.
6. Variant rows keep both the variant annotated string and the canonical
   Navarro-side annotated string.

Theory:

This pass is dataset construction and data augmentation. Orthographic expansion
is not a separate model; it creates extra supervised examples so later models
see the same analysis under multiple spelling conventions.

Assumptions:

- The annotation can be flattened into text without losing the alignment needed
  by later passes.
- Orthographic mapping preserves morpheme boundaries well enough that variant
  rows can point back to a canonical row.
- Rows without annotated text are not useful for this supervised target and are
  skipped.

Failure modes:

- If annotation extraction changes, downstream IDs and targets can change.
- Orthographic expansion can create a much larger synthetic/variant-heavy corpus
  than the historic material.
- Labels derived directly from annotated strings may be faster but can preserve
  artifacts from annotation rather than independent surface rendering.

## Pass 2: Build Stable Registries And Canonical IO

File:

- `tokenizer/rawgrammarpair.py`

Typical command:

```bash
python3 tokenizer/rawgrammarpair.py \
  --in_json tokenizer/output/corpus.jsonl \
  --out_dir tokenizer/output
```

Outputs:

- `tokenizer/output/canonical_io.jsonl`
- `tokenizer/output/annotated_tokens.json`
- `tokenizer/output/annotated_tags.json`
- `tokenizer/output/annotated_subtags.json`
- `tokenizer/output/annotated_token_pairs.json`
- `tokenizer/output/annotated_token_variants.json`

What happens:

1. The script tokenizes an annotated string into surface chunks and bracket tags.
2. Tags before a surface attach to the next surface.
3. Tags after a surface attach to the previous surface.
4. Unattached trailing tags are dropped.
5. Tags containing configured excluded substrings are dropped. The current
   defaults are `DIRECT` and `ROOT`.
6. Every observed morpheme surface gets an `M######` ID.
7. Every retained full tag gets a `T######` ID.
8. Every subpart of a retained full tag gets an `S######` ID.
9. A row is written as:

```json
{
  "input": "plain surface text",
  "output": "M000001 T000001 S000001 ..."
}
```

Theory:

This is a linearization pass. It converts an annotated morphology analysis into
a target language that a model can predict. The target language mixes lexical
identity (`M`) and grammatical analysis (`T` and `S`).

The stable registries are a vocabulary. They keep IDs stable across runs by
loading previous JSON registries before assigning new IDs. That is useful for
reproducibility and checkpoints, but it means a registry file is not a clean
frequency inventory of only the current corpus. Old IDs can persist.

Assumptions:

- Local adjacency is enough to attach tags to the right morpheme.
- A sequence of `M/T/S` IDs is an acceptable representation of the analysis.
- `S` subtags are derived information, not independent annotations.
- Dropping noisy/debug tags improves the target, but it can also remove
  linguistically useful information if the exclude list is too broad.

Failure modes:

- Ambiguous tag attachment is resolved by local position, not syntax.
- Default exclusion of tags containing `ROOT` means many root tags do not become
  `T` output tokens in the canonical IO.
- Stable registries can hide the difference between current vocabulary and
  historical vocabulary.

## Pass 3: Optional DSL Reconstruction

Files:

- `tokenizer/compile_to_dsl.py`
- `tokenizer/dsl_runtime.py`

Typical command:

```bash
python3 tokenizer/compile_to_dsl.py \
  --in_jsonl tokenizer/output/canonical_io.jsonl \
  --out_jsonl tokenizer/output/canonical_dsl.jsonl \
  --no-repl
```

Outputs:

- `tokenizer/output/canonical_dsl.jsonl`
- `tokenizer/output/canonical_dsl_meta.json`

What happens:

1. `M` IDs are decoded back to morpheme surfaces.
2. `T` IDs are decoded back to full bracket tags.
3. `S` IDs are skipped because they are derivable from `T`.
4. The annotated string is converted to a shallow AST: one node per morpheme.
5. A best-effort Pydicate-like expression is emitted.
6. A literal `Tok(...)` fallback is emitted for every morpheme so the annotated
   surface can still be preserved.
7. Optional structure metadata groups prefixes, roots, and suffixes and records
   a light state trace.

Theory:

This is decoding into an intermediate representation. It asks: "If a model
predicts the canonical ID stream, can we reconstruct something closer to the
source DSL?" It is conservative on purpose. It uses Pydicate constructors only
when a clear part-of-speech tag is present; affixes and uncertain tags fall back
to `Tok(...)`.

Assumptions:

- The canonical ID stream contains enough information to reconstruct useful
  annotated text.
- Full Pydicate reconstruction is harder than sequence prediction, so literal
  fallback must remain available.
- POS tags can choose constructors, but they do not fully recover syntax.

## Pass 4: Notebook Factorization

Files:

- `tokenizer/morph_poc_utils.py`
- `tokenizer/notebooks/morph_tokenizer_poc.ipynb`
- `tokenizer/notebooks/README.md`

Primary generated files:

- `tokenizer/output/morph_io.jsonl`
- `tokenizer/output/morph_vocab.json`
- `tokenizer/output/morph_dataset_meta.json`
- `tokenizer/output/morph_experiment_history.jsonl`
- `tokenizer/output/morph_tokenizer_poc.pt`

What happens:

The notebook starts from `corpus.jsonl`, `canonical_io.jsonl`, and the registries.
It converts the canonical target from raw IDs into a factorized target:

```text
M000123 T000045 S000010 ...
```

becomes:

```text
<M:000123> <G:POSTPOSITION> <G:DATIVE> ...
```

The config currently drops `DEEPEST_NODE*` and `DIRECT`, keeps `ROOT` if present,
and does not use explicit `S` IDs by default.

Theory:

This is feature factorization. Instead of asking a model to learn a huge number
of opaque full-tag IDs, the notebook splits tags into reusable grammatical
features. This should reduce sparsity:

- A rare full tag may appear only a few times.
- Its pieces, such as `POSTPOSITION`, `DATIVE`, or `NOUN`, appear in many places.
- A model can learn those reusable pieces even when a full combination is rare.

The tradeoff is that feature order and grouping become less explicit. `<G:NOUN>
<G:ROOT>` tells you useful things, but it is less precise than the original full
tag if multiple analyses could share the same feature bag.

Current local snapshot read from `tokenizer/output/morph_dataset_meta.json`:

- `tokenizer/output/morph_dataset_meta.json` records `2,014,384` rows.
- Only `358` rows are historic in that snapshot.
- `2,014,026` rows are synthetic.
- `1,319,996` rows are orthographic variants.
- The snapshot reports `5,200` `<M:...>` tokens and `101` `<G:...>` tokens.

That distribution matters. A high score can mean "good at the synthetic verb
distribution" more than "good at arbitrary historic Old Tupi text."

## Pass 5: Navarro Lexical Prior

Files:

- `tokenizer/morph_poc_utils.py`
- `../nhe-enga` via `pydicate.dbexplorer.NavarroDB`

What happens:

The notebook can load Navarro dictionary entries and represent them as:

```text
<LEX:NAVARRO:noun:kaa> <G:NOUN> <G:ROOT>
```

It can also generate simple lexicon rows and root-plus-postposition combo rows.
The lexicon-aware baseline can choose between:

- observed corpus morphemes,
- orthographic variants,
- Navarro lexemes,
- raw fallback characters.

Theory:

This is a lexical prior. In ML terms, it injects structured external knowledge
into the hypothesis space. The model or baseline does not have to infer every
possible morpheme from corpus frequency alone; the dictionary says "this is a
plausible lexical unit."

The lexicon-aware baseline is a dynamic-programming segmenter over candidate
edges. Each edge has a score:

- observed morpheme frequency helps,
- Navarro root/postposition bonuses help,
- feature alignment helps,
- raw fallback is penalized,
- too many segments are mildly penalized.

This is closely related to Viterbi decoding or shortest-path search in a
weighted finite-state graph.

Assumptions:

- Navarro entries are useful but not always the same representation as the local
  Pydicate lexicon.
- Dictionary roots and postpositions should often beat arbitrary character
  chunks.
- RAW fallback is necessary, but a high RAW rate means coverage is poor.

## Pass 6: Baseline Tokenizers

Files:

- `tokenizer/morph_poc_utils.py`
- `tokenizer/viterbi.py`

Current notebook baselines:

- `MorphBaseline`
- `LexiconAwareMorphBaseline`

`MorphBaseline`:

1. Builds a map from known surfaces to known `M` IDs.
2. Uses orthographic variant mappings when available.
3. Greedily segments each word by longest known surface.
4. Picks the best `M` ID by observed frequency.
5. Emits the most frequent grammar feature sequence seen with that `M`.
6. Emits `<RAW:...>` chunks when no known surface matches.

`LexiconAwareMorphBaseline`:

1. Builds all possible observed, variant, Navarro, and raw edges at each
   character position.
2. Scores those edges.
3. Uses dynamic programming to find the best complete segmentation.
4. Emits `<M:...>`, `<LEX:...>`, `<G:...>`, and `<RAW:...>` tokens.
5. Can return a trace showing why each segment was selected.

`tokenizer/viterbi.py` is an older standalone notebook-style baseline. It builds
an `M`-token unigram/bigram language model from `canonical_io.jsonl`, estimates
tag probabilities from observed `M -> T` counts, segments words with Viterbi, and
optionally considers joining adjacent whitespace tokens.

Theory:

The baselines are important because they are interpretable. Before trusting a
neural model, check whether a deterministic segmenter plus dictionary prior
already solves the case. If the baseline fails, inspect whether the failure is
coverage, scoring, ambiguity, or a real gap in the linguistic source data.

## Pass 7: Neural Seq2Seq Experiment

File:

- `tokenizer/notebooks/morph_tokenizer_poc.ipynb`

What happens:

The notebook can train a small PyTorch encoder-decoder model:

- source side: character sequence from the surface input,
- target side: token sequence from `morph_io.jsonl`,
- encoder: bidirectional GRU,
- decoder: GRU with attention,
- training loss: cross-entropy over target tokens,
- training trick: teacher forcing,
- defaults in the notebook include small dimensions and a small number of
  epochs.

Theory:

This is sequence-to-sequence transduction. The model learns to translate from
characters to morphological tokens. Character input is useful because Old Tupi
forms are morphologically dense; morpheme boundaries may occur inside a written
word.

The factorized target makes the learning problem easier than predicting a single
opaque class for each full analysis. The model can get credit for predicting
the right morpheme but not every grammar feature, or the right grammar features
but a wrong segmentation.

Assumptions:

- There is enough training data for character patterns to generalize.
- Synthetic and orthographic-variant examples improve robustness rather than
  teaching the wrong distribution.
- A single target sequence is acceptable, even though real linguistic analysis
  can be ambiguous.
- Train/dev splitting over augmented data is good enough for iteration, but it
  may overestimate true generalization if variants of related examples appear in
  both splits.

Current status:

The neural model is explicitly a small local proof of concept. Treat it as an
experiment harness, not as the trusted production analyzer.

## Pass 8: Evaluation And Experiment History

Files:

- `tokenizer/morph_poc_utils.py`
- `tokenizer/notebooks/morph_tokenizer_poc.ipynb`
- `tokenizer/output/morph_experiment_history.jsonl`

Metrics:

- `exact`: predicted target sequence exactly equals the gold sequence.
- `token_accuracy`: aligned position-wise token accuracy.
- `token_f1`: multiset F1 over all predicted target tokens.
- `m_f1`: multiset F1 over only `<M:...>` morpheme tokens.
- `g_f1`: multiset F1 over only `<G:...>` grammar tokens.
- `raw_rate`: fraction of morpheme-like predictions that are `<RAW:...>`.

Theory:

Exact match is strict and useful, but it is not the whole story. In this domain,
partial correctness matters:

- A model can segment correctly but miss a grammar feature.
- A model can identify a feature but choose the wrong morpheme.
- A model can avoid crashes by emitting RAW, but too much RAW means it is not
  really analyzing the input.

For development, look at all of `exact`, `m_f1`, `g_f1`, and `raw_rate`.

## What The Current System Is Not

It is not:

- an unsupervised tokenizer,
- a BPE/WordPiece vocabulary learner,
- a complete syntactic parser,
- a guaranteed inverse of Pydicate source code,
- a production-ready neural analyzer,
- independent of the hand-built corpus.

It is:

- a deterministic artifact pipeline for supervised morphology data,
- a stable-ID representation of morphemes and tags,
- a factorized ML target for experiments,
- an interpretable baseline framework,
- a place to test whether more encoded Old Tupi data improves generalization.

## How To Debug A Tokenizer Failure

Use this order:

1. Check whether the source expression has an annotated form.
2. Check the row in `tokenizer/output/corpus.jsonl`.
3. Check the row in `tokenizer/output/canonical_io.jsonl`.
4. Decode the relevant `M`, `T`, and `S` IDs from the registry JSON files.
5. If using the notebook, inspect the `morph_io.jsonl` target.
6. Run `MorphBaseline` and `LexiconAwareMorphBaseline` on the string.
7. Inspect RAW chunks and dynamic-programming traces.
8. Only then judge the neural model.

Interpretation guide:

- Missing in `corpus.jsonl`: source discovery or annotation extraction problem.
- Present in corpus but wrong in `canonical_io.jsonl`: tag attachment,
  exclusion, or registry problem.
- Correct canonical IO but wrong factorized target: feature-drop or
  factorization problem.
- Baseline emits RAW: coverage, orthography, or lexicon matching problem.
- Lexicon baseline succeeds but neural fails: model/data/training problem.
- Baseline and neural both fail: probably source coverage or ambiguous analysis.

## Current Design Goals

Short term:

- Keep the deterministic corpus and registry builders reproducible.
- Make the notebook repeatable enough to compare runs.
- Use baselines as sanity checks before trusting neural metrics.
- Track RAW rate and historic-source behavior, not just aggregate metrics.

Medium term:

- Improve coverage with more hand-encoded historic data.
- Keep synthetic generation useful without letting it define the whole task.
- Tighten train/dev splitting so related augmented variants do not inflate
  evaluation.
- Decide which generated artifacts should be committed and which should remain
  local experiment outputs.

Long term:

- Learn a robust surface-to-morphology analyzer for Old Tupi.
- Preserve a path back to human-readable linguistic analyses.
- Use dictionary knowledge and corpus evidence together rather than choosing one
  or the other.
