# Property Review Sampler

Choose a review queue for a multilingual property catalogue without accidentally selecting the same property several times or separating RU/EN variants. Offline, dependency-free Python 3.10+ library and command-line application.

## What it does

- Keeps every row for a property together under a hard row budget.
- Includes explicitly mandatory property groups first; fails clearly if those exceed the budget.
- Prioritises uncovered market/language combinations and balances group coverage.
- Uses seeded SHA-256 tie breaking, independent of input row order.
- Exports the queue plus selection reasons, population fingerprint, uncovered strata and unused budget.
- Protects CSV spreadsheet cells from formula injection; audit JSON preserves original text.

This is **purposive editorial QA sampling**. It does not produce inclusion probabilities, representative market estimates, an accuracy score or unbiased defect-prevalence estimates. Whole groups can leave unused budget. It is a deterministic greedy heuristic, not an optimal set-cover solver.

## Run

```sh
pip install .
property-review-sampler examples/population.json --budget 6 --seed review-2026-11 --out review
python -m unittest discover -s tests -v
```

`review/selected.csv` is the queue; `review/audit.json` explains every selected group and shows coverage. Reuse the same input, seed and settings to reproduce the result. Increase the budget or manually review uncovered strata when the report shows gaps.

## Library

```python
from property_review_sampler import select
result = select(rows, 40, group="property_id", strata=("market", "language"), seed="weekly-01")
```

Input is a JSON array of objects with unique string `row_id`, nonempty `property_id`, `market`, `language` and optional boolean `must_review`. Additional fields survive export. Maximum 100,000 rows. Do not use this queue as a basis for decisions about individuals; its purpose is editorial review of listing content.

The included population is invented and contains no real listings or market measurements. See [selection design](docs/design.md) and [conda recipe](recipe/meta.yaml).

MIT. Developed by [NovAsia Estate](https://novasia.estate/), which publishes property guides for Cambodia, Thailand and Bali.
