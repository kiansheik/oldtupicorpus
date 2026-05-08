# Tokenizer notebooks

## `morph_tokenizer_poc.ipynb`

Proof-of-concept notebook for a morphology-aware Old Tupi tokenizer/canonicalizer.

Run from the `oldtupicorpus` repo root:

```bash
jupyter notebook tokenizer/notebooks/morph_tokenizer_poc.ipynb
```

The data-loading and registry baseline cells use only the Python standard library plus the local sibling repo `../nhe-enga` when corpus artifacts need rebuilding.

The neural seq2seq training cell requires PyTorch:

```bash
python3 -m pip install torch numpy notebook ipykernel
```

The notebook will still open and run the non-neural sections if PyTorch is missing.
