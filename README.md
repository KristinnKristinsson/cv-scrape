# cv-scrape

A small toolkit for benchmarking a candidate against the real job market instead of
reasoning about fit in the abstract. It collects a real sample of current job
postings for a chosen set of role families, extracts comparable structured data
from each one (seniority signals, required technologies, cloud platforms,
language/education requirements, company type, and more), and evaluates a
candidate's evidence-graded capability profile (`candidate.yaml`, gitignored)
against that data — all persisted to a local SQLite store so it can be queried
and re-analyzed.

## What it does

- **Collects job postings** from a public JobSearch API (Arbetsförmedlingen /
  Platsbanken) and via Scrapy spiders for sites without an API.
- **Probes unfamiliar sites** before writing a spider for them (robots.txt,
  rendering requirements, anti-bot signals, structured data availability).
- **Extracts structured signals** from each posting's free text: role family,
  seniority, technologies, cloud platforms, years of experience required,
  language/education requirements, company type, and salary where stated.
- **Deduplicates** postings that are the same real vacancy cross-posted across
  sources or resubmitted under a different ad ID.
- **Evaluates candidate fit** for each curated posting against `candidate.yaml`,
  producing an `APPLY` / `APPLY_STRETCH` / `LOW_PRIORITY` / `SKIP` recommendation.

## Usage

```
python -m cv_scrape fetch-jobs --region <taxonomy-region-code> --q "data engineer"
python -m cv_scrape extract-signals
python -m cv_scrape evaluate
python -m cv_scrape probe https://example.com/jobs
```

## Development

```
uv sync
uv run pytest
```

Code is organized by *what each piece does* rather than by feature — see
`Behavioral Architecture.md` for the placement rules and `structure.md` for how
they're applied in this repo.
