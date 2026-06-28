# Source authoring workflow

Each executable Pydicate expression is tied to one human-owned source record. The point is to preserve the editorial target, proposed implementation, tests, and reasoning together.

## Record format

Canonical records live in `ground_truth/records/<kind>/<source>.jsonl`. One JSON object represents one executable source line.

Required fields are `id`, `source`, `kind`, `ordinal`, and `surface`.

Optional fields include `diplomatic`, `normalized_target`, `translation`, `analysis`, `status`, and `notes`.

`surface` is the comparison target unless `normalized_target` is present. Legacy `.txt` files remain mirrors for existing consumers during migration.

## Commands

```sh
make verify-ground-truth
make verify-ground-truth ARGS="--source araujo_catecismo_1686"
make migrate-ground-truth-records
make review-ground-truth
```

`verify-ground-truth` never writes. `review-ground-truth` can append only new trailing lines after human confirmation. It never accepts a renderer result as a replacement for an existing approved target.

## Agent-assisted line loop

1. Start from a source record, not from a bare surface string.
2. Retrieve nearby context and comparable existing expressions.
3. Ask for a candidate plus alternatives, not a silent edit.
4. Render the candidate in the relevant source namespace.
5. The human editor approves, rejects, or supplies a corrected target or analysis.
6. Apply the smallest source edit and run targeted checks.
7. When a reusable grammar behavior changed, add a focused regression and an evidence note.

## MCP

The local `oldtupi-authoring` MCP server offers `list_sources`, `get_source_context`, `render_candidate`, `search_rendered_expressions`, `search_lexicon`, and `verify_ground_truth`.

All MCP tools are read-only or evaluation-only. They cannot edit source files, ground-truth records, or Git state.

## Completion condition

A line is complete only when its target is human-approved, its expression has a clear analysis, rendering matches the target, relevant contrasts are tested, and reusable insight is documented with a source record id.
