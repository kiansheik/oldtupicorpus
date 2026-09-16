# Correlational Reflexive Nominal

## Goal

Make 3p nominal reflexive and reciprocal objects use correlational `o-` when
the subject is displaced/pro-dropped and there is no overt subject string:

```python
l += (+asé * aûsub * îe).base_nominal()
```

The target surface is `oîeaûsuba`.

## Files Inspected

- `historic/araujo_catecismo_1686.tu.py`
- `ground_truth/records/historic/araujo_catecismo_1686.jsonl`
- `ground_truth/records/historic/bettendorff_compendio.jsonl`
- `../nhe-enga/AGENTS.md`
- `../nhe-enga/tupi/AGENTS.md`
- `../nhe-enga/tupi/tupi/verb.py`
- `tests/base_nominal_object_pro_drop_test.py`

## Files Changed

- `../nhe-enga/tupi/tupi/verb.py`
- `historic/araujo_catecismo_1686.tu.py`
- `tests/base_nominal_object_pro_drop_test.py`
- `ground_truth/records/historic/araujo_catecismo_1686.jsonl`
- `ground_truth/records/historic/bettendorff_compendio.jsonl`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-06-28T23-14-16-0300-correlational-reflexive-nominal.md`

## Commands Run

- `python3 -c "... (+asé * aûsub * îe).base_nominal() ..."`
- `python3 -m unittest tests.base_nominal_object_pro_drop_test`
- `python3 -m unittest tests.base_nominal_object_pro_drop_test tests.paben_adverb_test tests.nominal_pro_drop_test tests.moro_incorporation_test`
- `make regenerate-ground-truth ARGS="--source araujo_catecismo_1686"`
- `make verify-ground-truth`
- `make regenerate-ground-truth`
- `make test ARGS="--skip-tokenizer"`

## What Worked

- The shared nominal transitive branch in `../nhe-enga/tupi/tupi/verb.py` was
  the right layer for the prefix choice.
- The 3p reflexive object path now renders
  `(+asé * aûsub * îe).base_nominal()` as `oîeaûsuba`.
- The reciprocal contrast renders `(+asé * aûsub * îo).base_nominal()` as
  `oîoaûsuba`.
- Araujo record `araujo_catecismo_1686:0074` was regenerated from source with
  surface `oîeaûsuba`.
- Full historic ground-truth verification passes after regenerating both Araujo
  and Bettendorff structured JSONL.

## What Failed

- Source-specific regeneration for Araujo was not enough for
  `make verify-ground-truth`; Bettendorff records with the same older `i îe...`
  nominal pattern became stale under the shared engine rule. A full
  `make regenerate-ground-truth` fixed the generated JSONL.

## Remaining Questions

- The sibling `../nhe-enga` working tree still has an unrelated
  `docs/.DS_Store` modification. It was not touched.

## Suggested Next Prompt

Continue after Araujo record 74 and add the next source line below the
`# new numbers` marker.
