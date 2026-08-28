# Base Nominal Object Pro Drop

## Goal

Support the corrected Araujo record 73 analysis where the fronted
`opkmbt = opakatu + (mbae + tetiruã)` phrase is also the dropped object of
`asé * aûsub`:

```python
opkmbt + (((asé * aûsub * +opkmbt).base_nominal()) * sosé) + (
    asé * (tupan * aûsub.base_nominal())
)
```

The target surface remains:
`opakatu mba'e tetiruã asé saûsuba sosé asé Tupã raûsuba`.

## Files Inspected

- `historic/araujo_catecismo_1686.tu.py`
- `ground_truth/records/historic/araujo_catecismo_1686.jsonl`
- `../nhe-enga/AGENTS.md`
- `../nhe-enga/tupi/AGENTS.md`
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`

## Files Changed

- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`
- `historic/araujo_catecismo_1686.tu.py`
- `tests/base_nominal_object_pro_drop_test.py`
- `ground_truth/records/historic/araujo_catecismo_1686.jsonl`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-06-28T18-01-43-0300-base-nominal-object-pro-drop.md`

## Commands Run

- `python3 -c "... render_candidate('araujo_catecismo_1686', ...)"`
- `python3 -m unittest tests.base_nominal_object_pro_drop_test`
- `make regenerate-ground-truth ARGS="--source araujo_catecismo_1686"`
- `python3 -m unittest tests.base_nominal_object_pro_drop_test tests.paben_adverb_test tests.nominal_pro_drop_test`
- `make verify-ground-truth`
- `make test ARGS="--skip-tokenizer"`

## What Worked

- Regular verb rendering already respected `+opkmbt`: `asé * aûsub * +opkmbt`
  rendered without surfacing the object.
- `Verb.base_nominal()` in sibling `nhe-enga` now also checks object
  `pro_drop`; dropped non-pronoun objects no longer pass their rendered string
  as `dir_obj_raw`.
- `(asé * aûsub * +opkmbt).base_nominal()` now renders `asé saûsuba`.
- The dropped `opkmbt` object remains in `nominal.arguments`, so syntax/tree
  consumers can still see that it is the same object as the fronted phrase.
- Araujo record `araujo_catecismo_1686:0073` still renders the approved target
  after regeneration.

## What Failed

- Before the shared fix,
  `(asé * aûsub * +opkmbt).base_nominal()` rendered
  `asé opakatu mba'e tetiruãraûsuba`, repeating the dropped object inside the
  nominalized verb.

## Remaining Questions

- None for this behavior. The sibling `nhe-enga` working tree includes earlier
  nominal pro-drop changes in the same file; avoid treating the full sibling
  file diff as only this turn's change without checking its local history.

## Suggested Next Prompt

Continue from the `# new numbers` marker in `historic/araujo_catecismo_1686.tu.py`
and add the next source line after record 73.
