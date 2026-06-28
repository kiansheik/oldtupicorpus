# Old Tupi Corpus Agent Rules

This repository is a computational-linguistics research corpus. A passing render is evidence that an implementation is internally consistent. It is not, by itself, evidence that a historical analysis is correct.

## Authority and write boundaries

- The human editor is the authority for diplomatic transcription, normalized target forms, translations, grammatical analyses, and editorial status.
- Never replace an approved ground-truth target with the renderer's output merely to make a comparison pass.
- Never use a ground-truth update command to create a target the human has not inspected.
- Work on one source record at a time. Do not batch-edit unrelated source lines.
- Keep a candidate expression separate from an applied source edit until the human has approved the analysis.

## Required line-authoring loop

1. Call `get_source_context` for the requested source record.
2. Search the lexicon and rendered precedents before inventing a new analysis.
3. Propose a Pydicate expression, explain the morphological assumptions, and state uncertainty or alternatives.
4. Call `render_candidate`; do not edit a source until the human approves the candidate.
5. After an approved edit, run the narrowest relevant regression first, then `make test ARGS="--skip-tokenizer"` and `make verify-ground-truth` when the change can affect historic rendering.
6. Document reusable behavior in `docs/agent/` with a source record id, expression, target, contrast, and test location.

## Ground truth

- `ground_truth/records/<kind>/<source>.jsonl` is the canonical structured target format when present.
- `ground_truth/<kind>/<source>.txt` is a compatibility mirror for legacy consumers.
- Use `make verify-ground-truth` to compare current renderings without writing files.
- Use `make review-ground-truth` only for new trailing lines after a human reviews the proposed target.
- Use `make migrate-ground-truth-records` to create JSONL records from legacy text. Migration creates identifiers but does not invent diplomatic text, translations, or analyses.

## Morphology engine changes

`nhe-enga` is a sibling dependency. Do not modify it as a convenient way to force one source line to match.

Before changing it:

1. Show why an expression-level analysis cannot represent the approved target.
2. Add a minimal focused behavior regression in the appropriate repository.
3. Identify one historic attestation and one contrast that must remain unchanged.
4. Run focused tests before broader corpus checks.

## MCP tools

The local `oldtupi-authoring` MCP server is read-only/evaluation-only. Use it to retrieve context, search precedents, render a candidate, and verify targets. It intentionally cannot apply edits or modify ground truth.

Read `docs/agent/source-authoring.md` before authoring a source record.
