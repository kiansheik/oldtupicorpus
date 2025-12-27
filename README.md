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

If your paths differ, adjust the `sys.path` inserts in `compendio_bettendorf.py`.

### How to replicate for another language
1. **Collect sources**: choose a text or manuscript with a stable edition.
2. **Define lexical items**: add lemmas and glosses as `Noun`, `Verb`, etc.
3. **Encode morphology**: represent each clause as compositional predicates.
4. **Add ground truth**: store a clean reference text for alignment.
5. **Test alignment**: compare evaluated expressions to the reference.

### Running tests
```bash
python3 tests/compendio_bettendorf_test.py
```

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

Se o seu caminho for diferente, ajuste o `sys.path` em `compendio_bettendorf.py`.

### Como adaptar para outra língua
1. **Escolha uma fonte confiável** (texto, catecismo, manuscrito).
2. **Defina o léxico** com glossas e categorias gramaticais.
3. **Modele a morfologia** de forma composicional.
4. **Crie um texto de referência** para comparar com a saída.
5. **Teste a correspondência** entre a análise e o texto.

### Rodar testes
```bash
python3 tests/compendio_bettendorf_test.py
```
