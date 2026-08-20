# cv-scrape structure

This is the applied instance of `Behavioral Architecture.md` for this project — where
prior placement decisions already landed. `Behavioral Architecture.md` remains the
prime directive; this document is the record of how it was applied here. **Consult this
before adding a new file.** If new code doesn't fit an existing row, extend this
document with the same reasoning shape (category + one-line why) rather than guessing.

## What this project is

A personal tool: (1) scrape job postings from various sites with Scrapy, (2) parse the
user's own CV, (3) score/match postings against it, (4) persist results for querying.

Some target sites run WAF/bot challenges. The intent is to defeat them later —
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
│   ├── __main__.py                               # thin CLI dispatcher → flow/* (ingest-cv, match)
│   │
│   ├── state/
│   │   ├── job_posting.py                        # JobPosting entity (doubles as the Scrapy Item shape)
│   │   ├── cv.py                                 # ParsedCv entity
│   │   ├── match_score.py                        # MatchScore entity
│   │   ├── response_envelope.py                  # normalized fetch-outcome shape (status/headers/body/tag)
│   │   ├── site_policy.py                        # per-domain config: selectors, rate-limit policy, header pool
│   │   ├── pending_fetch.py            [WAF]      # reified retry value: url, attempt, not_before, reason
│   │   ├── rate_limiter.py             [WAF]      # RateLimiterState: tokens, last_refill, per domain
│   │   ├── header_rotation.py          [WAF]      # HeaderRotationState: pool + current index
│   │   ├── session.py                  [WAF]      # SessionState: per-domain cookies/last-used headers
│   │   └── store.py                               # SQLite connection factory + schema
│   │
│   ├── interaction/
│   │   ├── receive_fetch_response.py   [WAF]      # raw bytes/headers/status → normalized envelope, or reject
│   │   ├── parse_job_posting_html.py              # validated envelope → JobPosting, or reject-tag
│   │   └── parse_cv_document.py                   # user's CV file (pdf/docx/txt) → ParsedCv, or reject-tag
│   │
│   ├── logic/
│   │   ├── score_match.py                         # ParsedCv + JobPosting in hand → MatchScore
│   │   ├── classify_response.py        [WAF]       # envelope in hand → ok/challenge/blocked/unknown tag
│   │   ├── decide_retry_action.py      [WAF]       # PendingFetch + now → retry-now/wait/abandon tag
│   │   ├── select_rate_limit_policy_for_domain.py [WAF]
│   │   └── select_header_pool_for_domain.py       [WAF]
│   │
│   ├── observation/
│   │   ├── read_clock.py               [WAF]
│   │   ├── read_session_state.py       [WAF]       # read our own stored cookies, unchanged
│   │   ├── read_stored_jobs.py
│   │   ├── read_stored_cv.py
│   │   └── read_pending_fetches.py     [WAF]
│   │
│   ├── effect/
│   │   ├── save_job_posting.py                     # convergent upsert
│   │   ├── save_cv.py                              # convergent upsert
│   │   ├── save_match_score.py                     # convergent upsert
│   │   ├── consume_rate_limit_token.py [WAF]        # ATOMIC check-and-decrement (Atomicity rule)
│   │   ├── rotate_header_selection.py  [WAF]        # ATOMIC get-next-and-advance own index
│   │   ├── update_session_state.py     [WAF]        # store newly-received cookies
│   │   └── enqueue_pending_fetch.py    [WAF]
│   │
│   ├── flow/
│   │   ├── pipelines.py                            # Scrapy item pipeline: interaction → logic → effect
│   │   ├── middlewares.py              [WAF]        # Scrapy downloader middleware, thin sequence over WAF stubs
│   │   ├── retry_pending_fetches.py    [WAF]        # future: drain queue, route on decide_retry_action's tag
│   │   ├── ingest_cv.py                             # CLI flow: file path → interaction → effect
│   │   └── match_jobs_to_cv.py                      # CLI flow: observation×2 → logic → effect
│   │
│   └── spiders/
│       └── example_listing_spider.py                # placeholder site; thin — no decisions/mutations in the callback
│
└── tests/
    └── (mirrors state/interaction/logic/observation/effect/flow — logic tests need no fixtures)
```

## Rationale (why each category)

- **state/** grouped by what each thing *is*. Domain nouns (`job_posting`, `cv`,
  `match_score`) sit alongside the reified WAF values (`pending_fetch`, `rate_limiter`,
  `header_rotation`, `session`, `response_envelope`) — each is "a value first," per the
  spec's reify rule, giving the logic/effect that act on them an obvious home.
  `site_policy.py` is static per-domain config, consumed but not decided by logic.
  `store.py` is the DB shape — infrastructure-as-state, imported by both effect (writes)
  and observation (reads).
- **interaction/** — the three genuinely uncontrolled-input boundaries: external site
  bytes, external site HTML shape, and the user's own CV file. Each validates/rejects
  before anything downstream may trust the value.
- **logic/** — pure decisions over values already in hand: scoring, classifying an
  already-fetched envelope, deciding what a pending retry becomes, picking (not
  advancing) a domain's policy/header pool.
- **observation/** — fetches that change nothing: the clock, our *currently stored*
  (not advanced) cookies, read-only store/queue queries.
- **effect/** — all mutation, including our own crawler-owned state: persistence
  (convergent upserts, safe to repeat), the two atomic get-and-advance operations
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

All `[WAF]`-tagged files are stubs today: docstring + function/class signatures, no
bodies. `flow/middlewares.py` sequences calls into them, but the calls are no-ops —
the spider runs unthrottled now and gains countermeasures later with no restructuring.

## Where the four core features live

- **CV parsing**: `interaction/parse_cv_document.py` → `state/cv.py` →
  `effect/save_cv.py`, sequenced by `flow/ingest_cv.py`.
- **Job-posting parsing**: `interaction/receive_fetch_response.py` →
  `logic/classify_response.py` → `interaction/parse_job_posting_html.py` →
  `state/job_posting.py` → `effect/save_job_posting.py`, sequenced by
  `spiders/example_listing_spider.py` + `flow/pipelines.py`.
- **Matching/scoring**: `logic/score_match.py` (pure), fed by
  `observation/read_stored_jobs.py` + `observation/read_stored_cv.py`, saved by
  `effect/save_match_score.py`, sequenced by `flow/match_jobs_to_cv.py`.
- **Persistence**: SQLite via `state/store.py` + `effect/save_*.py` writers +
  `observation/read_stored_*.py` readers — chosen over JSON Lines for queryability
  (matching needs jobs × scores joins) while staying dependency-light (stdlib
  `sqlite3`). Contained entirely inside `state/store.py` + the read/write modules, so
  swapping later doesn't touch logic/flow.

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

## Tooling defaults

- **Dependency/env management**: `uv` with `pyproject.toml`. Core dep: `scrapy`. CV
  parsing libs (`pdfplumber`, `python-docx`) get added when those stub bodies are
  filled in — not needed for the blueprint itself.
- **Persistence**: SQLite (stdlib `sqlite3`, no extra dependency).
