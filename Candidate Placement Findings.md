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
  - **CI/CD ownership** — was un-auditable against real postings at the time this
    section was written; resolved by the extraction-vocabulary fix below (see "Third
    revisit").
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

Unchanged at the time this section was written: CI/CD ownership remained un-auditable
against this extractor (`extract_technologies_mentioned.py` had no CI/CD keyword
vocabulary at all). Requirement-strength didn't help here — it operates on
technologies the extractor already matches, and CI/CD tools weren't in that list.
Resolved in the "Third revisit" section below.

## Second revisit: evaluate_candidate_against_job() built (2026-08-21, continued)

`evaluate_candidate_against_job()` (see `Objectives.md`, `structure.md`'s `[FIT]`
section) is now real, tested code, run via `cv_scrape evaluate` over the same 71
curated, deduped postings both prior passes analyzed by hand/scratch script. Results:

| Recommendation | n | Share |
|---|--:|--:|
| APPLY | 14 | 20% |
| APPLY_STRETCH | 23 | 32% |
| LOW_PRIORITY | 12 | 17% |
| SKIP | 22 | 31% |

**52% (37 of 71) are apply-now candidates**, up from 38% in the requirement-strength
revisit above. This is not a third independent re-derivation confirming the same
number — three deliberate rule changes went into the built code, distinct from
formalizing the existing rule verbatim, and they each pushed in the same direction:

1. **The years fix (the change this build was explicitly scoped around).** Both prior
   passes used a hard `years ≥ 5 → SKIP`. `candidate.yaml`'s own text says not to:
   "do not automatically reject a vacancy because stated years exceed the candidate's
   chronological experience... evaluate the combination." The built code demotes the
   recommendation by one tier instead of blocking it outright; an explicit
   Senior/Lead/Principal *title* still hard-skips (candidate.yaml states that one
   flatly, with no such hedge). In the real run, 7 postings were demoted this way and
   13 were hard-skipped on title — confirming both prior passes had the title-based
   skip right, and only the years-based one wrong.
2. **Cloud platforms now count toward strong-technology overlap.** Neither hand pass's
   mechanical rule ever included `cloud_platforms` in its strong-technology count —
   only the eight bare technology keywords (Python, SQL, Airflow, Git, Linux, Docker,
   Pandas, MySQL). The built `summarize_capability_overlap.py` also credits a
   `STRONG`-level cloud platform (GCP, held at level 3) toward `strong_matches`, since
   there's no principled reason real GCP evidence shouldn't count just because it
   arrived via `cloud_platforms` rather than `technologies`. This is a genuine model
   expansion, not a bug fix like ⇒(1) — flagged here plainly since it wasn't
   explicitly decided in either prior pass and does move real postings.
3. **A previously-undefined case now resolves toward APPLY-adjacent instead of SKIP.**
   Both hand passes' prose rule was silent on "≥2 strong matches but ≥3 blockers";
   both scratch implementations of it happened to fall through to `SKIP`. The built
   code's decision table resolves this case to `LOW_PRIORITY` instead — still not an
   apply-now recommendation, but one tier less severe, and the case is now decided
   deliberately rather than by code-order accident.

**Concrete illustration — Data Platform, the clearest single case:** the
requirement-strength revisit found this family "closed" (4/4 SKIP) but attributed it
correctly to years/title, not tech. The built code now shows **2 SKIP / 2
APPLY_STRETCH**. The two that moved were demoted, not blocked — one had
Airflow/Docker/Git/Python overlap, the other GCP/MySQL/Python/SQL — both real
strong-evidence overlap that a hard years cutoff was previously discarding entirely.
The two that stayed SKIP did so for the right, unchanged reasons: one has zero
technology overlap at all (title `Data Platform Engineer` — every named technology
was `MENTIONED`-only and below strong/partial thresholds), the other is explicitly
titled `Senior Data Platform Engineer` (hard-skipped on title, independent of its
real GCP/Python/SQL overlap).

Full family breakdown from the built code, for reference:

| Family | n | APPLY | STRETCH | LOW | SKIP |
|---|--:|--:|--:|--:|--:|
| Data Engineer | 49 | 11 | 18 | 8 | 12 |
| ETL / Integration | 7 | 2 | 0 | 2 | 3 |
| Data-heavy Backend | 5 | 0 | 2 | 2 | 1 |
| Analytics Engineer | 6 | 1 | 1 | 0 | 4 |
| Data Platform | 4 | 0 | 2 | 0 | 2 |

The Scala/dbt/Databricks leverage ranking from the requirement-strength revisit is
unaffected by any of this — that ranking is about which zero-evidence technology is
worth learning, a question upstream of and independent from the seniority/cloud
changes here. This pass only touches the seniority-fit and overlap-counting rules,
not the requirement-strength data itself.

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

## Third revisit: CI/CD extraction-vocabulary fix (2026-08-21, continued)

Closes the CI/CD gap both earlier passes flagged as un-auditable. Added named CI/CD
tools (GitHub Actions, GitLab CI, CircleCI, Jenkins, Azure DevOps, ArgoCD, Bitbucket
Pipelines, TeamCity, Bamboo) plus generic phrasing ("CI/CD", "continuous
integration/deployment/delivery") to `extract_technologies_mentioned.py`'s keyword
list, all mapped to a single `CI_CD` capability in
`map_technology_to_capability_name.py` — one capability, not one per tool, since
`candidate.yaml` grades CI/CD as one ownership-experience capability regardless of
which tool a posting names. No new logic piece: this is the same technology-mention +
requirement-strength determination every other technology already gets, so extending
the two existing vocabularies was the right fix per `Behavioral Architecture.md`'s
"one rule" (same determination, no caller-selecting flag needed) — not a bespoke
`detect_cicd_requirement.py`.

Re-ran `extract-signals` and `evaluate` over the same stored sample. Recommendation
counts are **unchanged** (14 APPLY / 23 APPLY_STRETCH / 12 LOW_PRIORITY / 22 SKIP) —
expected, since `candidate.yaml`'s `CI_CD` capability is graded `level_0_to_5: 1.5`,
above the zero-evidence threshold (`classify_candidate_capability_strength.py`'s
`_ZERO_LEVEL_THRESHOLD = 1.0`), so it can only ever land as `PARTIAL`, never a
`blocker` — a partial match doesn't move a recommendation the way a blocker does. But
the gap itself is now auditable, which is what was actually missing:

- CI/CD tooling (named or generic) appears at `REQUIRED`/`PREFERRED` strength in the
  raw 1,320-row collected set 361 times; the once-invisible signal is real and common,
  not rare.
- Across the curated 71: **CI/CD lands as a `PARTIAL` capability match in 32 of 71
  postings (45%)**, `STRONG` in 0, and — because `candidate.yaml`'s own level (1.5)
  keeps it above zero — **never a blocker**. This confirms `candidate.yaml`'s own
  framing of CI/CD as an *experience-depth* gap ("has interacted/fiddled with CI/CD
  but has not designed one from scratch") rather than a *capability* gap like dbt
  (0 evidence, frequently a hard blocker) — the market data now backs that
  self-assessment instead of leaving it unverified.
- Net effect on the earlier findings: the CI/CD caveat is resolved, not overturned.
  `current_major_gaps.high_priority`'s "CI/CD ownership" entry in `candidate.yaml` was
  already correctly filed as an *experience* gap, not a capability gap — this pass
  confirms that filing was right, it just couldn't be checked against real postings
  before now.

## Fourth revisit: broader keyword-coverage gap (2026-08-21, continued)

`Objectives.md`'s step-3 note flagged the technology keyword list as a first pass
worth revisiting once step 4/5 showed which coverage gaps actually mattered — now
done, over the same curated 71-posting sample.

**Method:** rather than guessing plausible tool names, checked candidate.yaml-adjacent
and generally common data/BI/warehouse terms against the actual stored descriptions,
snippet by snippet, before adding anything — the same discipline the original
"data"/"analytics" role-family mistake should have used from the start.

**Rejected, not added:** `rust`, `go`, `sap`, `excel`, `nifi` — each looked plausible
going in, but inspection showed they were near-total false-positive traps as bare
substrings on this sample: "rust" matched "trust"/"trusted" (5 of 6 hits), "excel"
matched "excellent"/"excellence" (7 of 7 hits), "nifi" matched "significant" (3 of 3
hits), "sap" matched "ASAP" (1 of 2 hits, the other a false "systemutvecklare... ASAP"
coincidence), "go" matched "go deep" once and Rust/Go the language once. None had
enough genuine signal (0-1 true hits each) to justify what a bare-word marker would
misclassify elsewhere in the sample.

**Added, verified clean:** Power BI, Looker, Tableau, SQL Server/MSSQL, Oracle,
MongoDB, Redis, Fivetran, Matillion, SSIS, Azure Data Factory, Azure Synapse, Delta
Lake, Iceberg, Flink, GraphQL, TypeScript, Lambda, Glue, Grafana — all 100%
true-positive on manual inspection of every match in the curated sample.

**The consequential finding:** two of these — MongoDB and SQL Server — are
capabilities `candidate.yaml` actually grades (`MongoDB` level 2.5, `SQL_Server_TSQL`
level 1.5). Neither had ever been extracted before this fix, meaning real existing
candidate evidence for both was completely absent from every prior fit evaluation in
this document, not merely under-counted the way Scala/Databricks were. Re-running
`extract-signals`/`evaluate`: recommendation counts are unchanged (both capabilities
sit in the same sub-`STRONG` `PARTIAL` band CI_CD occupies, so neither becomes a
blocker or a strong match), but MongoDB now surfaces as a `PARTIAL` match in 1 of 71
curated postings and SQL_Server_TSQL in 8 of 71 — real signal that simply wasn't
visible to this analysis before now.

The remaining additions (Power BI, Looker, Tableau, Oracle, Redis, Fivetran,
Matillion, SSIS, Azure Data Factory/Synapse, Delta Lake, Iceberg, Flink, GraphQL,
TypeScript, Lambda, Glue, Grafana) have no matching `candidate.yaml` capability and
stay unmapped by design, same as the pre-existing Scala/Kafka/Snowflake precedent —
they now populate `job_signals.technologies` for visibility (e.g. a future
"modern BI/warehouse stack" market-shape read, alongside the existing
dbt/Snowflake/Databricks one), but don't move any fit evaluation.
