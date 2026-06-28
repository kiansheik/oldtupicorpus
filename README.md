# Old Tupi Corpus (Computational Implementation)

## English

This repository contains Kian Arad Sheik's doctoral research in Computational Linguistics and the Description of Non-Indo-European Languages at the University of Sao Paulo (FFLCH). It encodes Old Tupi texts as compositional expressions, checks them against manually curated ground truth, and derives tokenizer- and DSL-oriented corpora from the same source material.

### What this repo currently does
- Encodes historic Old Tupi sources as compositional `pydicate` expressions backed by a shared lexicon.
- Keeps synthetic data generation in the same ecosystem, currently centered on verb generation.
- Compares rendered expressions against ground-truth text files.
- Lets you append new trailing ground-truth lines after the test suite passes,
  with an optional manual review mode for line-by-line confirmation.
- Builds corpus JSONL, canonical token streams, token/tag registries, orthography variants, and DSL output for downstream experiments.
- Provides an interactive REPL playground with `pydicate`, `tupi`, lexicon globals, and sample sources already loaded.

### Dependencies
This repo depends on the local `pydicate` and `tupi` packages from `kiansheik/nhe-enga`.

Expected local paths:
- `../nhe-enga/pydicate`
- `../nhe-enga/tupi`

The shared historic lexicon prepends those paths automatically for local development. If your checkout layout differs, update the path logic in `historic/lexicon.tu.py`.

### Repo map
- `historic/`: historic source modules plus the shared lexicon.
- `synthetic/`: synthetic source generators and helpers.
- `ground_truth/historic/`: reference text for historic sources.
- `ground_truth/synthetic/`: reference text for synthetic sources.
- `tests/`: corpus-alignment tests, ground-truth updater, and shared case loaders.
- `tokenizer/`: corpus builder, registry builder, DSL compiler/runtime, and experimental canonicalization tools.
- `playground.py`: interactive bootstrap for REPL work.
- `primary_sources.py`: compatibility aggregator that merges historic and synthetic sources.

### Source loading model
- Historic sources are auto-discovered from `historic/*.tu.py` and `historic/*.py` by `historic/primary_sources.py`.
- For a historic source, define a list named exactly like the filename stem. Example: `historic/bettendorff_compendio.tu.py` exports `bettendorff_compendio`.
- Synthetic sources are exported explicitly from `synthetic/primary_sources.py`.
- The shared lexicon lives in `historic/lexicon.tu.py`; `historic/lexicon.py` is a compatibility shim.

### Common workflows

**1. Open the REPL playground**
```bash
make play
```

What you get:
- `pydicate`
- `tupi`
- historic lexicon globals
- historic samples such as `bettendorff_compendio`
- synthetic samples such as `verb`
- helpers like `preview(...)`, `render(...)`, and `play_help()`

**2. Run tests**
```bash
make test
```

Useful variants:
- `make test ARGS="--skip-tokenizer"`: run tests only.
- `make test ARGS="--include-synthetic"`: include synthetic tests.
- `make test ARGS="--timings"`: print discovery/test/tokenizer timings.
- `make test ARGS="--tokenizer-verbose --tokenizer-log-every 1000"`: verbose tokenizer rebuild.
- `make test ARGS="--tokenizer-tqdm"`: progress bar during corpus generation.
- `make test ARGS="--tokenizer-include-synthetic"`: include synthetic sources in corpus generation.
- `make test ARGS="--tokenizer-label-from-annotated"`: derive labels from annotated text when missing.
- `make test ARGS="--tokenizer-orth-expand POTIGUARA TUPINAMBA SEM_DIACRITICO"`: add selected orthography variants.
- `make test ARGS="--tokenizer-orth-expand-all"`: expand all known orthographies except `NAVARRO`.

**3. Build and serve the static dictionary**
```bash
make dict
make serve-dict
```

What it does:
- Builds `site/data/rendered_corpus.json(.gz)` with structured historic corpus lines.
- Builds `site/data/dictionary_entries.json(.gz)` with structured lexicon entries and corpus attestations.
- Serves the `site/` bundle locally at `http://localhost:8000` by default.
- Exposes a local SQLite-backed tooltip API so sentence-breakdown notes can be edited in the UI and reused across matching tag scopes.

Useful variants:
- `make serve-dict PORT=4173`
- `make serve-dict TOOLTIP_DB=var/my_tooltips.sqlite3`
- `python3 -m dictionary.build_dict --include-navarro`: optionally include the Navarro-derived supplemental index exported from `../nhe-enga`.

**3. Test and append new ground truth**
```bash
make update-ground-truth
```

Useful variants:
- `make update-ground-truth ARGS="--ground-truth-source bettendorff_compendio"`
- `make update-ground-truth ARGS="--include-synthetic --ground-truth-source verb"`
- `make review-ground-truth`: manually review each candidate line with context.

How it behaves:
- It first runs `make test ARGS="..."`.
- It appends only lines past the current end of each ground-truth file.
- Existing ground-truth lines must still match; any mismatch blocks the append.
- `make test` by itself never writes ground truth.
- `make review-ground-truth` keeps the interactive flow: mismatches can keep
  `[e]xpected`, accept `[a]ctual`, or `[q]uit`; new trailing lines show a
  10-line context window and ask for `y`, `n`, or `q`.
- If a source cannot load or render, it is reported and blocked instead of crashing the whole session.

### Adding or extending sources

**Historic sources**
1. Add a module under `historic/`, usually `<name>.tu.py`.
2. Define a list named `<name>` in that module.
3. Add or extend `ground_truth/historic/<name>.txt`.
4. Run `make test` or `make update-ground-truth`.

**Synthetic sources**
1. Export the source from `synthetic/primary_sources.py`.
2. Add or extend `ground_truth/synthetic/<name>.txt`.
3. Run `make test ARGS="--include-synthetic"` or the updater with `--include-synthetic`.

### Tokenizer and corpus pipeline

**1. Build corpus rows from source expressions**
```bash
python3 tokenizer/build_corpus_json.py --out_jsonl tokenizer/output/corpus.jsonl
```

What it does:
- Reads historic sources, and optionally synthetic ones.
- Extracts annotated and surface strings from expressions.
- Can expand rows into alternative orthographies using `tupi`.
- Produces `tokenizer/output/corpus.jsonl` and optionally a JSON array output.

Important flags for `tokenizer/build_corpus_json.py`:
- `--out_jsonl PATH`
- `--out_json PATH`
- `--include-synthetic`
- `--orth-expand ORTH...`
- `--orth-expand-all`
- `--orth-workers N`
- `--orth-batch-size N`
- `--label-from-annotated`
- `--tqdm`
- `--debug`
- `--log-every N`

**2. Build stable registries and canonical IO**
```bash
python3 tokenizer/rawgrammarpair.py \
  --in_json tokenizer/output/corpus.jsonl \
  --out_dir tokenizer/output
```

What it does:
- Builds stable morpheme IDs (`M######`), tag IDs (`T######`), and subtag IDs (`S######`).
- Emits training-style input/output pairs.
- Exports unique token/tag pairs and variant-to-canonical mappings.

Important flags for `tokenizer/rawgrammarpair.py`:
- `--in_json PATH`
- `--out_dir PATH`
- `--out_jsonl NAME`
- `--exclude_tag_substrings ...`
- `--context_tags ...`
- `--debug`
- `--log-every N`

**3. Compile canonical streams into a DSL**
```bash
python3 tokenizer/compile_to_dsl.py \
  --in_jsonl tokenizer/output/canonical_io.jsonl \
  --out_jsonl tokenizer/output/canonical_dsl.jsonl
```

What it does:
- Reconstructs annotated strings from canonical token streams.
- Builds a morpheme-and-tag AST.
- Emits a best-effort Pydicate-style DSL string plus a literal fallback.
- Writes metadata describing required imports and runtime helpers.
- Can open an interactive DSL explorer REPL unless `--no-repl` is set.

Important flags for `tokenizer/compile_to_dsl.py`:
- `--in_jsonl PATH`
- `--out_jsonl PATH`
- `--tokens PATH`
- `--tags PATH`
- `--meta_out PATH`
- `--limit N`
- `--no-structure`
- `--repl`
- `--no-repl`

**4. Execute generated DSL**
- `tokenizer/dsl_runtime.py` provides `Tok(...)` and `Seq([...])` so compiled DSL output stays executable even when some morphemes fall back to literal tokens.

**5. Experimental canonicalizer**
- `tokenizer/viterbi.py` is a notebook-style baseline that uses the generated tokenizer outputs to score canonical morpheme sequences with a Viterbi approach. It is useful as an experiment or debugging aid, not as the main pipeline entry point.

### Key outputs
- `tokenizer/output/corpus.jsonl`
- `tokenizer/output/canonical_io.jsonl`
- `tokenizer/output/canonical_dsl.jsonl`
- `tokenizer/output/canonical_dsl_meta.json`
- `tokenizer/output/annotated_tokens.json`
- `tokenizer/output/annotated_tags.json`
- `tokenizer/output/annotated_subtags.json`
- `tokenizer/output/annotated_token_pairs.json`
- `tokenizer/output/annotated_token_variants.json`

### Notes for maintainers
- Prefer editing `historic/lexicon.tu.py`; `historic/lexicon.py` exists for compatibility.
- The root-level `primary_sources.py` is a compatibility aggregator, not the canonical place to register historic sources.
- Historic source loading prefers `.tu.py` over `.py` when both exist for the same source name.
- The ground-truth updater is intentionally user-triggered. `make update-ground-truth`
  runs the test suite before appending trailing rendered lines; use
  `make review-ground-truth` for line-by-line confirmation.

---

## Portugues

Este repositório reúne a pesquisa de doutorado de Kian Arad Sheik na USP (FFLCH). Ele codifica textos em Tupi Antigo como expressões composicionais, compara essas expressões com textos de referência e gera saídas para tokenizer, registries e DSL a partir das mesmas fontes.

### O que o repositório faz hoje
- Codifica fontes históricas em `pydicate`, com um léxico histórico compartilhado.
- Gera dados sintéticos no mesmo ecossistema, hoje principalmente verbos.
- Compara a saída renderizada com arquivos de ground truth.
- Permite acrescentar novas linhas finais ao ground truth depois que a suíte passa,
  com um modo manual opcional para confirmar linha por linha.
- Gera corpus JSONL, streams canônicos, registries de morfemas/tags, variantes ortográficas e uma DSL derivada do corpus.
- Oferece um playground em REPL com `pydicate`, `tupi`, léxico e fontes já carregados.

### Dependências
Este projeto depende dos pacotes locais `pydicate` e `tupi` vindos de `kiansheik/nhe-enga`.

Caminhos esperados:
- `../nhe-enga/pydicate`
- `../nhe-enga/tupi`

O léxico histórico compartilhado já faz o prepend desses caminhos para desenvolvimento local. Se sua estrutura de pastas for diferente, ajuste a lógica em `historic/lexicon.tu.py`.

### Mapa do repositório
- `historic/`: fontes históricas e o léxico compartilhado.
- `synthetic/`: geradores e helpers para fontes sintéticas.
- `ground_truth/historic/`: textos de referência das fontes históricas.
- `ground_truth/synthetic/`: textos de referência das fontes sintéticas.
- `tests/`: testes de alinhamento, atualizador de ground truth e loaders compartilhados.
- `tokenizer/`: builder do corpus, builder dos registries, compilador/runtime da DSL e ferramentas experimentais.
- `playground.py`: bootstrap interativo para REPL.
- `primary_sources.py`: agregador de compatibilidade para fontes históricas e sintéticas.

### Como as fontes são carregadas
- Fontes históricas são descobertas automaticamente a partir de `historic/*.tu.py` e `historic/*.py` por `historic/primary_sources.py`.
- Para uma fonte histórica, defina uma lista com o mesmo nome do arquivo. Exemplo: `historic/bettendorff_compendio.tu.py` exporta `bettendorff_compendio`.
- Fontes sintéticas são exportadas explicitamente por `synthetic/primary_sources.py`.
- O léxico compartilhado vive em `historic/lexicon.tu.py`; `historic/lexicon.py` é apenas um shim de compatibilidade.

### Fluxos mais comuns

**1. Abrir o playground no REPL**
```bash
make play
```

O que já vem carregado:
- `pydicate`
- `tupi`
- globais do léxico histórico
- fontes históricas como `bettendorff_compendio`
- fontes sintéticas como `verb`
- helpers como `preview(...)`, `render(...)` e `play_help()`

**2. Rodar testes**
```bash
make test
```

Variações úteis:
- `make test ARGS="--skip-tokenizer"`: roda só os testes.
- `make test ARGS="--include-synthetic"`: inclui testes sintéticos.
- `make test ARGS="--timings"`: mostra tempos de discovery/test/tokenizer.
- `make test ARGS="--tokenizer-verbose --tokenizer-log-every 1000"`: rebuild verboso do tokenizer.
- `make test ARGS="--tokenizer-tqdm"`: barra de progresso na geração do corpus.
- `make test ARGS="--tokenizer-include-synthetic"`: inclui fontes sintéticas no corpus.
- `make test ARGS="--tokenizer-label-from-annotated"`: deriva labels do texto anotado quando faltarem.
- `make test ARGS="--tokenizer-orth-expand POTIGUARA TUPINAMBA SEM_DIACRITICO"`: adiciona variantes ortográficas selecionadas.
- `make test ARGS="--tokenizer-orth-expand-all"`: expande todas as ortografias conhecidas, exceto `NAVARRO`.

**3. Testar e acrescentar novo ground truth**
```bash
make update-ground-truth
```

Variações úteis:
- `make update-ground-truth ARGS="--ground-truth-source bettendorff_compendio"`
- `make update-ground-truth ARGS="--include-synthetic --ground-truth-source verb"`
- `make review-ground-truth`: revisa manualmente cada linha candidata com contexto.

Comportamento:
- Primeiro roda `make test ARGS="..."`.
- Só acrescenta linhas depois do fim atual de cada arquivo de ground truth.
- As linhas antigas precisam continuar batendo; qualquer divergência bloqueia o append.
- `make test` sozinho nunca grava ground truth.
- `make review-ground-truth` mantém o fluxo interativo: divergências podem
  manter `[e]xpected`, aceitar `[a]ctual` ou sair com `[q]uit`; novas linhas
  finais mostram uma janela de 10 linhas de contexto e perguntam `y`, `n` ou
  `q`.
- Se uma fonte não carregar ou não renderizar, ela é reportada e bloqueada sem derrubar a sessão inteira.

### Como adicionar ou ampliar fontes

**Fontes históricas**
1. Adicione um módulo em `historic/`, normalmente `<nome>.tu.py`.
2. Defina uma lista chamada `<nome>` nesse módulo.
3. Crie ou amplie `ground_truth/historic/<nome>.txt`.
4. Rode `make test` ou `make update-ground-truth`.

**Fontes sintéticas**
1. Exporte a fonte em `synthetic/primary_sources.py`.
2. Crie ou amplie `ground_truth/synthetic/<nome>.txt`.
3. Rode `make test ARGS="--include-synthetic"` ou o atualizador com `--include-synthetic`.

### Pipeline de tokenizer e corpus

**1. Gerar linhas de corpus a partir das expressões**
```bash
python3 tokenizer/build_corpus_json.py --out_jsonl tokenizer/output/corpus.jsonl
```

O que faz:
- Lê fontes históricas e, opcionalmente, sintéticas.
- Extrai strings anotadas e de superfície a partir das expressões.
- Pode expandir as linhas para ortografias alternativas usando `tupi`.
- Produz `tokenizer/output/corpus.jsonl` e, opcionalmente, um JSON em array.

Flags importantes de `tokenizer/build_corpus_json.py`:
- `--out_jsonl PATH`
- `--out_json PATH`
- `--include-synthetic`
- `--orth-expand ORTH...`
- `--orth-expand-all`
- `--orth-workers N`
- `--orth-batch-size N`
- `--label-from-annotated`
- `--tqdm`
- `--debug`
- `--log-every N`

**2. Gerar registries estáveis e canonical IO**
```bash
python3 tokenizer/rawgrammarpair.py \
  --in_json tokenizer/output/corpus.jsonl \
  --out_dir tokenizer/output
```

O que faz:
- Gera IDs estáveis para morfemas (`M######`), tags (`T######`) e subtags (`S######`).
- Emite pares de entrada/saída para treino.
- Exporta pares únicos token/tag e o mapeamento variante -> canônico.

Flags importantes de `tokenizer/rawgrammarpair.py`:
- `--in_json PATH`
- `--out_dir PATH`
- `--out_jsonl NAME`
- `--exclude_tag_substrings ...`
- `--context_tags ...`
- `--debug`
- `--log-every N`

**3. Compilar streams canônicos para uma DSL**
```bash
python3 tokenizer/compile_to_dsl.py \
  --in_jsonl tokenizer/output/canonical_io.jsonl \
  --out_jsonl tokenizer/output/canonical_dsl.jsonl
```

O que faz:
- Reconstrói strings anotadas a partir dos streams canônicos.
- Monta uma AST de morfemas e tags.
- Emite uma DSL no estilo Pydicate, mais um fallback literal.
- Escreve metadados com imports e runtime necessários.
- Pode abrir um REPL de exploração da DSL, a menos que `--no-repl` seja usado.

Flags importantes de `tokenizer/compile_to_dsl.py`:
- `--in_jsonl PATH`
- `--out_jsonl PATH`
- `--tokens PATH`
- `--tags PATH`
- `--meta_out PATH`
- `--limit N`
- `--no-structure`
- `--repl`
- `--no-repl`

**4. Executar a DSL gerada**
- `tokenizer/dsl_runtime.py` fornece `Tok(...)` e `Seq([...])`, para que a DSL compilada continue executável mesmo quando algum morfema cai para um token literal.

**5. Canonicalizador experimental**
- `tokenizer/viterbi.py` é um baseline em estilo notebook que usa as saídas do tokenizer para pontuar sequências canônicas de morfemas com Viterbi. Serve como experimento e ferramenta de inspeção, não como pipeline principal.

### Saídas principais
- `tokenizer/output/corpus.jsonl`
- `tokenizer/output/canonical_io.jsonl`
- `tokenizer/output/canonical_dsl.jsonl`
- `tokenizer/output/canonical_dsl_meta.json`
- `tokenizer/output/annotated_tokens.json`
- `tokenizer/output/annotated_tags.json`
- `tokenizer/output/annotated_subtags.json`
- `tokenizer/output/annotated_token_pairs.json`
- `tokenizer/output/annotated_token_variants.json`

### Notas para manutenção
- Prefira editar `historic/lexicon.tu.py`; `historic/lexicon.py` existe por compatibilidade.
- `primary_sources.py` na raiz é um agregador de compatibilidade, não o lugar canônico para registrar fontes históricas.
- No carregamento histórico, `.tu.py` tem prioridade sobre `.py` quando os dois existem para o mesmo nome.
- O atualizador de ground truth foi desenhado para continuar interativo e explicitamente disparado pelo usuário.
