# Old Tupi Corpus (Computational Implementation)

## English (for international, academic replication)

This repository contains Kian Arad Sheik's doctoral research in Computational Linguistics and the Description of Non‑Indo‑European Languages at the University of São Paulo (FFLCH). The project implements the Old Tupi corpus in a distributed‑morphology, morpheme‑by‑morpheme representation.

### Why this matters
- Build a searchable, structured corpus of Old Tupi sources.
- Generate facsimiles, syntax trees, and aligned analyses for complex clauses.
- Create synthetic data grounded in real lexical and morphosyntactic patterns.
- Support training of parsers and LLMs for historical or endangered languages.

### Dependencies
This project relies on the `pydicate` and `tupi` Python libraries from `kiansheik/nhe-enga`.
The code expects local checkouts at:
- `../nhe-enga/pydicate`
- `../nhe-enga/tupi`

If your paths differ, adjust the `sys.path` inserts in each primary source module
(for example, `bettendorff_compendio.py`).

### Primary sources and ground truth
- Store reference texts in `ground_truth/historic/<source_name>.txt`.
- Define a list named `<source_name>` in a source module under `historic/`
  (for example, `historic/bettendorff_compendio.py`).
- Import that list in `historic/primary_sources.py` so tests can discover it.
- Synthetic data lives in `synthetic/` and mirrors ground truth in
  `ground_truth/synthetic/` (for example, `synthetic/primary_sources.py`
  paired with `ground_truth/synthetic/verb.txt`).

### How to replicate for another language
1. **Collect sources**: choose a text or manuscript with a stable edition.
2. **Define lexical items**: add lemmas and glosses as `Noun`, `Verb`, etc.
3. **Encode morphology**: represent each clause as compositional predicates.
4. **Add ground truth**: store a clean reference text for alignment.
5. **Test alignment**: compare evaluated expressions to the reference.

### Running tests
```bash
make test
```

Or run directly:
```bash
python3 -m unittest discover -s tests -p "*_test.py"
```

**Test runner options**
- `make test ARGS="--skip-tokenizer"`: run tests only, skip corpus/tokenizer regeneration.
- `make test ARGS="--include-synthetic"`: include synthetic tests.
- `make test ARGS="--timings"`: show discovery/test/tokenizer timings.
- `make test ARGS="--tokenizer-verbose --tokenizer-log-every 1000"`: debug output while regenerating tokenizer artifacts.
- `make test ARGS="--tokenizer-tqdm"`: show a tqdm progress bar during corpus generation.
- `make test ARGS="--tokenizer-include-synthetic"`: include synthetic sources in the corpus build.
- `make test ARGS="--tokenizer-label-from-annotated"`: derive labels from annotated strings when missing (faster).
- `make test ARGS="--tokenizer-orth-expand POTIGUARA TUPINAMBA SEM_DIACRITICO"`: add orthography variants.
- `make test ARGS="--tokenizer-orth-expand-all"`: add variants for all known orthographies (excluding NAVARRO).
- You can also pass standard unittest discovery flags via `--start-directory` and `--pattern`.

**Tokenizer pipeline**
- Build corpus JSONL:
  ```bash
  python3 tokenizer/build_corpus_json.py --out_jsonl tokenizer/output/corpus.jsonl
  ```
- Build token registries + canonical IO:
  ```bash
  python3 tokenizer/rawgrammarpair.py --in_json tokenizer/output/corpus.jsonl --out_dir tokenizer/output
  ```

`tokenizer/build_corpus_json.py` flags:
- `--out_jsonl PATH`: write JSONL (streaming).
- `--out_json PATH`: optional JSON array output.
- `--include-synthetic`: include synthetic sources.
- `--orth-expand ORTH...`: add orthography variants (e.g. `POTIGUARA`, `TUPINAMBA`, `SEM_DIACRITICO`).
- `--orth-expand-all`: expand all known orthographies (excluding NAVARRO).
- `--label-from-annotated`: derive labels from annotated string (faster).
- `--tqdm`: show progress bar.
- `--debug` / `--log-every N`: debug and periodic logging.

`tokenizer/rawgrammarpair.py` flags:
- `--in_json PATH`: JSON or JSONL input.
- `--out_dir PATH`: output directory.
- `--out_jsonl NAME`: output JSONL filename (inside `out_dir`).
- `--exclude_tag_substrings ...`: drop tags containing these substrings.
- `--context_tags ...`: context tags to ignore if unattached.
- `--debug` / `--log-every N`: debug and periodic logging.

Outputs include:
- `tokenizer/output/corpus.jsonl`
- `tokenizer/output/canonical_io.jsonl`
- `tokenizer/output/annotated_tokens.json`
- `tokenizer/output/annotated_tags.json`
- `tokenizer/output/annotated_subtags.json`
- `tokenizer/output/annotated_token_pairs.json`
- `tokenizer/output/annotated_token_variants.json` (variant → canonical map)

---

## Português (para uso prático e comunitário)

Este repositório reúne a pesquisa de doutorado de Kian Arad Sheik na USP (FFLCH). O objetivo é construir um corpus do Tupi Antigo com análise morfológica detalhada, para apoiar estudo, ensino e revitalização.

### Para que serve
- Buscar palavras e trechos no corpus.
- Gerar árvores sintáticas e versões fac-símile.
- Criar novos exemplos com base no léxico real.
- Ajudar na criação de ferramentas para outras línguas indígenas.

### Dependências
Este projeto usa as bibliotecas `pydicate` e `tupi` do repositório `kiansheik/nhe-enga`.
Os caminhos esperados são:
- `../nhe-enga/pydicate`
- `../nhe-enga/tupi`

Se o seu caminho for diferente, ajuste o `sys.path` em cada módulo de fonte
(por exemplo, `bettendorff_compendio.py`).

### Fontes primárias e texto de referência
- Guarde o texto em `ground_truth/historic/<nome_da_fonte>.txt`.
- Defina uma lista chamada `<nome_da_fonte>` no módulo da fonte dentro de
  `historic/` (por exemplo, `historic/bettendorff_compendio.py`).
- Importe essa lista em `historic/primary_sources.py` para os testes encontrarem.
- Dados sintéticos ficam em `synthetic/` e espelham os textos em
  `ground_truth/synthetic/` (por exemplo, `synthetic/primary_sources.py`
  com `ground_truth/synthetic/verb.txt`).

### Como adaptar para outra língua
1. **Escolha uma fonte confiável** (texto, catecismo, manuscrito).
2. **Defina o léxico** com glossas e categorias gramaticais.
3. **Modele a morfologia** de forma composicional.
4. **Crie um texto de referência** para comparar com a saída.
5. **Teste a correspondência** entre a análise e o texto.

### Rodar testes
```bash
make test
```

Ou rode diretamente:
```bash
python3 -m unittest discover -s tests -p "*_test.py"
```

**Opções do runner de testes**
- `make test ARGS="--skip-tokenizer"`: roda apenas os testes, sem regenerar corpus/tokenizer.
- `make test ARGS="--include-synthetic"`: inclui testes sintéticos.
- `make test ARGS="--timings"`: mostra tempos de discovery/test/tokenizer.
- `make test ARGS="--tokenizer-verbose --tokenizer-log-every 1000"`: debug detalhado na regeneração.
- `make test ARGS="--tokenizer-tqdm"`: barra de progresso no corpus.
- `make test ARGS="--tokenizer-include-synthetic"`: inclui fontes sintéticas no corpus.
- `make test ARGS="--tokenizer-label-from-annotated"`: deriva labels do anotado (mais rápido).
- `make test ARGS="--tokenizer-orth-expand POTIGUARA TUPINAMBA SEM_DIACRITICO"`: gera variantes de ortografia.
- `make test ARGS="--tokenizer-orth-expand-all"`: gera variantes para todas as ortografias (exceto NAVARRO).
- Flags padrão do unittest (`--start-directory`, `--pattern`) também funcionam.

**Pipeline do tokenizer**
- Gerar corpus JSONL:
  ```bash
  python3 tokenizer/build_corpus_json.py --out_jsonl tokenizer/output/corpus.jsonl
  ```
- Gerar registries + canonical IO:
  ```bash
  python3 tokenizer/rawgrammarpair.py --in_json tokenizer/output/corpus.jsonl --out_dir tokenizer/output
  ```

`tokenizer/build_corpus_json.py`:
- `--out_jsonl PATH`: escreve JSONL (streaming).
- `--out_json PATH`: JSON array opcional.
- `--include-synthetic`: inclui fontes sintéticas.
- `--orth-expand ORTH...`: variantes de ortografia (ex.: `POTIGUARA`, `TUPINAMBA`, `SEM_DIACRITICO`).
- `--orth-expand-all`: todas as ortografias (exceto NAVARRO).
- `--label-from-annotated`: label a partir do anotado (mais rápido).
- `--tqdm`: barra de progresso.
- `--debug` / `--log-every N`: debug e logs periódicos.

`tokenizer/rawgrammarpair.py`:
- `--in_json PATH`: JSON ou JSONL.
- `--out_dir PATH`: diretório de saída.
- `--out_jsonl NAME`: nome do JSONL (dentro de `out_dir`).
- `--exclude_tag_substrings ...`: remove tags com esses substrings.
- `--context_tags ...`: ignora tags de contexto sem ancoragem.
- `--debug` / `--log-every N`: debug e logs periódicos.

Saídas:
- `tokenizer/output/corpus.jsonl`
- `tokenizer/output/canonical_io.jsonl`
- `tokenizer/output/annotated_tokens.json`
- `tokenizer/output/annotated_tags.json`
- `tokenizer/output/annotated_subtags.json`
- `tokenizer/output/annotated_token_pairs.json`
- `tokenizer/output/annotated_token_variants.json` (mapa variante → canônico)
