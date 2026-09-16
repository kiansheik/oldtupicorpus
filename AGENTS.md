# Old Tupi Corpus Agent Rules

This repository is a computational-linguistics research corpus. A passing render is evidence that an implementation is internally consistent. It is not, by itself, evidence that a historical analysis is correct.

## Authority and write boundaries

- The human editor is the authority for diplomatic transcription, normalized target forms, translations, grammatical analyses, editorial status, and philological citations.
- Never replace a historical target with the renderer's output merely to make a comparison pass.
- Work on one source expression at a time. Do not batch-edit unrelated source lines.
- Keep a candidate expression separate from an applied source edit until the human has approved the analysis.
- Put scholarly metadata directly above its expression as `# @...` source comments. Do not hand-edit generated JSONL as a parallel editorial source.

## Required line-authoring loop

1. Call `get_source_context` for the requested source record.
2. Search the lexicon and rendered precedents before inventing a new analysis.
3. Propose a Pydicate expression, explain the morphological assumptions, and state uncertainty or alternatives.
4. Call `render_candidate`; do not edit a source until the human approves the candidate.
5. After an approved edit, place any source locator directly above the entry, for example `# @page 25-26` and `# @line 25-34`.
6. Run `make regenerate-ground-truth`, then the narrowest relevant regression, then `make test ARGS="--skip-tokenizer"` and `make verify-ground-truth` when the change can affect historic rendering.
7. Document reusable behavior in `docs/agent/` with a source record id, expression, target, contrast, and test location.

## Ground truth

- Historic `.tu.py` source expressions and their adjacent `# @...` comments are authoritative.
- `ground_truth/records/<kind>/<source>.jsonl` is the sole generated ground-truth artifact. Do not hand-edit it.
- Use `make regenerate-ground-truth` after changing a source expression or attached directives.
- Use `make verify-ground-truth` to check both renderings and whether generated JSONL is current.
- `@witness`, `@edition`, `@page`, `@folio`, `@line`, `@section`, `@subsection`, `@url`, and `@note` add a location to the next list item or `l +=` entry. `@page`, `@section`, and `@subsection` inherit forward. `@diplomatic`, `@target`, `@translation`, `@analysis`, and `@status` add editorial metadata.

## Morphology engine changes

`nhe-enga` is a sibling dependency. Do not modify it as a convenient way to force one source line to match.

Before changing it:

1. Show why an expression-level analysis cannot represent the approved target.
2. Add a minimal focused behavior regression in the appropriate repository.
3. Identify one historic attestation and one contrast that must remain unchanged.
4. Run focused tests before broader corpus checks.

## MCP tools

The local `oldtupi-authoring` MCP server is read-only/evaluation-only. Use it to retrieve context, search precedents, render a candidate, and verify targets. It intentionally cannot apply edits or modify source files, generated ground truth, or Git state.

Read `docs/agent/source-authoring.md` before authoring a source record.
