# Approved spacing correction — 2026-10-08

User explicitly authorized correcting Araújo1686:118 ground truth and pushing main,
after pushing the engine separator fix. Generated the corrected surface through
authoring.regenerate.generated_records, applied only ordinal118 through the
records API, and asserted every other field/record was identical before writing.
No expression or editorial metadata changed. The prior two-space surface is now
"abá marã sekoagûerĩ resé nherane'yma".

make test: all113 tests pass; all160 historic renderings agree. Test-generated
tracked tokenizer outputs were restored to their previously clean HEAD bytes.
make verify-ground-truth: existing source-annotation drift at record1 in Araújo
and Catecismo Brasílico persists; Bettendorff passes. This one-line correction
does not resolve or broaden that unrelated metadata migration.

User formatter edits in three historic sources remain uncommitted and unchanged;
they are AST-equivalent to HEAD. Push contains only the approved ground-truth
spacing correction and this note. Next: update server dependencies from main
using the state-preserving server workflow; no server update performed here.
