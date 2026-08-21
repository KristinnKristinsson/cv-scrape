# Objectives — Business Logic

This is the counterpart to `Behavioral Architecture.md` and `structure.md`. Those
govern *where code goes*; this governs *what the project is for and what it must
ultimately produce*. Consult this before deciding what a new feature should compute,
extract, or report — `structure.md` still decides where that computation lives once
you know what it needs to do.

## Mission

Turn the user's CV into a grounded, evidence-based job-market positioning strategy —
not an abstract self-assessment. Every claim about fit ("junior-ready," "gap in X,"
"strong in Y") must be backed by comparison against a real, current sample of job
vacancies, not intuition. The scraping/parsing/scoring machinery exists to make that
comparison possible at a scale a human can't do by hand.

The project is complete for a given market/role-family only when it can place the
user's evidence against a real distribution and answer three questions with data
behind them: *where do I land, what's actually missing, and which roles should I
target first.*

## Current phase: Stockholm market benchmark

The first application of the mission above. Prior stages (see project history)
established the user's profile qualitatively; this phase tests it against the real
market instead of continuing to reason about it in the abstract.

Order of work:

1. **Define the role families to search.** Not just "Data Engineer" — a controlled
   group: Junior Data Engineer, Data Engineer, Analytics Engineer, Data
   Integration/ETL Developer, Python/Data Developer, data-heavy Backend Developer,
   and selected Data Platform roles.
2. **Collect a meaningful sample of current Stockholm vacancies.** Analyse something
   like 30–50 relevant jobs, not five vacancies cherry-picked to suit the user.
3. **Extract comparable data from every vacancy:** required/preferred skills,
   experience expectations, education requirements, technologies, cloud platforms,
   responsibilities, Swedish/English requirements, seniority signals, company type,
   salary where available, and whether the job actually looks junior despite its
   title.
4. **Build the market distribution.** Distinguish:
   - market floor
   - typical junior
   - competitive junior
   - strong junior / early mid-level
   - stretch roles
5. **Place the user's current evidence against it.** Python, SQL, scraping/data
   ingestion, GCP, Docker, Linux, databases, AI systems thinking, education,
   professional experience, and GitHub evidence get scored against what employers are
   actually requesting — not against a generic job description.
6. **Identify gaps properly.** Each apparent weakness becomes exactly one of:
   - a **real capability gap** (needs learning),
   - an **evidence gap** (needs building — something exists but isn't demonstrable),
   - a **presentation gap** (already true, just not explained well).
7. **Choose 2–3 positioning lanes.** E.g. "Python/data ingestion engineer" as the
   strongest immediate lane, conventional Data Engineer as the main progression path,
   AI/data systems as the differentiator — or whatever the data actually shows, which
   may not match that guess.

Steps 1–3 are what the scraping/extraction side of this codebase produces. Steps
4–7 are analysis performed over that data — currently manual/conversational, not yet
automated, and don't need to be forced into code before they've been done by hand at
least once.

## Role families — Stockholm benchmark (step 1, draft)

Seven families, each earning its place by testing a distinct piece of the user's
evidence (Python, SQL, scraping/data ingestion, GCP, Docker, Linux, databases, AI
systems thinking). Search terms cover both English and Swedish postings, since
Stockholm listings mix both. This is a draft — react to it before it's locked in for
collection.

| # | Family | Why it's in scope | Titles to search (EN / SV) | Boundary |
|---|---|---|---|---|
| 1 | Junior Data Engineer | Direct target — matches current experience level exactly | "Junior Data Engineer", "Junior Dataingenjör", "Data Engineer (entry level)" | Explicit junior/entry signal in title or requirements |
| 2 | Data Engineer (unqualified) | Core family; many ads don't title-qualify seniority even when the role is effectively junior-friendly | "Data Engineer", "Dataingenjör" | Collect regardless of apparent seniority — seniority gets classified during extraction (step 3), not filtered out at collection |
| 3 | Analytics Engineer | Adjacent family, dbt/SQL/warehouse-modeling-centric — tests SQL + data-modeling evidence specifically, distinct emphasis from pipeline-engineering-flavored Data Engineer roles | "Analytics Engineer" | Swedish market rarely localizes this title; keep as-is |
| 4 | Data Integration / ETL Developer | Closest match to "scraping/data ingestion" evidence — pipeline-building without full engineering-team scope | "ETL Developer", "ETL-utvecklare", "Integration Developer", "Integrationsutvecklare", "Data Integration Engineer" | Include platform-specific titles too (e.g. "Azure Data Factory Developer") — technology fit is scored in step 5, not filtered here |
| 5 | Python/Data Developer | Tests general Python fluency directly — the single strongest, most portable piece of evidence | "Python Developer", "Python-utvecklare" | Narrowest family: a plain Python-developer ad with zero data/pipeline component is out of scope — must show some data-handling responsibility |
| 6 | Data-heavy Backend Developer | Tests databases + Docker/Linux + general engineering evidence, via backend roles with a real data-pipeline or data-service component | "Backend Developer", "Backend-utvecklare" | Exclude pure product/API-CRUD backend roles with no data angle — this family exists specifically to catch data-flavored backend work hiding under a generic title |
| 7 | Selected Data Platform roles | Tests GCP/Docker/Linux/infrastructure evidence — curated, not the full Platform Engineer universe (which skews pure infra/SRE) | "Data Platform Engineer", "Cloud Data Engineer", "GCP Data Engineer" | Include only when the platform work is explicitly data-oriented (data lake/warehouse infra, pipeline orchestration) — general cloud/DevOps/SRE roles stay out even if GCP-heavy |

Cross-family rules:

- **Seniority is not a collection filter, except at the extremes.** Senior/Lead/
  Principal/Head-of titles are excluded from the primary 30–50 sample by default —
  they'd swamp the floor/typical/competitive tiers step 4 is trying to build. A
  small, deliberate handful can still be pulled in later as "stretch roles" (step
  4's top tier), but that's a separate, intentional addition, not incidental
  inclusion.
- **Collection casts wider than the final positioning lanes will.** All seven
  families get sampled even though step 7 will likely narrow to 2–3 lanes — the
  distribution needs the full spread to show which families the user's evidence
  actually clears, rather than assuming the answer (e.g. family 5 or 6) before the
  data is in.

Open item, not resolved here: this repo currently has two live collection paths —
Platsbanken's API (free-text `q`, plus `occupation-group` taxonomy codes resolvable
via the taxonomy API per `flow/fetch_jobs_from_api.py`'s docstring) and
jobbsafari.se's spider (hardcoded today to one `yrke` category, "utvecklare", per
`spiders/jobbsafari_listing_spider.py`). Neither has been checked yet for how well
its own taxonomy maps onto these seven families — that's collection-mechanics work
for step 2, not step 1.

## Step 2 collection log (Stockholm, 2026-08-20)

First real run of steps 1–2, using only the two collection paths that already
existed — nothing new was built for this. `job_posting` was cleared first (it held
763 unrelated rows from earlier pipeline dev/testing — excavator operators, generic
.NET/Java postings — not benchmark data).

- **Platsbanken API** (`fetch-jobs --region CifL_Rzy_Mku`, one run per family query):
  `"data engineer"` (53), `"dataingenjör"` (40), `"analytics engineer"` (451),
  `"ETL"` (25), `"data integration"` (750), `"python developer"` (51), `"data
  platform"` (145), `"backend developer"` (58) — 988 unique rows saved after
  dedup-by-URL.
- **jobbsafari.se spider** (`jobbsafari_listing`, unchanged — still fixed to the
  Stockholm "utvecklare" category): 332 items.

**Finding: the API's `q` is loose OR-matching, not a phrase search.**
`"analytics engineer"` alone returned 451 rows — mostly unrelated titles containing
just "Engineer" (Electrical Engineer, PCB Design Engineer, Maintenance Engineer,
...). `"data integration"` returned 750 for the same reason. Two-word queries where
one word is rare (`"data engineer"`, `"dataingenjör"`) stayed reasonably precise on
their own; queries containing a common word ("engineer", "integration", "backend",
"developer") did not. **Consequence: `q` is a recall tool, not a filter** — every
query's results still need title/description filtering afterward, which is exactly
what the role-family boundary rules drafted in step 1 turned out to be for. Confirms
those rules were the right call rather than a formality.

Title-keyword curation of the combined 1,320 rows (query run 2026-08-20, exact SQL
in shell history, not preserved as code — this was a one-off analysis pass, not a
reusable tool):

| Family | Clean title matches | Note |
|---|---|---|
| 1–2 Data Engineer / Junior Data Engineer | 49 distinct | High precision straight from title; largest family by far — a real market signal in itself, not a collection artifact |
| 3 Analytics Engineer | 6 | Clean |
| 4 ETL / Integration | 8 | Clean |
| 5 Python/Data Developer | ~2–3 of 9 title-matches | Confirms the boundary rule: most "Python" titles were plain web/systemutvecklare roles with no visible data component; Nordea's "Model and Python Developer – Counterparty Credit Risk" is the clear qualifier |
| 6 Data-heavy Backend Developer | 2 of 48 title-matches | Sharply confirms the boundary rule: 46 of 48 backend postings (game studios, .NET/Java/C#) have no data angle; only PEAB's "Backendutvecklare inom Data & Analytics" (ETL/Snowflake/Azure, appears twice — likely one role re-listed) actually qualifies |
| 7 Data Platform | 4 | Clean |
| *(unmatched)* | 1,194 | Noise from the loose `q` matching above — not part of the sample |

~75–80 distinct postings currently qualify by title (before description-level
seniority/gap extraction from step 3 narrows or reclassifies some of them) — above
the 30–50 floor step 2 asked for, mostly on the strength of family 1–2 alone. Several
rows turned out to be duplicate listings (e.g. "Junior Data Engineer" at Nextory AB,
"Senior integrationsutvecklare" at Quest Consulting each appeared twice) — see the
"Deduplication" section below for the fix; the curated count after dedup is 71, not
75.

**Not yet done (at the time this section was written):** deciding whether to trim
family 1–2 down for balance against the much smaller families 3/5/6/7, and running
step 3's extraction over the curated set. The `job_posting` table right now holds
the full 1,320-row raw pull, not the curated ~75–80 — there's no `role_family`
column yet to persist the curation itself (see the data-model note below), so the
curated list currently only exists as this log entry.

## Step 3 extraction (built 2026-08-20)

Built the extraction vertical the previous section only sketched, now that the
sample's real shape was known (per that section's own sequencing note). Placement
follows `Behavioral Architecture.md`/`structure.md` exactly — see `structure.md`'s
new "Job-signal extraction vertical" section for the file-by-file breakdown; nine
small `logic/` pieces (one per determination: role family, seniority, language
requirement, education requirement, company type, technologies, cloud platforms,
years-required, salary), bundled into `state/job_signals.py` by
`flow/extract_job_signals.py` (`cv_scrape extract-signals`), persisted to a new
`job_signals` SQLite table.

**A heuristic mistake and its fix, worth remembering:** the first version of the
Python/backend "does this actually have a data component" check (the boundary rule
family 5/6 exist for) used the bare words `"data"` and `"analytics"` as its hint
list. Run against the real sample, this matched 37 of 51 `Backend Developer`
postings — including several game studios with no data responsibility at all —
because "data" appears incidentally in almost any job ad (player data, GDPR
boilerplate). Tightened to specific compound markers (`"data pipeline"`, `"data
warehouse"`, `"etl"`, `"dbt"`, `"databricks"`, `"snowflake"`, ...), which dropped
the false-positive count to 6, all genuinely data-adjacent on manual spot-check
(one of them, Validio AB, turned out to literally be a data-quality/observability
company). Lesson for any future hint list in this codebase: a single common word
as a boundary condition isn't a heuristic, it's a coin flip — this is exactly the
"much more detailed parse regex function" need flagged earlier in this document,
now built and empirically corrected once.

Results, run over the full 1,320-row collected set:

| Family | Count | Seniority split |
|---|---|---|
| Data Engineer / Junior Data Engineer | 51 | 2 junior-friendly, 45 mid/senior, 4 unclear |
| Data-heavy Backend Developer | 6 | 4 mid/senior, 2 unclear |
| ETL/Integration | 8 | 7 mid/senior, 1 unclear |
| Analytics Engineer | 6 | 6 mid/senior |
| Data Platform | 4 | 4 mid/senior |
| Python/Data Developer | 0 | — (Nordea's "Model and Python Developer" no longer clears the tightened hint list; a known, accepted precision/recall tradeoff, not re-tuned to fit one example) |

Across the 75 classified postings: only **2** read as junior-friendly by title +
text combined — the market floor for this role family group in Stockholm is
effectively mid-level, not junior, on this sample. 61 of 75 state no explicit
language requirement (14 explicitly require Swedish), 68 of 75 state no explicit
education requirement, 56 of 75 read as direct employers vs. 19
consultancy/staffing. Most-mentioned technologies: SQL (53), Python (40), dbt (36),
Snowflake (29), Databricks (21), Airflow (20); cloud platforms: Azure (38) > AWS
(28) > GCP (19) — GCP, the platform in the user's own evidence, is the
*least*-requested of the three, not the most.

**Not yet done (at the time this section was written):** deduplication, building the
market-tier distribution (step 4) from these signals, placing the user's evidence
against it (step 5), and gap/positioning-lane output (steps 6–7). The
`technologies`/`role_family` keyword lists are a first pass — they'll under-count
postings that use less common phrasing (e.g. AWS-specific service names instead of
"AWS") and should be revisited once step 4/5 reveal which gaps in coverage actually
matter to the analysis.

## Deduplication (done 2026-08-20)

The four repeat groups flagged in step 2 (Nextory AB, Techrytera AB, Quest
Consulting Sverige AB, Validio AB) turned out to be two distinct duplicate shapes,
confirmed by comparing description length/content per pair, not just title+company:

- **Cross-source repost**: the same ad picked up by both `arbetsformedlingen.se`
  (Platsbanken API) and `jobbsafari.se` (its own spider) — near-identical
  description length, posted within a day of each other.
- **Same-source resubmission**: the employer submitted the same ad twice on
  Platsbanken under two different ad IDs, a minute apart, identical description
  length.

Neither shape is catchable by the store's own `url` primary key, since both produce
distinct URLs for what is the same real vacancy — this had to be a decision over the
data, not a storage constraint. Built `logic/deduplicate_job_postings.py`: groups by
normalized (title, company), keeps the copy with the earliest `posted_at` (falling
back to first-seen order when a date is missing or ties can't be compared), pure
function over `list[JobPosting]`, six tests. Deliberately title+company only, not
fuzzy/description matching — same "one rule" reasoning as `classify_role_family.py`:
extend it if real data ever shows two genuinely different postings sharing a
title+company (not seen yet), don't pre-build for it.

Run over the curated (non-`UNMATCHED`) 75-posting set: **75 → 71**. All 4 dropped
rows were exactly the two duplicate shapes above, no unexpected collapses.

| Family | Before | After |
|---|---|---|
| Data Engineer / Junior Data Engineer | 51 | 49 |
| ETL/Integration | 8 | 7 |
| Data-heavy Backend Developer | 6 | 5 |
| Analytics Engineer | 6 | 6 |
| Data Platform | 4 | 4 |

The market-floor/tech/cloud findings in the Step 3 section above are unaffected in
substance (all four dropped rows are Data Engineer/ETL/Backend, the largest
families, and none were among the 2 junior-friendly postings) — the 71-count is now
the number step 4 should build the tier distribution from, not 75.

Not yet wired into a `flow/`/CLI entry point. It was called directly from a one-off
scratch script for the step 4 analysis below (same role a one-off SQL pass played in
step 2) — still not wired to a persistent flow, since step 4 itself stays manual per
this document's own sequencing note, not a new automated vertical.

## Step 4 market distribution (built 2026-08-20)

Per this document's own sequencing note ("steps 4–7 ... don't need to be forced into
code before they've been done by hand at least once"), this is a documented analysis
pass over the 71 deduped signals, not a new `logic/`/`flow/` vertical — a one-off
scratch script, not committed.

**Method.** The extracted signals don't carry a ready-made demand ordinal, so one had
to be built: a per-posting **experience score** (the deciding axis) —
`years_experience_required` when the posting states one; otherwise `0` for
`JUNIOR_FRIENDLY`, `6` for a senior-marker title word (`"senior"`, `"lead"`,
`"principal"`, `"erfaren"`, `"expert"`) with no explicit figure, `4` as a
flat default for `MID_OR_SENIOR` from body language alone, `2` for `UNCLEAR`. **This
default-4 case is the single biggest bucket in the whole sample (36 of 71) and is a
real limitation worth stating plainly**: for those 36, "4" is a modeling stand-in for
"reads as wanting real experience, no number given," not an observed figure — the
extraction's own honesty gap (see `technologies`/`role_family` note in the Step 3
section) shows up here too. Tech+cloud-platform breadth (count of distinct
technologies mentioned) was used as the tie-breaker to split that one oversized
bucket, since it's the only signal that actually varies across it and correlates
sensibly with role scope.

**Tiers**, cut at the natural breaks the sorted score produced (full sorted list not
preserved as code, per the method note above):

| Tier | Rule | n | What it looks like |
|---|---|---|---|
| 1. Market floor | experience score ≤ 2 (no years stated, no senior language anywhere — the single `JUNIOR_FRIENDLY` posting plus 6 `UNCLEAR` ones) | 7 | All `DIRECT_EMPLOYER`, no language/education requirement stated, avg. 6.6 tech mentions. Not "junior-labeled" — it's simply the least-demanding tier that actually exists |
| 2. Typical junior | experience score = 3 (explicit "3 years" is the lowest *quantified* bar anywhere in the sample) | 8 | All `DATA_ENGINEER`-titled; half staffing/consultancy; still no education requirement |
| 3. Competitive junior | experience score = 4, tech+cloud breadth ≤ 5 | 21 | The narrower-scope half of the "wants experience, unspecified" bucket; light on named tools (avg. 3.4) |
| 4. Strong junior / early mid-level | experience score = 4 with breadth ≥ 6, or explicit 5-year requirement | 25 | The largest tier — broad tool lists (avg. 7.3: SQL/Python/dbt/Snowflake/Azure dominate), starts showing `DEGREE_PREFERRED` (4 of 25) |
| 5. Stretch | experience score ≥ 6 (title says "Senior"/"Lead"/"Erfaren", or an explicit 8-year requirement) | 10 | Almost entirely `DIRECT_EMPLOYER`; the only tier where `SWEDISH_REQUIRED` share rises noticeably (3 of 10) |

**Reading the shape, not just the tiers.** 7 + 8 = 15 of 71 (21%) sit at or below a
quantified 3-year bar; the remaining 79% cluster from "meaningful but unstated
experience" through "explicit 5 years" through "senior." There is effectively no
0–1-year tier in this sample — confirms the Step 3 finding (2 of 75, now the single
survivor at 71) from a different angle: the Stockholm market for these seven
families doesn't really have an entry-level floor, it has a *lower-demand* floor
that still assumes some prior experience. Tiers 3–4 (46 of 71, two-thirds of the
sample) are where the real weight of the market sits, not tier 1 or 2 — this is
where step 5's evidence-placement should focus, not the thin true floor.

No systematic salary or language signal by tier worth reporting — `salary_mentioned`
is populated in only 3 of 71 rows total (too sparse to break out per tier),
Swedish-required share stays low and roughly flat until tier 5.

## How this reshapes the existing vertical

The scrape → parse → match pipeline in `structure.md` was built generically, ahead of
this methodology. It will need to grow to actually serve it — this section is a
forward note, not a spec to implement immediately:

- **`state/job_posting.py`** currently holds only title/company/description/location.
  Step 3's extraction (skills, tech, cloud platforms, seniority signals, language
  requirements, salary, company type, role family) is richer than free-text
  `description` can serve for comparison — it will need structured fields or a
  companion extraction result, decided when that extraction logic is actually
  written (see `Behavioral Architecture.md`'s reify rule: the extracted structured
  read is a value, distinct from the raw posting).
  - Step 3's fields split into two kinds, and the split matters for what needs
    building: **read fields** come off the page mostly as-is (title, company,
    location, salary when a site publishes it as a discrete number). **Inferred
    fields** — seniority signal, role-family fit, language requirement, arguably
    company type — are rarely stated as a labeled field anywhere on the page; they
    have to be read out of the free-text description/requirements section
    (e.g. "looks junior despite its title" per step 3 is, by definition, not
    recoverable from the title field). Those need dedicated
    extraction/classification logic over already-fetched description text —
    pattern/keyword-based to start (years-of-experience phrasing, degree
    requirements, "fluent Swedish required" vs. "English is fine," etc.) — which is
    a pure decision over text already in hand once the posting is fetched, so it's
    `logic/` per `Behavioral Architecture.md`, not a new fetch or a new boundary.
    It's buildable independently of the rest of the schema work, since it only
    needs raw description text, not the final field layout — but per the note
    below, still worth sequencing after a first look at real description text from
    the sample, so the patterns are built against what postings actually say
    rather than guessed in advance.
- **`logic/score_match.py`** / **`state/match_score.py`** are stubs shaped for a
  single scalar score. Step 4–5 need the user's evidence placed against a
  *distribution*, not scored against one job at a time — the market tiers (floor /
  typical junior / competitive junior / strong junior / stretch) are themselves data
  that doesn't exist yet in `state/`.
- **Role family** (step 1) doesn't exist anywhere in the current model; job postings
  and any distribution/tier logic will need to be taggable by it.
- **Gap classification** (step 6) and **positioning lanes** (step 7) are new kinds of
  output this project doesn't produce today — a `MatchScore` records fit against one
  job, not a capability/evidence/presentation determination against a role family's
  whole sample.

None of this is a green light to start writing those pieces — place them by the
`Behavioral Architecture.md` rules when the methodology above has actually been run
once and the real shape of the data is known, not before.

## Status

- Role families for the Stockholm benchmark: drafted (see above), not yet locked in.
- Vacancy sample: raw collection done via the two existing sources (Platsbanken API,
  jobbsafari.se spider), curated to 75 by title/description role-family matching,
  deduplicated to 71 — see "Step 2 collection log" and "Deduplication" below. Still
  not locked: whether to trim family 1–2 for balance.
- Extraction schema: built and run over the full collected sample — see "Step 3
  extraction" above. `JobPosting` itself is unchanged; signals live in the new
  `job_signals` table instead of extending `JobPosting`.
- Deduplication: done — `logic/deduplicate_job_postings.py`, 75 → 71.
- Market distribution / tiers: done — see "Step 4 market distribution" above. 5
  tiers over the 71 deduped postings (7 / 8 / 21 / 25 / 10); documented analysis,
  not code, per this document's own step 4–7 sequencing note.
- Step 5 handoff: the market-side output of steps 1–4 is written up standalone in
  `Market Benchmark Findings.md`, for another agent (one with the user's actual
  CV/evidence) to combine with that evidence and produce steps 5–7. This repo's
  pipeline produces the market side of the comparison; it doesn't hold the user's
  evidence (the `cv` table is empty, no CV file exists in this repo) — step 5 needs
  that supplied separately, not guessed from the category list in this document's
  Mission section.
- Steps 5–7: done (2026-08-21), once `candidate.yaml` supplied the evidence the
  handoff above was waiting on. Findings in `Candidate Placement Findings.md`:
  placement against the 71 deduped postings by family/tier, gap classification
  (dbt/warehouse confirmed as the load-bearing capability gap; CI/CD ownership
  un-auditable against the current extractor; Scala flagged as frequency without
  requirement-strength data, not a confirmed gap), positioning-lane validation, and
  a learning-ROI ranking. Also identifies the next concrete build (requirement-
  strength extraction) as the one that would most improve this analysis, ahead of
  generalizing it into `evaluate_candidate_against_job()`.
- Requirement-strength extraction: built (2026-08-21) —
  `logic/classify_technology_requirement_strength.py`, wired through the
  `[SIGNALS]` vertical, `extract-signals` re-run over the full stored sample. Steps
  6/7 revisited in `Candidate Placement Findings.md` using it: the Scala flag is
  resolved (30% REQUIRED+PREFERRED vs. dbt's 69% — a real but moderate gap, not a
  top-tier one, confirming `candidate.yaml`'s own low-priority filing of it),
  Databricks' leverage was previously under-rated, and Data Platform/Analytics
  Engineer's closed-off verdicts were re-derived: Data Platform's SKIPs are
  seniority/years-driven (tech-independent), Analytics Engineer is thinner than
  "closed" implied (2 of 6 postings only mention, don't require, the dbt/Snowflake
  gap). CI/CD ownership remains un-auditable — out of scope for this build, needs a
  separate extraction-vocabulary fix. `evaluate_candidate_against_job()` is now
  unblocked as the next generalization step, not yet started.
