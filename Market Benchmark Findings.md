# Stockholm Market Benchmark — Findings (2026-08-20)

This is the market-side output of steps 1–4 of the benchmark methodology in
`Objectives.md`. It exists to be handed to another agent — one that has the user's
actual CV/evidence — to do what this codebase's scraping/extraction pipeline can't:
place a specific person's background against a real market and produce steps 5–7.

**What this document is not:** it contains no evidence about the user. Every number
below comes from scraped job postings, not from the user's CV, skills, or history.
Anyone using this to do step 5 needs the user's evidence supplied separately — see
"What the next step needs" at the bottom.

## Method summary (steps 1–4, full detail in `Objectives.md`)

1. **Role families searched** (7, Stockholm, EN+SV titles): Junior Data Engineer,
   Data Engineer (unqualified), Analytics Engineer, ETL/Integration Developer,
   Python/Data Developer, data-heavy Backend Developer, selected Data Platform
   roles. Senior/Lead/Principal titles excluded from primary collection by design
   (they'd swamp the lower tiers) — a small deliberate set was still captured
   incidentally and forms tier 5 below.
2. **Collected** via the two scraping paths this repo already has: the
   Arbetsförmedlingen/Platsbanken JobSearch API and a jobbsafari.se spider scoped to
   Stockholm "utvecklare" listings. 1,320 raw postings collected 2026-08-20.
3. **Curated** to 71 postings that actually match one of the 7 families by
   title/description keyword rules, after removing 4 duplicates (same vacancy
   cross-posted across sources, or resubmitted twice on Platsbanken under different
   ad IDs).
4. **Tiered** into 5 demand bands using a composite "experience score" (explicit
   years-required when stated, marker-based estimate otherwise) with tech-stack
   breadth as a tie-breaker. Full derivation and caveats in `Objectives.md`'s "Step 4
   market distribution" section — the short version is repeated below.

## The 71-posting sample, by role family

| Family | n |
|---|---|
| Data Engineer (incl. Junior) | 49 |
| ETL / Integration | 7 |
| Analytics Engineer | 6 |
| Data-heavy Backend Developer | 5 |
| Data Platform | 4 |

Data Engineer dominates the sample — not a collection artifact, the largest family
by a wide margin in the real market for these seven families.

## Market tier distribution

| Tier | n | Rule | Profile |
|---|---|---|---|
| 1. Market floor | 7 | No years stated, no senior language anywhere | All direct employers, no language/education requirement stated, avg. 6.6 distinct technologies mentioned |
| 2. Typical junior | 8 | Explicit 3-year requirement — the lowest *quantified* bar in the whole sample | All Data Engineer-titled; half staffing/consultancy, half direct |
| 3. Competitive junior | 21 | Reads as wanting real experience but states no number, narrow tool scope (≤5 technologies) | avg. 3.4 technologies — narrower-scope roles |
| 4. Strong junior / early mid-level | 25 | Same as tier 3 but broad tool scope (≥6 technologies), or an explicit 5-year requirement | Largest tier — avg. 7.3 technologies, 4 of 25 state a preferred degree |
| 5. Stretch | 10 | Title says Senior/Lead/Erfaren, or an explicit 8-year requirement | Almost all direct employers; the only tier where Swedish-required share rises (3 of 10) |

**Headline finding:** only 15 of 71 postings (21%) sit at or below a quantified
3-year bar. There is effectively no 0–1-year tier in this market for these seven
families — 1 posting in the entire sample read as straightforwardly junior-friendly.
Two-thirds of the market (tiers 3–4, 46 of 71) is "wants real experience, breadth of
tools" territory, not entry-level. That's where any placement should focus, not the
thin true floor.

## Technologies and cloud platforms demanded, across all 71

Most-mentioned technologies: SQL (50), Python (39), Git (38), dbt (35), Snowflake
(27), Scala (27), Databricks (21), Airflow (19), Spark (16), BigQuery (12).

Cloud platforms: Azure (37) > AWS (28) > GCP (19). GCP is the least-requested of the
three major clouds in this sample — worth noting explicitly since it's a platform
commonly held as evidence.

Per-family technology emphasis differs:

| Family | Top technologies |
|---|---|
| Data Engineer | SQL, Python, Git, dbt, Scala |
| Analytics Engineer | dbt, Snowflake, SQL, Git, BigQuery |
| Data Platform | Scala, Python, Databricks, BigQuery, SQL |
| ETL/Integration | Git, Scala, Linux, Java, Kafka |
| Data-heavy Backend | SQL, Snowflake, Git, Java, Kafka |

## Other cross-cutting findings

- **Language:** 58 of 71 state no explicit language requirement; 13 explicitly
  require Swedish (concentrated more in tier 5).
- **Education:** 64 of 71 state no explicit degree requirement; 7 state a preferred
  (not required) degree — no posting in the sample states a hard degree requirement.
- **Company type:** 53 of 71 are direct employers, 18 are consultancy/staffing
  postings.
- **Salary:** stated explicitly in only 3 of 71 postings — too sparse to draw a
  conclusion from, and the extracted values themselves are unreliable (the
  extraction regex captured truncated fragments like "000 SEK" rather than the full
  figure in at least these 3 cases — a known extraction-quality issue, not fixed as
  part of this pass).

## Known limitations of this data (read before placing evidence against it)

- **The "experience score" powering the tiers is partly a modeling default, not
  observed data.** 36 of 71 postings had no explicit years-required figure and no
  title-level seniority marker; those were defaulted to a flat mid-level score and
  then split into tiers 3/4 by tech-stack breadth alone. Treat tier 3 vs. 4
  boundaries as approximate, not a precise cutoff.
- **`role_family` and `technologies` are first-pass keyword classifiers**, tuned
  once against this sample (see `Objectives.md`'s Step 3 note on a false-positive
  bug found and fixed in the backend/Python family boundary). They under-count
  postings using less common phrasing — e.g. a specific AWS service name instead of
  "AWS" — so technology counts above are a floor, not a ceiling.
- **Seniority/education/language detection is keyword-based**, not a language
  model — it can miss requirements phrased unusually and will occasionally pick up
  boilerplate (e.g. company "about us" text) rather than role-specific requirements.

## What the next step needs

Step 5 ("place the user's current evidence against it") needs the user's actual
evidence, not the category list from `Objectives.md`'s Mission section — specifics,
not labels: years and depth of Python/SQL, what "scraping/data ingestion" evidence
concretely is (this repo counts), GCP/Docker/Linux specifics, database experience,
what "AI systems thinking" means concretely, education (degree, field, completion
status), professional experience (titles, durations), and GitHub evidence (which
repos, what they demonstrate). Once that's supplied, placement against the 5 tiers
above should answer, per tier: does the user's evidence clear it, partially clear
it, or fall short — then step 6 (classify each shortfall as a real capability gap,
an evidence gap, or a presentation gap) and step 7 (2–3 positioning lanes) follow
from that placement.
