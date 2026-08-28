# Source authoring workflow

Each executable Pydicate expression is the editable scholarly source of truth. Ground-truth JSONL is the only generated artifact, rebuilt from the expressions and their directly attached source comments.

## Add a philological locator where the expression is written

Use comment directives immediately above the next list item or `l +=` entry. They add no wrappers, parentheses, or changes to the Pydicate expression.

```python
# @page 25-26
# @section 2
# @subsection 2.1
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

Available locator directives are `@witness`, `@edition`, `@page`, `@folio`, `@line`, `@section`, `@subsection`, `@url`, and `@note`. Singular and plural spellings are accepted. Ranges may use `-`, `–`, or `—`.

### Sequential locator inheritance

The authoring file is read in source order. `@page`, `@section`, and `@subsection` waterfall forward. Line numbers, folios, witnesses, editions, URLs, notes, and editorial fields remain local to their expression.

```python
# @page 25-26
# @section 2
# @subsection 2.1
# @line 25-34
l += first_expression

# @line 35-39
l += second_expression

l += third_expression

# @section 3
l += fourth_expression
```

The second and third expressions receive page `26`, section `2`, and subsection `2.1`. The second alone receives its `35-39` line range. The fourth receives page `26` and section `3`; a new section clears the inherited subsection unless it also declares `@subsection`.

Optional editorial directives are `@diplomatic`, `@target`, `@translation`, `@analysis`, and `@status`. They attach to the same next expression. A directive block must be immediately adjacent to its expression, apart from blank lines.

## Generated record format

`ground_truth/records/<kind>/<source>.jsonl` is regenerated from the source code. Each object has stable `id`, `source`, `kind`, `ordinal`, and `surface` fields, plus optional editorial fields and a repeatable `locations` array. This JSONL is the only generated ground-truth format.

```json
{
  "locations": [
    {
      "page_start": "25",
      "page_end": "26",
      "section": "2",
      "subsection": "2.1",
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

`regenerate-ground-truth` rebuilds JSONL from the current `.tu.py` source. `verify-ground-truth` never writes. It fails when rendering differs or the generated JSONL is stale relative to the source comments.

## Agent-assisted line loop

1. Start from the source expression and adjacent `# @...` directives.
2. Retrieve nearby context and comparable existing expressions.
3. Ask for a candidate plus alternatives, not a silent edit.
4. Render the candidate in the relevant source namespace.
5. The human editor approves, rejects, or corrects the target or analysis.
6. Put the desired expression and any locator directly in the `.tu.py` file.
7. Run `make regenerate-ground-truth` and then `make verify-ground-truth`.
8. When reusable grammar behavior changed, add a focused regression and an evidence note.

## MCP

The local `oldtupi-authoring` MCP server offers `list_sources`, `get_source_context`, `render_candidate`, `search_rendered_expressions`, `search_lexicon`, and `verify_ground_truth`.

All MCP tools are read-only or evaluation-only. They cannot edit source files, generated records, or Git state.

## Completion condition

A line is complete when its source expression and optional citation comments are present, generated JSONL is current, rendering matches the target, relevant contrasts are tested, and its analysis is human-approved.
