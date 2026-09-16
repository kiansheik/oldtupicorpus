# Structured ground truth records

Each `*.jsonl` file contains one JSON object per executable source expression. The file is canonical whenever it exists; the matching legacy `ground_truth/<kind>/<source>.txt` file remains a compatibility mirror.

Required fields:

- `id`, for example `araujo_catecismo_1686:0104`
- `source`
- `kind`, for example `historic`
- `ordinal`, contiguous from 1
- `surface`, the approved comparison target

Optional editorial fields include `diplomatic`, `normalized_target`, `translation`, `analysis`, `status`, and `notes`.

Create records from existing text with:

```sh
make migrate-ground-truth-records
```

Do not use migration output as newly researched metadata. It preserves the existing target text and creates stable identities only.
