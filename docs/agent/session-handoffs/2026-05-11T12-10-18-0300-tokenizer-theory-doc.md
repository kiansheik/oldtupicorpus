# Handoff: Tokenizer Theory Doc

## Goal

Write a teaching document explaining the current tokenizer/canonicalizer in
machine-learning and computer-science terms, pass by pass, for a reader who no
longer remembers how it works.

## Files Inspected

- `docs/agent/index.md`
- `docs/agent/current-state.md`
- `docs/agent/repo-map.md`
- `docs/agent/open-questions.md`
- `tokenizer/build_corpus_json.py`
- `tokenizer/rawgrammarpair.py`
- `tokenizer/compile_to_dsl.py`
- `tokenizer/dsl_runtime.py`
- `tokenizer/morph_poc_utils.py`
- `tokenizer/viterbi.py`
- `tokenizer/notebooks/README.md`
- `tokenizer/notebooks/morph_tokenizer_poc.ipynb`
- `tokenizer/output/canonical_io.jsonl`
- `tokenizer/output/annotated_tokens.json`
- `tokenizer/output/annotated_tags.json`
- `tokenizer/output/annotated_subtags.json`
- `tokenizer/output/morph_dataset_meta.json`
- `.gitignore`
- Relevant oldtupicorpus memory entry about source discovery and tokenizer
  helpers

## Files Changed

- `docs/tokenizer-theory.md`
- `docs/agent/current-state.md`
- `docs/agent/repo-map.md`
- `docs/agent/open-questions.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-05-11T12-10-18-0300-tokenizer-theory-doc.md`

## Commands Run

```bash
sed -n '1,220p' docs/agent/index.md
sed -n '1,220p' docs/agent/current-state.md
sed -n '1,240p' docs/agent/repo-map.md
sed -n '1,220p' docs/agent/open-questions.md
rg -n "tokenizer|morph_tokenizer|rawgrammarpair|build_corpus_json|compile_to_dsl|DSL|canonical|viterbi|morph_poc" /Users/kian/.codex/memories/MEMORY.md
sed -n '1,280p' tokenizer/build_corpus_json.py
sed -n '280,620p' tokenizer/build_corpus_json.py
sed -n '1,360p' tokenizer/rawgrammarpair.py
sed -n '360,760p' tokenizer/rawgrammarpair.py
sed -n '1,320p' tokenizer/compile_to_dsl.py
sed -n '320,760p' tokenizer/compile_to_dsl.py
sed -n '1,240p' tokenizer/dsl_runtime.py
sed -n '1,260p' tokenizer/morph_poc_utils.py
sed -n '260,620p' tokenizer/morph_poc_utils.py
sed -n '620,1040p' tokenizer/morph_poc_utils.py
sed -n '1040,1500p' tokenizer/morph_poc_utils.py
sed -n '1,320p' tokenizer/viterbi.py
sed -n '320,760p' tokenizer/viterbi.py
sed -n '1,260p' tokenizer/notebooks/README.md
rg -n "rawgrammarpair|build_corpus_json|compile_to_dsl|morph_io|morph_poc|tokenizer" tests tokenizer -g '*test.py' -g '*.py'
find tokenizer/output -maxdepth 1 -type f -print | sort
head -n 3 tokenizer/output/canonical_io.jsonl
head -n 5 tokenizer/output/annotated_tokens.json
head -n 5 tokenizer/output/annotated_tags.json
head -n 5 tokenizer/output/annotated_subtags.json
head -n 5 tokenizer/output/morph_io.jsonl 2>/dev/null || true
sed -n '1,120p' tokenizer/output/morph_dataset_meta.json 2>/dev/null || true
rg -n "FORCE_REBUILD|build_morph_rows|write_morph_dataset|MorphBaseline|LexiconAwareMorphBaseline|evaluate|exact|token_acc|token_f1|neural|seq2seq|GRU|Transformer|morph_io|morph_vocab|append_jsonl|experiment_history" tokenizer/notebooks/morph_tokenizer_poc.ipynb tokenizer/morph_poc_utils.py
rg -n "canonical_io|annotated_tokens|annotated_tags|annotated_subtags|annotated_token_variants|morph_io|morph_vocab|morph_dataset_meta|canonical_dsl" README.md tokenizer/notebooks/README.md docs/agent/*.md
nl -ba /Users/kian/.codex/memories/MEMORY.md | sed -n '1478,1486p'
rg -n "class Encoder|class Decoder|class Seq2Seq|src_stoi|src_itos|tgt_stoi|teacher_forcing|char|BOS|EOS|PAD|UNK|EMBED_DIM|HIDDEN_DIM|BATCH_SIZE|EPOCHS|LEARNING_RATE" tokenizer/notebooks/morph_tokenizer_poc.ipynb
rg -n "## [0-9]|# |markdown|source" tokenizer/notebooks/morph_tokenizer_poc.ipynb | head -n 120
rg -n "DROP_FEATURE_PREFIXES|DROP_FEATURES|KEEP_ROOT_FEATURE|USE_EXPLICIT_S_IDS|TRAIN_MODEL|SAVE_CHECKPOINT|EVAL_LIMIT|TEST_STRINGS|MAX_NAVARRO|NAVARRO" tokenizer/notebooks/morph_tokenizer_poc.ipynb
sed -n '1,220p' .gitignore
find docs -maxdepth 2 -type f -print | sort
git status --short
date +%Y-%m-%dT%H-%M-%S%z
```

## What Worked

- The tokenizer passes were documented from the current source files, not just
  from memory or the notebook README.
- The new doc separates deterministic artifact generation from the ML notebook
  layer.
- The doc captures assumptions and failure modes around tag attachment, stable
  registries, orthographic expansion, synthetic-data dominance, feature
  factorization, Navarro lexical priors, baselines, neural seq2seq, and metrics.

## What Failed

- No command failures.
- No tests were run because this was documentation-only.

## Remaining Questions

- Decide whether to link `docs/tokenizer-theory.md` from the main `README.md`
  or `tokenizer/notebooks/README.md` after the user's local edits to those files
  settle.
- Decide which generated tokenizer outputs should be committed after normal
  experiment runs.
- Decide whether tokenizer evaluation should split related orthographic variants
  by source family to reduce optimistic metrics.

## Suggested Next Prompt

Read `docs/tokenizer-theory.md`, then pick one concrete example string and trace
it through `corpus.jsonl`, `canonical_io.jsonl`, the registries, the baseline
trace, and the notebook metrics.

