# cv-scrape structure

This is the applied instance of `Behavioral Architecture.md` for this project — where
prior placement decisions already landed. `Behavioral Architecture.md` remains the
prime directive; this document is the record of how it was applied here. **Consult this
before adding a new file.** If new code doesn't fit an existing row, extend this
document with the same reasoning shape (category + one-line why) rather than guessing.

## What this project is

A personal tool: (1) scrape job postings from various sites with Scrapy, (2) extract
inferred signals from each posting (role family, seniority, technologies, ...),
(3) evaluate each against the candidate's own evidence-graded capability profile
(`candidate.yaml`, gitignored — never the codebase's job to hold that data itself),
(4) persist results for querying. See `Objectives.md` for *why* — the market-benchmark
methodology this pipeline exists to serve.

Some target sites run WAF/bot challenges. The intent is to handle them gracefully later —
without external proxies or third-party anti-bot services — but that logic is
**not built yet**. The module boundaries below exist so rate limiting, backoff/retry,
header/UA rotation, response challenge-classification, and cookie/session continuity
can be dropped into pre-placed, correctly-categorized stub files (marked `[WAF]`) with
zero restructuring later.

## Directory tree

```
cv-scrape/
├── Behavioral Architecture.md
├── structure.md                                  # this file
├── scrapy.cfg
├── pyproject.toml                                # deps managed via uv
├── .gitignore
├── data/
│   └── .gitkeep                                  # cv_scrape.db (SQLite) lands here at runtime, gitignored
│
├── cv_scrape/
│   ├── __init__.py
│   ├── settings.py                               # Scrapy-mandated static config (exception, see notes)
│   ├── __main__.py                               # thin CLI dispatcher → flow/* (evaluate, extract-signals, fetch-jobs, probe)
│   │
│   ├── state/
│   │   ├── job_posting.py                        # JobPosting entity (doubles as the Scrapy Item shape)
│   │   ├── candidate_profile.py        [FIT]      # CandidateProfile: capabilities parsed from candidate.yaml
│   │   ├── capability_overlap.py       [FIT]      # CapabilityOverlap: strong/blocker/partial capability names for one posting
│   │   ├── candidate_fit_evaluation.py [FIT]      # CandidateFitEvaluation: the final recommendation + reasons
│   │   ├── response_envelope.py                  # normalized fetch-outcome shape (status/headers/body/tag)
│   │   ├── site_policy.py                        # per-domain config: selectors, rate-limit policy, header pool
│   │   ├── pending_fetch.py            [WAF]      # reified retry value: url, attempt, not_before, reason
│   │   ├── rate_limiter.py             [WAF]      # RateLimiterState: tokens, last_refill, per domain
│   │   ├── header_rotation.py          [WAF]      # HeaderRotationState: pool + current index
│   │   ├── session.py                  [WAF]      # SessionState: per-domain cookies/last-used headers
│   │   ├── site_profile.py             [PROBE]    # SiteProfile: everything one probe run found about a domain
│   │   ├── probe_sample.py             [PROBE]    # reified per-request result within a probe run
│   │   ├── robots_evaluation.py        [PROBE]    # allowed/crawl-delay for a target path
│   │   ├── framework_signals.py        [PROBE]    # generator/powered-by/server/marker hints
│   │   ├── structured_data_findings.py [PROBE]    # JSON-LD/feed/sitemap/API hints
│   │   ├── rate_limit_findings.py      [PROBE]    # 429/Retry-After signal, summarized
│   │   ├── job_signals.py              [SIGNALS]  # role family/seniority/language/etc. inferred from a posting
│   │   └── store.py                               # SQLite connection factory + schema
│   │
│   ├── interaction/
│   │   ├── receive_fetch_response.py   [WAF]      # raw bytes/headers/status → normalized envelope, or reject
│   │   │                                          # first real caller: flow/probe_site.py [PROBE]
│   │   ├── parse_job_posting_html.py              # validated envelope → JobPosting, or reject-tag
│   │   └── parse_candidate_profile.py  [FIT]      # user's candidate.yaml file → CandidateProfile, or reject-tag
│   │
│   ├── logic/
│   │   ├── map_technology_to_capability_name.py [FIT] # tech/cloud keyword in hand → matching capability name, or None
│   │   ├── classify_candidate_capability_strength.py [FIT] # capability name + CandidateProfile in hand → strong/partial/zero tag
│   │   ├── classify_candidate_seniority_fit.py [FIT] # JobPosting + years-required in hand → SeniorityFit tag
│   │   ├── summarize_capability_overlap.py [FIT]  # JobSignals + CandidateProfile in hand → CapabilityOverlap
│   │   ├── evaluate_candidate_against_job.py [FIT] # JobSignals + CapabilityOverlap + SeniorityFit in hand → CandidateFitEvaluation
│   │   ├── classify_response.py        [WAF]       # envelope in hand → ok/challenge/blocked/unknown tag
│   │   │                                           # implemented; first real caller: flow/probe_site.py [PROBE]
│   │   ├── decide_retry_action.py      [WAF]       # PendingFetch + now → retry-now/wait/abandon tag
│   │   ├── select_rate_limit_policy_for_domain.py [WAF]
│   │   ├── select_header_pool_for_domain.py       [WAF]
│   │   ├── detect_waf_vendor.py         [PROBE]    # envelope in hand → known-vendor tag (signature matching)
│   │   ├── detect_framework_signals.py  [PROBE]    # envelope in hand → FrameworkSignals
│   │   ├── discover_structured_data.py  [PROBE]    # envelope body in hand → StructuredDataFindings
│   │   ├── evaluate_robots_txt.py       [PROBE]    # robots.txt text + path in hand → RobotsEvaluation
│   │   ├── compare_raw_vs_rendered.py   [PROBE]    # raw body + rendered body in hand → JS-requirement tag
│   │   ├── extract_same_domain_links.py [PROBE]    # body in hand → a few same-domain URLs for the sample
│   │   ├── detect_rate_limit_signal.py  [PROBE]    # one status+headers in hand → hit/Retry-After
│   │   ├── summarize_rate_limit_signals.py [PROBE] # a probe run's signals in hand → RateLimitFindings
│   │   ├── assemble_probe_sample.py     [PROBE]    # a fetch outcome + tag in hand → ProbeSample; one piece, reused for raw/rendered/extra-link fetches
│   │   ├── classify_role_family.py     [SIGNALS]   # JobPosting in hand → RoleFamily tag
│   │   ├── classify_seniority.py       [SIGNALS]   # JobPosting + years-required in hand → SeniorityTag
│   │   ├── classify_company_type.py    [SIGNALS]   # JobPosting in hand → CompanyType tag
│   │   ├── detect_language_requirement.py [SIGNALS] # JobPosting in hand → LanguageRequirement tag
│   │   ├── detect_education_requirement.py [SIGNALS] # JobPosting in hand → EducationRequirement tag
│   │   ├── extract_technologies_mentioned.py [SIGNALS] # JobPosting in hand → tuple of matched tech keywords
│   │   ├── extract_cloud_platforms_mentioned.py [SIGNALS] # JobPosting in hand → tuple of gcp/aws/azure
│   │   ├── extract_years_experience_required.py [SIGNALS] # JobPosting in hand → years figure, or None
│   │   ├── extract_salary_mentioned.py [SIGNALS]   # JobPosting in hand → raw salary substring, or None
│   │   └── deduplicate_job_postings.py             # list[JobPosting] in hand → same list, repeat vacancies collapsed
│   │
│   ├── observation/
│   │   ├── read_clock.py               [WAF]       # implemented; first real caller: flow/probe_site.py [PROBE]
│   │   ├── read_session_state.py       [WAF]       # read our own stored cookies, unchanged
│   │   ├── read_stored_jobs.py
│   │   ├── read_stored_job_signals.py  [SIGNALS]
│   │   ├── read_stored_candidate_fit_evaluations.py [FIT]
│   │   ├── read_pending_fetches.py     [WAF]
│   │   ├── fetch_page_raw.py            [PROBE]    # plain HTTP GET (httpx); "another system's answer"
│   │   └── fetch_page_rendered.py       [PROBE]    # same URL via a real headless browser (playwright)
│   │
│   ├── effect/
│   │   ├── save_job_posting.py                     # convergent upsert
│   │   ├── save_candidate_fit_evaluation.py [FIT]  # convergent upsert, keyed by job_url
│   │   ├── consume_rate_limit_token.py [WAF]        # ATOMIC check-and-decrement (Atomicity rule)
│   │   ├── rotate_header_selection.py  [WAF]        # ATOMIC get-next-and-advance own index
│   │   ├── update_session_state.py     [WAF]        # store newly-received cookies
│   │   ├── enqueue_pending_fetch.py    [WAF]
│   │   ├── save_site_profile.py         [PROBE]     # per-run write of a SiteProfile + HTML snapshots to disk
│   │   └── save_job_signals.py          [SIGNALS]   # convergent upsert, keyed by job_url
│   │
│   ├── flow/
│   │   ├── pipelines.py                            # Scrapy item pipeline: interaction → logic → effect
│   │   ├── middlewares.py              [WAF]        # Scrapy downloader middleware, thin sequence over WAF stubs
│   │   ├── retry_pending_fetches.py    [WAF]        # future: drain queue, route on decide_retry_action's tag
│   │   ├── probe_site.py                [PROBE]     # CLI flow: `cv_scrape probe <url>` — see below
│   │   ├── extract_job_signals.py       [SIGNALS]   # CLI flow: `cv_scrape extract-signals` — see below
│   │   └── evaluate_candidate_fit.py    [FIT]       # CLI flow: `cv_scrape evaluate` — see below
│   │
│   └── spiders/
│       └── example_listing_spider.py                # placeholder site; thin — no decisions/mutations in the callback
│
├── .claude/skills/probe-site/SKILL.md                # drives `cv_scrape probe`, adds API-discovery (WebSearch)
│                                                       # and selector/SitePolicy synthesis on top — see below
│
└── tests/
    └── (mirrors state/interaction/logic/observation/effect/flow — logic tests need no fixtures)
```

## Rationale (why each category)

- **state/** grouped by what each thing *is*. Domain nouns (`job_posting`,
  `candidate_profile`, `capability_overlap`, `candidate_fit_evaluation`) sit alongside
  the reified WAF values (`pending_fetch`, `rate_limiter`, `header_rotation`,
  `session`, `response_envelope`) — each is "a value first," per the spec's reify
  rule, giving the logic/effect that act on them an obvious home. `site_policy.py` is
  static per-domain config, consumed but not decided by logic. `store.py` is the DB
  shape — infrastructure-as-state, imported by both effect (writes) and observation
  (reads).
- **interaction/** — the three genuinely uncontrolled-input boundaries: external site
  bytes, external site HTML shape, and the user's own `candidate.yaml` file. Each
  validates/rejects before anything downstream may trust the value.
- **logic/** — pure decisions over values already in hand: scoring, classifying an
  already-fetched envelope, deciding what a pending retry becomes, picking (not
  advancing) a domain's policy/header pool.
- **observation/** — fetches that change nothing: the clock, our *currently stored*
  (not advanced) cookies, read-only store/queue queries.
- **effect/** — all mutation, including our own crawler-owned state: persistence
  (convergent upserts, safe to repeat, for scrape/match data — see Ambiguous Call #6
  for why probe output deliberately isn't), the two atomic get-and-advance operations
  (token bucket, rotation index — collapsed into one atomic effect each per the
  Atomicity rule, not split into observation+effect, since that split would open the
  exact stale-check race window the spec warns about), writing new cookies, enqueuing
  retries.
- **flow/** — Scrapy's required hook classes (pipeline, downloader middleware) plus the
  two CLI-triggered scripts, unified because they're the same *behavior* (thin
  sequencing + routing on already-returned tags), regardless of what triggers them.
  None contains a decision or a direct mutation.
- **spiders/** — kept separate only because Scrapy's spider-loader requires a package
  here structurally; the file inside is flow-only, delegating to
  `interaction.parse_job_posting_html` and yielding items for `flow/pipelines.py`.

## WAF-countermeasure stub placement

| Concern | Files | Why there |
|---|---|---|
| Rate limiting | `state/rate_limiter.py`, `logic/select_rate_limit_policy_for_domain.py`, `effect/consume_rate_limit_token.py` | policy lookup is pure logic; check-and-decrement is one atomic effect |
| Backoff / retry | `state/pending_fetch.py`, `logic/decide_retry_action.py`, `effect/enqueue_pending_fetch.py`, `observation/read_pending_fetches.py`, `flow/retry_pending_fetches.py` | textbook reify: pending retry is a value, deciding its fate is logic, performing/queuing is effect, draining is flow |
| UA/header rotation | `state/header_rotation.py`, `logic/select_header_pool_for_domain.py`, `effect/rotate_header_selection.py` | choosing *which pool* is logic; get-next-and-advance is one atomic effect |
| Challenge-page detection | `interaction/receive_fetch_response.py`, `logic/classify_response.py` | normalizing uncontrolled bytes is interaction; tagging the now-trusted envelope is logic |
| Cookie/session continuity | `state/session.py`, `observation/read_session_state.py`, `effect/update_session_state.py` | reading our own jar unchanged is observation; storing new cookies is effect |

All other `[WAF]`-tagged files are stubs today: docstring + function/class
signatures, no bodies. `flow/middlewares.py` sequences calls into them, but the
calls are no-ops — the spider runs unthrottled now and gains countermeasures later
with no restructuring. Two exceptions: `interaction/receive_fetch_response.py` and
`logic/classify_response.py` are implemented for real, because the `[PROBE]`
vertical below needed a real caller for both — the runtime WAF path gets them for
free when `flow/middlewares.py` is filled in.

## Site-probing vertical (pre-crawl investigation) `[PROBE]`

A different behavior from the WAF countermeasures above: one-shot investigation of
an unfamiliar site *before* a spider exists for it, not per-request handling
*inside* a crawl. Triggered by `cv_scrape probe <url>` (see
`.claude/skills/probe-site/SKILL.md` for the conversational skill that drives it and
adds the parts that need judgment rather than a fixed rule — recognizing a
documented public API, proposing selectors from the saved markup).

| Concern | Files | Why there |
|---|---|---|
| Fetching (raw + rendered) | `observation/fetch_page_raw.py`, `observation/fetch_page_rendered.py` | downloading is observation (Ambiguous Call #1) — but unlike the crawl path, Scrapy's engine isn't doing the download here, so the probe needs its own explicit fetch pieces. Raw (httpx) and rendered (playwright) are two different "other systems" to ask, not one function with a caller-selecting flag. |
| Normalizing + classifying | `interaction/receive_fetch_response.py`, `logic/classify_response.py` | same pieces the WAF path will use later — reused, not duplicated, per the one rule's second consequence. Every fetched body in `flow/probe_site.py`, robots.txt included, crosses `receive_fetch_response` before any logic sees it — no fetch gets a separate, unguarded decode path. |
| WAF vendor / framework / structured data | `logic/detect_waf_vendor.py`, `logic/detect_framework_signals.py`, `logic/discover_structured_data.py` | pure decisions over an envelope already in hand; results land in `state/*_signals.py` / `state/*_findings.py`, mirroring how `logic/evaluate_candidate_against_job.py` returns `state/candidate_fit_evaluation.py` |
| robots.txt posture | `logic/evaluate_robots_txt.py` → `state/robots_evaluation.py` | pure decision over already-decoded text; the fetch is another `fetch_page_raw` call and the bytes still cross `receive_fetch_response` first, same as any other fetched body — not a separate piece, not a separate guard |
| JS-requirement | `logic/compare_raw_vs_rendered.py` | pure diff over the raw body and rendered body already in hand |
| Sample expansion | `logic/extract_same_domain_links.py` | pure decision over an already-fetched body, keeps the "small multi-page sample" bounded and same-domain |
| Rate-limit signal | `logic/detect_rate_limit_signal.py` (per request), `logic/summarize_rate_limit_signals.py` (reduced across the run) | keeps `flow/probe_site.py` from inspecting raw status/headers itself to reach a determination |
| Sample assembly | `logic/assemble_probe_sample.py` → `state/probe_sample.py` | fetched-or-failed + tag already in hand → `ProbeSample`; one piece, called for the raw fetch, the rendered fetch, and each same-domain extra-link fetch — same determination regardless of which of the three call sites it serves, per the one rule's second consequence |
| Persistence | `effect/save_site_profile.py` → `data/probes/<domain>/<run_id>/profile.json` + `raw/`, `rendered/` HTML snapshots | investigation output, not scrape results — files, not the SQLite store, so the skill and the user can read it directly. Deliberately not a convergent upsert like the SQLite writers: see Ambiguous Call #6. |
| Sequencing | `flow/probe_site.py` | robots.txt first (stops sampling further if disallowed, still saves what was gathered) → small paced sample, raw + rendered → assemble `state/site_profile.py` → save |

`WafVendor` (in `logic/detect_waf_vendor.py`) and `JsRequirement` (in
`logic/compare_raw_vs_rendered.py`) are bare tags colocated with the logic that
produces them, same placement as `ResponseTag` in `classify_response.py` — richer
records (`FrameworkSignals`, `StructuredDataFindings`, `RobotsEvaluation`,
`RateLimitFindings`) live in `state/` instead, since they're closer to "what it is"
than a single-value tag.

## Job-signal extraction vertical `[SIGNALS]`

Objectives.md step 3: most of the fields that matter for the Stockholm benchmark
(role family, seniority, language/education requirement, company type,
technologies, cloud platforms, years required, salary) aren't stated as labeled
fields anywhere on a scraped page — they're only recoverable by reading a
`JobPosting`'s own title/description text after it's already stored. Triggered by
`cv_scrape extract-signals`, which runs over every stored posting (no per-domain
fetching, no interaction boundary — the text is already-trusted stored state).

Same granularity as the `[PROBE]` vertical (one small logic piece per
determination, same input, different questions) rather than one monolithic
extractor — per the one rule, "role family" and "seniority" are different
determinations even though both read the same `JobPosting`, so they're different
pieces:

| Concern | Files | Why there |
|---|---|---|
| Role family | `logic/classify_role_family.py` → `RoleFamily` | title-keyword match against the seven families Objectives.md drafted; Python/backend titles additionally require a data-handling hint in the description (see note below) |
| Seniority ("looks junior despite title") | `logic/extract_years_experience_required.py` → years figure, then `logic/classify_seniority.py` (that figure + the posting) → `SeniorityTag` | years-required is reused by seniority rather than re-derived, same already-in-hand-determination pattern as `logic/decide_retry_action.py` taking a `PendingFetch` |
| Language / education requirement | `logic/detect_language_requirement.py`, `logic/detect_education_requirement.py` | independent keyword reads over the same description text |
| Company type | `logic/classify_company_type.py` → `CompanyType` | company-name/phrase heuristic (agency vs. direct employer), not a registry lookup |
| Technologies / cloud platforms | `logic/extract_technologies_mentioned.py`, `logic/extract_cloud_platforms_mentioned.py` | kept separate per the one rule — "all tech" and "which cloud" are different questions over the same text, unifying them would need a caller-selecting flag |
| Salary | `logic/extract_salary_mentioned.py` | best-effort raw substring, not structured parsing — most Swedish ads don't state one |
| Persistence | `effect/save_job_signals.py` → `job_signals` SQLite table, `observation/read_stored_job_signals.py` | convergent upsert keyed by `job_url`, same shape as `save_candidate_fit_evaluation.py` |
| Sequencing | `flow/extract_job_signals.py` | reads every stored posting → calls the pieces above → assembles `state/job_signals.py` → saves, mirroring `flow/probe_site.py` assembling `SiteProfile` |

**Known heuristic limitation, found and fixed during the first real run
(2026-08-20):** the data-handling hint list for Python/backend titles originally
included the bare words `"data"` and `"analytics"`. Since almost any job
description mentions "data" somewhere incidentally (player data, GDPR, analytics
events), this matched most backend postings in the sample regardless of actual
relevance — 37 of the 51 `Backend Developer`-titled postings, including several
game studios with no data component at all. Fixed by requiring more specific
compound markers (`"data pipeline"`, `"data warehouse"`, `"etl"`, `"dbt"`,
`"databricks"`, etc.) instead of the bare words — dropped the false-positive count
to 6, all genuinely data-adjacent on inspection. Documented here as a warning for
any future hint list in this vertical: a single common word as a boundary
condition is not a heuristic, it's a coin flip.

**`logic/deduplicate_job_postings.py`** is a sibling piece, not part of this
vertical — it doesn't infer anything from a posting's text, it decides which of
several stored `JobPosting`s are the same real vacancy seen twice (cross-posted
across `arbetsformedlingen.se`/`jobbsafari.se`, or resubmitted twice on
Platsbanken under different ad IDs — neither catchable by the store's own `url`
primary key). Reified per the same "value first, wire in later" sequencing
`classify_role_family.py` followed in step 3; its first real caller is
`flow/evaluate_candidate_fit.py`, part of the `[FIT]` vertical below.

## Candidate-fit evaluation vertical `[FIT]`

`Objectives.md` steps 5–7: place the candidate's own evidence-graded capability
profile (`candidate.yaml`, read fresh from disk each run — gitignored, never
persisted, changes as the user's self-assessment evolves) against each curated
posting's `JobSignals`, and produce one of four recommendations
(`APPLY`/`APPLY_STRETCH`/`LOW_PRIORITY`/`SKIP`). Formalizes the mechanical rule
`candidate.yaml`'s own `job_evaluation_guidance` section already describes in
prose — hand-run twice as one-off scratch analyses (`Candidate Placement
Findings.md`) before being built here. Triggered by `cv_scrape evaluate`.

| Concern | Files | Why there |
|---|---|---|
| Reading candidate.yaml | `interaction/parse_candidate_profile.py` → `state/candidate_profile.py` | same uncontrolled-file-boundary category as the CV-parsing boundary this replaces; only `capability_model.capabilities` is extracted — nothing else in the file (target constraints, salary floor, work authorization, self-assessed gaps) is read by code |
| Technology name → capability name | `logic/map_technology_to_capability_name.py` | a static fact about the two vocabularies (job-posting keywords vs. candidate.yaml capability names), independent of the candidate's actual evidence levels, so it's its own piece rather than folded into the strength check below |
| Capability strength | `logic/classify_candidate_capability_strength.py` → `CapabilityStrengthTag` (`STRONG`/`PARTIAL`/`ZERO`) | thresholds validated by hand across both prior scratch passes (level ≥3 → strong, evidence_class `[]` or level ≤1 → zero) |
| Seniority fit | `logic/classify_candidate_seniority_fit.py` → `SeniorityFit` | a different, coarser bar than `classify_seniority.py`'s `SeniorityTag` (tuned for market-wide tiering, not personal disqualification) — and unlike it, tells apart an explicit Senior/Lead/Principal *title* (flat skip signal per candidate.yaml) from a stated *years* bar (candidate.yaml explicitly says not to auto-reject on years alone) |
| Overlap summary | `logic/summarize_capability_overlap.py` → `CapabilityOverlap` | reduces a posting's technologies + cloud platforms into strong/blocker/partial capability names; dedups by resolved capability name (fixes the postgres/postgresql double-count `Candidate Placement Findings.md` flagged) and only counts a zero-evidence technology as a blocker at `REQUIRED`/`PREFERRED` strength, not bare `MENTIONED` |
| Final recommendation | `logic/evaluate_candidate_against_job.py` → `Recommendation`, assembled into `state/candidate_fit_evaluation.py` | combines the overlap counts with `SeniorityFit`: a senior title hard-skips, a high years bar demotes the base result by one tier instead of blocking it outright — the confirmed fix for a hard `years≥5` cutoff both prior scratch passes used, which contradicted candidate.yaml's own written guidance |
| Persistence | `effect/save_candidate_fit_evaluation.py` → `candidate_fit_evaluation` SQLite table, `observation/read_stored_candidate_fit_evaluations.py` | convergent upsert keyed by `job_url`, same shape as `save_job_signals.py` |
| Sequencing | `flow/evaluate_candidate_fit.py` | scopes to `role_family != "UNMATCHED"`, deduplicated via `logic/deduplicate_job_postings.py` (its first real flow caller) → calls the pieces above → saves, mirroring `flow/extract_job_signals.py` |

This replaced a pre-`candidate.yaml` generic CV-ingestion/single-scalar-match
vertical (`ParsedCv`, `logic/score_match.py`, `MatchScore`) that never ran past
`NotImplementedError` stubs — deleted outright rather than left alongside the real
thing, per this repo's own no-dead-code convention.

## Where the core features live

- **Job-posting parsing**: `interaction/receive_fetch_response.py` →
  `logic/classify_response.py` → `interaction/parse_job_posting_html.py` →
  `state/job_posting.py` → `effect/save_job_posting.py`, sequenced by
  `spiders/example_listing_spider.py` + `flow/pipelines.py`.
- **Candidate-fit evaluation**: see the dedicated section above —
  `interaction/parse_candidate_profile.py` → the `classify_*`/`summarize_*`/
  `evaluate_*` `[FIT]` logic → `state/candidate_fit_evaluation.py` →
  `effect/save_candidate_fit_evaluation.py`, sequenced by
  `flow/evaluate_candidate_fit.py`.
- **Persistence**: SQLite via `state/store.py` + `effect/save_*.py` writers +
  `observation/read_stored_*.py` readers — chosen over JSON Lines for queryability
  (matching needs jobs × scores joins) while staying dependency-light (stdlib
  `sqlite3`). Contained entirely inside `state/store.py` + the read/write modules, so
  swapping later doesn't touch logic/flow.
- **Site probing**: see the dedicated section above — `observation/fetch_page_raw.py`
  + `fetch_page_rendered.py` → `interaction/receive_fetch_response.py` →
  `logic/classify_response.py` + the WAF-vendor/framework/structured-data/
  robots/JS-requirement/rate-limit logic → `state/site_profile.py` →
  `effect/save_site_profile.py`, sequenced by `flow/probe_site.py`.
- **Job-signal extraction**: see the dedicated section above —
  `observation/read_stored_jobs.py` → the `classify_*`/`detect_*`/`extract_*`
  `[SIGNALS]` logic → `state/job_signals.py` → `effect/save_job_signals.py`,
  sequenced by `flow/extract_job_signals.py`.
- **Job fetching via a public API** (Arbetsförmedlingen/Platsbanken): probing this
  domain (`data/probes/arbetsformedlingen.se/report.md`) found a free, keyless,
  first-party JSON API and a JS-required, structured-data-free HTML page — so this
  domain is fetched via the API, never scraped. Reuses `observation/fetch_page_raw.py`
  and `interaction/receive_fetch_response.py` unchanged (a GET and a decode guard
  don't care whether the body is HTML or JSON), adds
  `interaction/parse_job_search_api_response.py` (JSON-shape guard + per-ad field
  extraction into `state/job_posting.py`, reusing `RejectedJobPosting` from
  `parse_job_posting_html.py` since "doesn't satisfy JobPosting's shape" is the same
  determination regardless of source format) and `state/job_search_api_page.py`
  (postings + the API's own `total`, so flow knows when to stop paginating without
  re-decoding the body) → `effect/save_job_posting.py`, sequenced by
  `flow/fetch_jobs_from_api.py`. No spider, no `SitePolicy`, none of the
  WAF-countermeasure or probe machinery — a documented first-party API is not an
  uncontrolled adversarial boundary the way scraped HTML is. Three decisions the flow
  would otherwise make inline are pulled out as logic pieces, same as
  `probe_site.py`'s: `logic/classify_fetch_status.py` (status code in → `OK`/`FAILED`
  out, so the flow never branches on `result.status` itself),
  `logic/compute_published_after_minutes.py` (elapsed time since the query's
  watermark, plus a clock-skew safety margin, already-in-hand values in → a
  determination out), and `logic/decide_pagination_action.py` (offset vs. the API's
  `total`, and whether the page came back empty, → `CONTINUE`/`STOP`); the flow only
  routes on the tags. Incremental re-fetching adds one more state/observation/effect
  trio, same reify shape as the WAF stubs: `state/fetch_watermark.py`
  (`FetchWatermark`: the query's own filter signature + when it last completed a
  full run — mirrors `state/session.py`'s per-domain shape, one level more
  specific), `observation/read_fetch_watermark.py` (read our own stored watermark
  unchanged, mirrors `read_session_state.py`), and `effect/save_fetch_watermark.py`
  (convergent upsert, same shape as `save_job_posting.py`). `flow/fetch_jobs_from_api.py`
  reads the watermark before paginating, feeds it into
  `compute_published_after_minutes.py`, and saves a fresh one only after the run
  completes — a decision no single piece owns, visible only by reading the flow (see
  Flow — the altitude, and its body).
- **Job scraping: jobbsafari.se**: probing this domain
  (`data/probes/jobbsafari.se/report.md`) found no API (the site's own internal API is
  robots-disallowed), `STATIC_OK` HTML, and — critically — a complete `JobPosting`
  JSON-LD block on every job-detail page, richer and more stable than the listing
  card's MUI/emotion markup (class names that churn across deploys). So this domain is
  scraped in two stages instead of the single CSS-selector pass
  `parse_job_posting_html.py`/`SitePolicy` were built for: `spiders/
  jobbsafari_listing_spider.py` walks listing pages via `interaction/
  parse_job_listing_page.py` (detail-page + `rel="next"` links only — no per-field
  extraction, since the churny listing markup has nothing this project needs that the
  detail page doesn't have more reliably), then fetches each detail page and extracts
  the full `JobPosting` via `interaction/parse_job_posting_json_ld.py` (JSON-LD key
  access, reusing `RejectedJobPosting` from `parse_job_posting_html.py` — same "doesn't
  satisfy JobPosting's shape" determination regardless of mechanism, same reasoning as
  `parse_job_search_api_response.py`). `state/job_listing_page.py` reifies a listing
  page's already-parsed links, mirroring `state/job_search_api_page.py`'s shape. Both
  spider callbacks route on `logic/classify_response.py`'s tag before trusting a body
  as real markup, since Cloudflare fronts this site even though it wasn't seen actively
  challenging during probing. No `SitePolicy` is used — see the two interaction
  pieces' docstrings for why a CSS-selector-shaped config doesn't fit a site whose real
  extraction mechanism is JSON-LD key access. `start_urls` walks two Stockholm
  listings independently — the original `yrke/utvecklare` (role-title) filter plus
  `kategori/data-och-it` (the site's own broader category), added per `Objectives.md`'s
  jobbsafari-taxonomy-coverage check, which found real postings (e.g. "Data Engineer
  till SPP") that never appeared under `utvecklare` alone. Same "loose recall, filtered
  downstream" treatment as Platsbanken's `q` — no new logic needed since
  `logic/classify_role_family.py` and `logic/deduplicate_job_postings.py` already do
  that filtering and cross-listing dedup.

## Ambiguous placement calls (for the record)

1. **Downloading a page**: observation, not effect — the spec's own examples list
   "another system's answer" (an HTTP response) as observation, and our fetches are
   plain idempotent GETs. Caveat: a future POST-based challenge-solve would be an
   effect crossing the uncontrolled boundary (landed/refused/unknown tagging applies
   there, not to today's reads).
2. **HTML/CV extraction**: interaction, per the spec's explicit examples — split into
   `receive_fetch_response.py` (generic malformed/undecodable-bytes guard, same piece
   for challenge pages and real pages — one piece per the "same thing" rule) and
   `parse_job_posting_html.py` (further per-field validation, since site-layout drift
   is still uncontrolled even after bytes decode cleanly).
3. **Spider callback**: must stay flow-only — it delegates to
   `interaction.parse_job_posting_html` and yields/routes, never picks fields out of
   the response itself, or it silently becomes a second, badly-placed interaction
   piece.
4. **Rotation/rate-limit read-then-advance**: collapsed into one atomic effect, not
   observation+effect — splitting them opens the stale-check race window the spec's
   Atomicity section warns about, and matches the spec's literal example ("rotating
   your own proxy-index counter... is an EFFECT").
5. **`store.py` / `settings.py`**: treated as exceptions to the six categories — neither
   is a decision/fetch/mutation on its own; `store.py` is declarative "what the store
   is" (state), `settings.py`/`scrapy.cfg` is Scrapy-mandated static wiring.
6. **Probe run directories, not an upsert**: `effect/save_site_profile.py` writes
   each run under `data/probes/<domain>/<run_id>/` — `run_id` is `profile.probed_at`
   (from `observation/read_clock.py`, already unique per run), sanitized for use as
   a path segment — rather than overwriting one shared `<domain>/` directory in
   place. A shared, overwritten directory would let a smaller run (fewer samples,
   e.g. because robots.txt started disallowing) leave a *previous* run's snapshots
   on disk uncorrelated with the new `profile.json` — a stale mix presented as one
   run's evidence. Per-run directories side-step that: nothing is ever partially
   overwritten, so there's no requirement to converge (compare Ambiguous Call #4,
   where convergence *is* required — that's a repeatable check-and-change on shared
   crawler state, not one-off investigation output). Within a run, snapshots are
   still named by index within `profile.json`'s `samples` list, filtered by renderer
   (`raw/0.html`, `raw/1.html`, ...) rather than derived from the URL — that
   filename detail is unchanged, still a persistence-mechanics detail rather than a
   domain decision, so it stays in the effect rather than earning its own logic
   piece.
7. **Probe's own footprint**: `flow/probe_site.py` paces requests with
   `robots.crawl_delay or DEFAULT_DELAY_SECONDS` inline rather than through a logic
   piece — it's a policy default, not a determination reached by inspecting fetched
   content, so it doesn't cross the "flow may not decide" line the way branching on
   raw status/headers would.

## Tooling defaults

- **Dependency/env management**: `uv` with `pyproject.toml`. Core deps: `scrapy`,
  `httpx` (raw probe fetches), `playwright` (rendered probe fetches — after `uv
  sync`, browser binaries still need `uv run playwright install chromium`, a
  several-hundred-MB download, run manually rather than automatically). No CV
  parsing libs — the pre-`candidate.yaml` CV-ingestion vertical that would have
  needed them (`pdfplumber`, `python-docx`) was deleted outright, per the
  `[FIT]` vertical section above.
- **Persistence**: SQLite (stdlib `sqlite3`, no extra dependency) for scrape/match
  data; plain files under `data/probes/` for probe investigation output (see
  site-probing vertical above) — different data, different lifetime, not the same
  store.
