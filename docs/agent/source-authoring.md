# Source authoring workflow

Each executable Pydicate expression is the editable scholarly source of truth. Ground-truth JSONL and legacy text are generated artifacts, rebuilt from the expressions and their directly attached source comments.

## Add a philological locator where the expression is written

Use comment directives immediately above the next list item or `l +=` entry. They add no wrappers, parentheses, or changes to the Pydicate expression.

```python
# @page 25-26
# @line 25-34
l += (...)
```

For manuscripts, use a folio instead of a page:

```python
# @witness BNE MSS/1234
# @folio 10r
# @line 4-7
l += (...)
```

Available locator directives are `@witness`, `@edition`, `@page`, `@folio`, `@line`, `@section`, `@url`, and `@note`. Singular and plural spellings are both accepted, so `@page` and `@pages` behave the same way. Ranges may use `-`, `–`, or `—`.

Optional editorial directives are `@diplomatic`, `@target`, `@translation`, `@analysis`, and `@status`. They attach to the same next expression. A directive block must be immediately adjacent to its expression, apart from blank lines.

## Generated record format

`ground_truth/records/<kind>/<source>.jsonl` is regenerated from the source code. Each object has stable `id`, `source`, `kind`, `ordinal`, and `surface` fields, plus optional editorial fields and a repeatable `locations` array. Legacy `.txt` files remain generated mirrors for current consumers.

Example generated location:

```json
{
  "locations": [
    {
      "page_start": "25",
      "page_end": "26",
      "line_start": "25",
      "line_end": "34"
    }
  ]
}
```

## Commands

```sh
make regenerate-ground-truth
make regenerate-ground-truth ARGS="--source araujo_catecismo_1686"
make verify-ground-truth
```

`regenerate-ground-truth` deliberately rebuilds JSONL and text from the current `.tu.py` source. `verify-ground-truth` never writes. It fails when either rendering differs or the generated artifacts are stale relative to the source comments.

## Agent-assisted line loop

1. Start from the source expression and its adjacent `# @...` directives.
2. Retrieve nearby context and comparable existing expressions.
3. Ask for a candidate plus alternatives, not a silent edit.
4. Render the candidate in the relevant source namespace.
5. The human editor approves, rejects, or supplies a corrected target or analysis.
6. Put the desired expression and any page, folio, or line locator directly in the `.tu.py` file.
7. Run `make regenerate-ground-truth` and then `make verify-ground-truth`.
8. When reusable grammar behavior changed, add a focused regression and an evidence note.

## MCP

The local `oldtupi-authoring` MCP server offers `list_sources`, `get_source_context`, `render_candidate`, `search_rendered_expressions`, `search_lexicon`, and `verify_ground_truth`.

All MCP tools are read-only or evaluation-only. They cannot edit source files, generated records, or Git state.

## Completion condition

A line is complete when its source expression and optional citation comments are present, generated records are current, rendering matches the target, relevant contrasts are tested, and its analysis is human-approved.