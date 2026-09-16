# Historic Source Authoring

Each executable item in a source list corresponds positionally to one approved ground-truth record. Do not reorder existing items casually.

## Before editing a line

- Identify the record id and inspect its neighbors with `get_source_context`.
- Preserve the source's established local style, imports, aliases, and grouping.
- Prefer reusing an existing lexical variable or idiom found through `search_lexicon` or `search_rendered_expressions`.
- Keep new lexical definitions local only while they are genuinely source-specific. Move reusable definitions into `historic/lexicon.tu.py` deliberately.

## Candidate requirements

A proposed expression must come with:

- the intended modern-orthography target;
- the relevant source/context evidence supplied by the human editor;
- a short morpheme-by-morpheme or construction-level explanation;
- a rendered output from `render_candidate`;
- at least one comparable precedent or an explicit statement that no precedent was found.

## Do not infer authority from a match

A target match does not settle whether a construction is linguistically correct. If the analysis is underdetermined, record the alternatives in the structured record or an agent note and leave status as `human_review` or `unresolved`.

## Source edits

After a human approves an expression, make the smallest edit possible. Do not change target records in the same edit merely to hide a disagreement. Use a focused test whenever the source introduces or relies on a reusable grammatical behavior.
