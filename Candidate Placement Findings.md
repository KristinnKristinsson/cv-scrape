# Candidate Placement — Steps 5–7 (2026-08-21)

This is steps 5–7 of the methodology in `Objectives.md`, run now that `candidate.yaml`
supplies the evidence `Market Benchmark Findings.md` was waiting on ("Step 5 needs the
user's actual evidence... supplied separately"). Per `Objectives.md`'s own sequencing
note, this is a documented analysis pass, not new `logic/`/`flow/` code — same
treatment steps 4 got.

**Data used:** the 71 deduped, curated postings' `job_signals` rows (queried directly
from `data/cv_scrape.db`, not just the aggregate tables in `Market Benchmark
Findings.md`) against `candidate.yaml`'s `capability_model`. Working from per-posting
rows rather than the published averages so placement is against real vacancies, not
summary statistics.

## Method

Candidate technologies split by evidence class, using `extract_technologies_mentioned`'s
own keyword vocabulary (the only technologies a posting *can* register as requiring):

- **Strong (class A/B, level ≥3):** Python, SQL, Airflow, Git, Linux, Docker, Pandas,
  MySQL.
- **Zero (evidence_class `[]` or level ≤1):** dbt, Snowflake, Databricks, Scala, Kafka,
  Terraform, BigQuery, Java, T-SQL.
- **Cloud:** GCP held (operational only, per `candidate.yaml`'s explicit
  `not_claimed` list — no architecture/Terraform/IAM); Azure and AWS not held at all.

Per posting: recommendation follows `candidate.yaml`'s own `job_evaluation_guidance`
section, made mechanical —

- **SKIP** if title carries a senior/lead/principal marker, or years-required ≥5, or
  ≥3 zero-evidence technologies are named with ≤1 strong-technology overlap.
- **APPLY** if ≥2 strong technologies are named and zero blockers are named.
- **APPLY-STRETCH** if ≥2 strong technologies are named alongside ≤2 blockers.
- **LOW PRIORITY** if only one strong technology is named, with no disqualifier.

This mechanizes rules `candidate.yaml` already wrote in prose; it does not add new
judgment. Rebuilding as `evaluate_candidate_against_job()` later should keep this same
default-apply-unless-disqualified shape rather than a distance/similarity score.

## Recommendation distribution (71 postings)

| Recommendation | n | Share |
|---|--:|--:|
| APPLY | 5 | 7% |
| APPLY-STRETCH | 13 | 18% |
| LOW PRIORITY | 23 | 32% |
| SKIP | 30 | 42% |

**18 of 71 (25%) are apply-now candidates.** Extending to LOW PRIORITY (some real
overlap, just thinner), 41 of 71 (58%) aren't a poor match on technology grounds —
they're excluded from the SKIP pile mainly by seniority language or blocker density,
not by a lack of any relevant evidence at all.

## By family

| Family | n | APPLY | STRETCH | LOW | SKIP |
|---|--:|--:|--:|--:|--:|
| Data Engineer (incl. Junior) | 49 | 4 | 11 | 17 | 17 |
| ETL / Integration | 7 | 1 | 0 | 3 | 3 |
| Data-heavy Backend | 5 | 0 | 2 | 1 | 2 |
| Analytics Engineer | 6 | 0 | 0 | 2 | 4 |
| Data Platform | 4 | 0 | 0 | 0 | 4 |

Confirms two things `Objectives.md`/`candidate.yaml` already suspected, now with
numbers behind them:

- **Analytics Engineer is close to closed off** — 4 of 6 SKIP, the other 2 LOW
  PRIORITY, zero APPLY/STRETCH. This family is dbt/Snowflake/warehouse-modeling by
  construction (`Objectives.md` step 1's own framing), and dbt sits at
  `level_0_to_5: 0` with no evidence class at all. Not a presentation problem — a
  real, currently-total capability gap for this specific family.
- **Data Platform is fully closed for now** — 4 of 4 SKIP. `candidate.yaml` already
  filed this as a "stretch" lane; the data agrees more strongly than that label
  suggests — none of the 4 postings clear even the STRETCH bar. Consistent with GCP
  being the least-requested cloud in this market (`Market Benchmark Findings.md`) and
  this family's top technologies (Scala, Databricks, BigQuery) being mostly
  zero-evidence for the candidate.
- **Data Engineer carries essentially the whole opportunity set** — 15 of 18 apply-now
  postings, 32 of 41 non-SKIP postings. This is the primary lane
  `candidate.yaml`'s `market_positioning` already names, now with a denominator: not
  "the strongest lane" in the abstract, but "the only lane with a meaningful volume of
  currently-reachable roles" in this sample.

## Gap classification (step 6)

Per `Objectives.md` step 6, each apparent weakness is exactly one of: real capability
gap, evidence gap, or presentation gap.

- **Real capability gaps (needs learning), confirmed by market data:**
  - **dbt** — 0 evidence, appears as a blocker in 21 of the 41 non-SKIP postings
    (51%). The single most consequential gap in the sample.
  - **Snowflake / BigQuery (warehouse layer)** — 0 evidence, dbt and Snowflake
    co-occur in 22 of 35 dbt-mentioning postings — these aren't two independent gaps,
    they're one "modern warehouse stack" cluster candidate.yaml's own
    `suggested_entry: BigQuery` note already anticipated. BigQuery co-occurs with a
    GCP cloud requirement in only 6 of 12 postings that mention it, so it isn't
    exclusively a GCP-adjacent skill in this market, but it remains the natural entry
    point given existing GCP operational evidence.
  - **Databricks** — 0 evidence, blocker in 12 of 41 (29%), usually alongside Spark
    and Scala rather than standalone.
- **Unresolved / not auditable against this sample:**
  - **CI/CD ownership** — `candidate.yaml` lists this as a high-priority gap, but
    `extract_technologies_mentioned.py`'s keyword vocabulary doesn't track CI/CD tools
    at all (no "GitHub Actions," "GitLab CI," "Jenkins," etc. in its list). This claim
    is currently un-auditable against real postings — not confirmed, not refuted. Real
    limitation of the current extraction, worth fixing before leaning on this gap
    further.
  - **Scala** — see "What this reveals for what to build next" below; frequency alone
    overstates this as a gap without requirement-strength data.
- **No presentation gaps stood out as decisive** in this pass — the disqualifying
  factor in most SKIP cases was seniority language or blocker density, not
  under-explained existing evidence. (`candidate.yaml`'s own development-area entry on
  technical communication may still matter at interview stage; it doesn't show up in
  this posting-level filter.)

## Learning ROI (step 6/7 input)

Ranked by (a) frequency as a blocker among otherwise-reachable postings and (b)
whether it's a standalone skill or part of a cluster:

1. **dbt — highest leverage.** Blocks 51% of otherwise-reachable postings; a single
   skill, not a cluster; directly extends existing SQL depth.
2. **BigQuery (as warehouse entry point) — high leverage.** Smaller raw count (12 of
   71) but the most transferable choice given existing GCP operational evidence;
   opens Analytics Engineer and Data Platform postings that are currently fully
   closed.
3. **Snowflake — moderate leverage, redundant with BigQuery.** Same functional slot
   as BigQuery for most postings; picking one warehouse platform (BigQuery, per
   existing GCP evidence) likely captures most of the value both would separately —
   don't treat these as two gaps to close.
4. **Databricks — lower leverage than raw frequency (21 of 71) suggests.** Usually
   bundled with Spark and Scala in postings that also carry other blockers; closing
   it alone doesn't flip many postings from SKIP to APPLY.
5. **Scala — do not act on this yet.** See below.

**Scala flag, worth surfacing directly:** Scala appears in 27 of 71 postings (38%,
third-most-mentioned technology in the whole sample) — more than Databricks, and
`candidate.yaml`'s own `current_major_gaps` doesn't list it at all (filed only under
`explicit_non_claims`/`lower_priority_for_immediate_search`, alongside
Terraform/Kubernetes/Kafka). 23 of those 27 postings also carry ≥2 of the candidate's
strong technologies (Python/SQL/Airflow/Git), meaning most "Scala" postings are
otherwise squarely in range. But the extractor only records that the word "Scala"
appears in the text — it cannot currently tell "Scala is the primary implementation
language" apart from "Scala is one bullet in a ten-technology stack list, Python is
fine." Treating Scala as confirmed-high-priority on frequency alone would repeat
exactly the mistake `candidate.yaml`'s own design principle warns against (self-
assessment as hypothesis, not fact) — just inverted, market-side. This is flagged, not
resolved.

## Positioning lanes (step 7) — validated, not just repeated

`candidate.yaml`'s `market_positioning` section already names three lanes. Checking
each against this sample rather than restating them:

- **Primary lane, "Data Engineer — ingestion/reliability/pipelines": confirmed as the
  correct primary lane**, and more narrowly than the label suggests — it's carrying
  15 of 18 apply-now postings. Not "a good lane among several," the load-bearing one.
- **Secondary lane, "Python/data-focused Software Developer": weakly supported.**
  Data-heavy Backend Developer (the closest family match) only produced 5 postings
  total, 2 STRETCH. Real but thin — not a lane with much current volume in this
  sample, whatever its longer-run value.
- **Emerging lane, "Applied AI + grounded data systems": untestable from this data.**
  No job-posting technology keyword captures it (nothing in
  `extract_technologies_mentioned.py`'s vocabulary maps to "LLM," "AI," "MCP," etc.),
  consistent with `candidate.yaml` already filing it as "differentiator, not yet a
  primary job identity" rather than a searchable lane.

## What this reveals for what to build next

The design discussion preceding this file proposed building `evaluate_candidate_against_job()`
next, with a **requirement-strength** field (`explicitly required` /
`strongly expected` / `preferred` / `merely mentioned`) as part of the market model.
This pass is direct evidence that field is the actual blocking gap, not a
speculative nice-to-have: the Scala finding above is exactly the shape of error
requirement-strength exists to prevent — a technology that's frequent in the raw
keyword sense but whose actual centrality to each specific role is unknown. Recommend
building requirement-strength extraction (a `logic/` piece reading each posting's
description for "required," "meriterande," "plus," "nice to have" context around each
matched keyword) as the next concrete step before generalizing this analysis into
`evaluate_candidate_against_job()` — it directly resolves the least-trustworthy part
of the gap ranking above, and it's buildable over data already collected, no new
scraping needed.

Two smaller data-quality notes surfaced while running this: two PEAB "Backendutvecklare
inom...Data & Analytics" postings from the same company (`A Hub AB` recruiting for
PEAB) survived dedup because their titles differ by one phrase
("...inom lösningsarkitektur för Data & Analytics" vs. "...inom Data & Analytics") —
`Objectives.md`'s Step 2 log already flagged this exact pair as "likely one role
re-listed" without fully resolving it; title-normalized dedup won't catch a
paraphrase, which `logic/deduplicate_job_postings.py`'s docstring already scopes
itself to (title+company exact match, extend only if real data shows it's needed —
this is that data point, not yet acted on). And `extract_technologies_mentioned.py`
tracks `"postgres"` and `"postgresql"` as two separate keywords that will double-count
the same posting — cosmetic, doesn't change any finding above.

## Revisit with requirement-strength data (2026-08-21, continued)

`classify_technology_requirement_strength` (see `Objectives.md`) is now built and
`extract-signals` has been re-run over the full stored sample, so every technology in
`job_signals.technologies` now carries `REQUIRED`/`PREFERRED`/`MENTIONED` instead of
being a bare name. This closes the gap the previous pass explicitly flagged as
unresolved — redoing the same 71-posting curated/deduped sample (reconstructed fresh:
`role_family != UNMATCHED` joined against `job_posting`, run back through
`logic/deduplicate_job_postings.py`, 75 → 71 again) with a **blocker** now defined as
a zero-evidence technology at `REQUIRED` or `PREFERRED` strength, not any mention.

### Scala, resolved

| | count | REQUIRED | PREFERRED | MENTIONED | REQUIRED+PREFERRED share |
|---|--:|--:|--:|--:|--:|
| dbt | 35 | 14 | 10 | 11 | **69%** |
| Databricks | 21 | 8 | 5 | 8 | 62% |
| Snowflake | 27 | 12 | 2 | 13 | 52% |
| Kafka | 10 | 4 | 3 | 3 | 70% (small n) |
| Terraform | 10 | 2 | 4 | 4 | 60% (small n) |
| Java | 6 | 2 | 1 | 3 | 50% (small n) |
| **Scala** | **27** | **6** | **2** | **19** | **30%** |
| BigQuery | 12 | 4 | 0 | 8 | 33% |

Scala's raw frequency (27 of 71, third-most-mentioned) is confirmed to have been
misleading: 19 of those 27 mentions (70%) are `MENTIONED`-only — one line in a stack
list — not an actual requirement. Its `REQUIRED`+`PREFERRED` count (8) is barely above
Kafka (7) and Terraform (6), and well below dbt (24), Databricks (13), and Snowflake
(14). **The earlier flag is resolved: Scala is a real but moderate-priority gap, not
a top-tier one.** `candidate.yaml`'s own filing of it under
`lower_priority_for_immediate_search` alongside Terraform/Kubernetes/Kafka turns out
to be right, not a presentation risk — the market data now agrees rather than
just being silent on it.

### Updated learning ROI ranking (by REQUIRED+PREFERRED count, i.e. real signal, not raw mentions)

1. **dbt — still highest leverage, more confidently now.** 24 of 35 mentions are
   actual requirements (69%), the highest rate of any zero-evidence technology, not
   just the highest raw count.
2. **Databricks — moves up.** 13 of 21 (62%) are real requirements — higher-rate than
   Snowflake, contrary to the previous pass's "lower leverage than raw frequency
   suggests" call. Revise that: Databricks was actually under-rated before, not
   over-rated — the earlier caveat assumed most mentions were incidental stack-list
   noise, which strength data shows isn't true here.
3. **Snowflake — still real, still largely redundant with BigQuery** for the postings
   that need a warehouse platform at all; 14 of 27 (52%) required/preferred.
4. **Scala — moderate, not urgent.** 8 of 27 (30%) required/preferred — worth learning
   eventually (roughly Kafka/Terraform tier), not a near-term blocker the way dbt is.
5. **BigQuery — leverage claim softens.** Only 4 of 12 mentions (33%) are actual
   requirements, and per the family breakdown below, BigQuery's zero-evidence weight
   in Analytics Engineer/Data Platform postings isn't the deciding disqualifier there
   — those families are closed off by years/seniority language, not by BigQuery
   specifically. Still the sensible warehouse entry point given existing GCP
   operational evidence, but "opens Analytics Engineer and Data Platform" (previous
   pass's claim) doesn't hold up: see below.

### Recommendation distribution, recomputed

Same mechanical rule as the original pass, blocker definition changed from "any
mention of a zero-evidence technology" to "REQUIRED or PREFERRED only." (Recomputed
fresh against the same written rule, not a byte-for-byte replay of the original
one-off script — that script was never preserved as code, same caveat this document
already carries for the market-tier reconstruction.)

| Recommendation | n | Share |
|---|--:|--:|
| APPLY | 12 | 17% |
| APPLY-STRETCH | 15 | 21% |
| LOW PRIORITY | 9 | 13% |
| SKIP | 35 | 49% |

**38% (27 of 71) are now apply-now candidates**, up from 25% (18 of 71) under
bare-mention blockers. This is not the market getting easier — it's the previous
number being an underestimate, because most zero-evidence "blockers" it counted
weren't actually required. The SKIP share also rose (30 → 35): postings with genuine
`REQUIRED`/`PREFERRED` zero-evidence blockers alongside real strong-technology overlap
sort more decisively into SKIP now, instead of landing in the middle bands on raw
mention count alone.

By family, most of the shift lands in Data Engineer (APPLY 4→10, STRETCH 11→12, LOW
17→5, SKIP 17→22 — same underlying pattern: sharper separation now that mentions and
requirements are told apart). Two family-level findings from the original pass need
correction:

- **Data Platform's 4/4 SKIP is confirmed, but for a different, more solid reason
  than assumed.** All four postings' SKIP verdict traces to `years_experience_required
  = 5` (three postings) or a "Senior" title (the fourth) — not to zero-evidence tech
  blockers at all. The strength data doesn't change this family's outcome; it
  independently confirms it wasn't actually about the tech gap. **Correction to the
  previous pass's Learning-ROI claim:** BigQuery/Databricks would not open these four
  postings even at full strength, because seniority/years is the disqualifier, not
  the tech stack.
- **Analytics Engineer is less closed than the original framing suggested.** Was 0
  APPLY / 0 STRETCH / 2 LOW / 4 SKIP; now 1 APPLY / 1 STRETCH / 0 LOW / 4 SKIP. Two
  of the six postings ("Analytics Engineer till UR i Stockholm," "Analytics Engineer,
  Finance") have dbt/Snowflake/BigQuery at `MENTIONED` only, not `REQUIRED` — the
  candidate's dbt=0 evidence isn't actually disqualifying for those two specific
  postings. The other 4 SKIPs are still title/years-driven (3 "Senior"-titled, one
  with `years=5`), same as Data Platform above. **Revised finding: Analytics Engineer
  is thin, not closed** — real but limited volume, consistent with (not contradicting)
  `candidate.yaml`'s dbt=0 gap, just less absolute than "4 of 6 SKIP, zero APPLY/STRETCH"
  implied.

### What this confirms about the earlier CI/CD caveat

Unchanged and still worth restating: CI/CD ownership remains un-auditable against this
extractor (`extract_technologies_mentioned.py` has no CI/CD keyword vocabulary at
all). Requirement-strength doesn't help here — it operates on technologies the
extractor already matches, and CI/CD tools aren't in that list. Still an open
extraction gap, not resolved by this pass.

## Caveats carried over

- Years-required is stated in only 15 of 71 postings — most APPLY/STRETCH
  recommendations above rest on technology overlap, not a verified years comparison,
  because the field is usually absent, not because it was checked and cleared.
- Technology detection is the same first-pass keyword vocabulary
  `Market Benchmark Findings.md` already flagged as a floor, not a ceiling — a
  posting requiring "AWS Glue" without the word "AWS" spelled out, for instance,
  won't register.
- This is one snapshot (2026-08-20 collection, `candidate.yaml` v2026-08-21). No
  trend claim is made here — that needs the "never overwrite a scrape" collection
  discipline the design discussion proposed, which isn't built yet.
