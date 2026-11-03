# Camarão letters (1645): nominal predication audit

Source: Navarro (2022), "Transcrição e tradução integral anotada das cartas dos índios Camarões". https://doi.org/10.1590/2178-2547-BGOELDI-2021-0034. Open-access CC BY.

**Important:** this is a reproducible pilot analysis and NOT approved philological ground truth. All six letters' justalinear lines are transcribed to all_lines.csv; only manually tagged hypotheses are labeled yes_preliminary. A not_confirmed label means unreviewed/untagged, not proven to be non-copular. Columns beginning with has_ are candidate labels, not grammatical facts.

Counts count **clauses**, not editorial lines (one clause can span several lines); strict deictic_between distinguishes the two clear ã-insertion cases from postposed deictics. Zero strategy means zero overt copular particle, NOT absence of demonstratives. A full paradigm scan in demonstrative_hits.csv now tracks kó, ikó, aîpó, a’e, koba’e, ebokûé, kûeî, akûeî and other forms, with nominal-reference roles distinct from the predicative copula hypothesis. The accompanying summary groups occurrences by lemma, family and letter. Emphatic é / niã and pronouns with competing readings are inventoried separately. eko_predicative includes substantive and state predication, NOT ordinary locative, aspectual or possessive rekó. See summary.json for matched and unmatched annotations.

Rebuild: pip install requests beautifulsoup4 pymupdf; python research/potiguara_1645/build.py.

Future review: inspect all candidate rows, disambiguate ã/niã, é, aé and verb ekó versus demonstrative ikó, then label all clauses and establish verified exhaustive counts.
