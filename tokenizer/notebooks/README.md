# Tokenizer notebooks

## `morph_tokenizer_poc.ipynb`

Proof-of-concept notebook for a morphology-aware Old Tupi tokenizer/canonicalizer trained from the local pydicate + oldtupicorpus data.

Run from the `oldtupicorpus` repo root:

```bash
jupyter notebook tokenizer/notebooks/morph_tokenizer_poc.ipynb
```

The non-neural build, factorization, baseline, and evaluation utilities use the Python standard library plus the local sibling repo `../nhe-enga`. The neural seq2seq section requires PyTorch:

```bash
python3 -m pip install torch numpy notebook ipykernel
```

## Rebuilding the data

Near the top of the notebook, set:

```python
FORCE_REBUILD = True
INCLUDE_SYNTHETIC = True
LABEL_FROM_ANNOTATED = True
ORTH_EXPAND = ["POTIGUARA", "TUPINAMBA", "SEM_DIACRITICO"]
ORTH_EXPAND_ALL = False
ORTH_WORKERS = 1
BUILD_LOG_EVERY = 10000
USE_NAVARRO_LEXICON = True
ADD_LEXEME_TOKENS = True
GENERATE_NAVARRO_LEXICON_ROWS = True
GENERATE_NAVARRO_POSTPOSITION_COMBOS = True
```

Use `FORCE_REBUILD = True` after adding new pydicate-encoded material under `historic/` or `synthetic/`. The notebook prints the exact `build_corpus_json.py` and `rawgrammarpair.py` commands it runs.

Use `INCLUDE_SYNTHETIC = True` to include synthetic sources. The current synthetic verb generator can be very large, so first full rebuilds may take real time, especially with orthographic expansion enabled. Use `ORTH_WORKERS` and `BUILD_LOG_EVERY` to make long rebuilds easier to monitor.

Use `ORTH_EXPAND` for selected orthographic variants, or `ORTH_EXPAND_ALL = True` to request every known orthography exposed by `../nhe-enga/tupi`.

## Navarro lexical prior

The notebook can preload Navarro dictionary entries through `pydicate.dbexplorer.NavarroDB`.

Default classes:

```python
NAVARRO_CLASSES = ["noun", "verb", "postposition", "adverb", "pronoun"]
```

Navarro entries add `<LEX:NAVARRO:...>` tokens to the vocabulary and the lexicon-aware baseline. They do not replace corpus-generated `<M:...>` tokens. The intended representation is layered:

- `<M:...>`: observed surface or morpheme realization from generated/annotated corpus data.
- `<LEX:NAVARRO:...>`: underlying dictionary lexeme.
- `<G:...>`: grammatical feature.

The lexicon-aware baseline uses dynamic programming over observed M surfaces, orthographic variants, Navarro lexemes, and RAW fallbacks. This is why examples such as `ka'ape` can prefer `ka'a + pe` over locally valid but linguistically worse chunks.

Optional augmentation is controlled by:

```python
GENERATE_NAVARRO_LEXICON_ROWS = True
GENERATE_NAVARRO_POSTPOSITION_COMBOS = True
MAX_NAVARRO_AUGMENT_ROWS = 10000
```

Generated lexicon rows are marked with `corpus = "lexicon"` and `lexicon_generated = True`.

## Files written

The notebook preserves the existing tokenizer outputs and adds derived research artifacts:

- `tokenizer/output/morph_io.jsonl`: surface input to factorized `<M:...>` / `<G:...>` target rows with source metadata.
- `tokenizer/output/morph_vocab.json`: special tokens, target vocabulary, M tokens, LEX tokens, and G tokens.
- `tokenizer/output/morph_dataset_meta.json`: timestamp, config, row counts, feature-drop settings, and corpus/source/orthography counts.
- `tokenizer/output/morph_tokenizer_poc.pt`: optional PyTorch checkpoint when `SAVE_CHECKPOINT = True`.
- `tokenizer/output/morph_experiment_history.jsonl`: one appended metrics/config row per evaluation run.

Large/generated experiment files are ignored by `.gitignore` so local notebook runs do not accidentally add training data or checkpoints.

## Metrics

The evaluation table reports:

- `exact`: full target sequence match.
- `token_acc`: aligned position-wise token accuracy.
- `token_f1`: multiset F1 over all target tokens.
- `m_f1`: multiset F1 over `<M:...>` morpheme tokens; precision/recall are also stored in history.
- `g_f1`: multiset F1 over `<G:...>` grammar feature tokens; precision/recall are also stored in history.
- `raw_rate`: share of baseline-like morpheme chunks emitted as `<RAW:...>`.

The table compares `baseline`, `lexicon_baseline`, and `neural` when each is available.

## Caveat

The neural model is still a small local toy until the corpus has enough rows and variation. The repeatable part is the point: as you add Old Tupi pydicate data, force rebuild, rerun training/evaluation, and compare `morph_experiment_history.jsonl`.
