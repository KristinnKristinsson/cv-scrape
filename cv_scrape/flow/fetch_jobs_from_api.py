"""Flow: CLI-triggered. Sequences observation -> interaction -> logic -> effect
against Arbetsförmedlingen's public JobSearch API, paginating until the API's own
`total` count is exhausted. No decision, no mutation of its own — routes on tags
logic/classify_fetch_status.py, logic/compute_published_after_minutes.py, and
logic/decide_pagination_action.py already returned.

This skips the spider/WAF-handling path entirely: the API is documented, keyless, and
first-party (see data/probes/arbetsformedlingen.se/report.md) — none of the
robots/rate-limit/WAF-countermeasure machinery built for scraped HTML applies to
calling it. Still reuses fetch_page_raw and receive_fetch_response as-is: a plain
idempotent GET and a status/UTF-8 decode guard don't care whether the body ends up
being HTML or JSON, per the "same thing, one piece" rule.

region/occupation_group/employment_type take taxonomy concept codes (the same codes
Platsbanken's own filter UI embeds in its share URL as the opaque-looking `at=`/`p=`
tokens — resolvable via `GET taxonomy.api.jobtechdev.se/v1/taxonomy/main/concepts?id=<code>`)
so a narrow UI selection (e.g. a handful of occupation groups) can be reproduced
exactly, rather than only the free-text `q` this flow started with.

Incremental fetching: each distinct filter combination gets its own watermark
(state/fetch_watermark.py, keyed by _build_query_key below) recording when it last
completed a full run. A later run for the *same* filters asks the API for only
what's published since then (`published-after`, in minutes — chosen over an
absolute timestamp because it's compared against the API's own clock relative to
now, sidestepping any timezone mismatch between our clock and theirs). A run under
different filters gets no watermark and fetches everything, same as the first-ever
run — filters aren't merged or compared, only matched exactly, so widening a
previously-narrower search can't silently miss postings older than some other
search's watermark.
"""

import time
from collections.abc import Sequence
from datetime import datetime, timezone
from urllib.parse import urlencode

from cv_scrape.effect.save_fetch_watermark import save_fetch_watermark
from cv_scrape.effect.save_job_posting import save_job_posting
from cv_scrape.interaction.parse_job_search_api_response import (
    RejectedJobSearchApiResponse,
    parse_job_search_api_response,
)
from cv_scrape.interaction.receive_fetch_response import RejectedResponse, receive_fetch_response
from cv_scrape.logic.classify_fetch_status import FetchStatusOutcome, classify_fetch_status
from cv_scrape.logic.compute_published_after_minutes import compute_published_after_minutes
from cv_scrape.logic.decide_pagination_action import PaginationAction, decide_pagination_action
from cv_scrape.observation.fetch_page_raw import RawFetchResult, fetch_page_raw
from cv_scrape.observation.read_clock import read_clock
from cv_scrape.observation.read_fetch_watermark import read_fetch_watermark

API_SEARCH_URL = "https://jobsearch.api.jobtechdev.se/search"
PAGE_SIZE = 100
MAX_OFFSET = 2000  # API's documented ceiling on the `offset` parameter
DELAY_SECONDS = 0.5


class JobSearchApiFetchFailed(Exception):
    """Raised when a page request fails outright: network error, non-200, or bad body."""


def fetch_jobs_from_api(
    region: str | None = None,
    occupation_group: Sequence[str] = (),
    employment_type: Sequence[str] = (),
    q: str | None = None,
) -> int:
    query_key = _build_query_key(region, occupation_group, employment_type, q)
    watermark = read_fetch_watermark(query_key)

    run_started_at_dt = datetime.fromtimestamp(read_clock(), tz=timezone.utc)
    run_started_at = run_started_at_dt.isoformat()

    published_after_minutes = None
    if watermark is not None:
        published_after_minutes = compute_published_after_minutes(run_started_at_dt, watermark.last_run_at)

    offset = 0
    saved = 0

    while offset <= MAX_OFFSET:
        params: list[tuple[str, str | int]] = [("limit", PAGE_SIZE), ("offset", offset)]
        if region:
            params.append(("region", region))
        if q:
            params.append(("q", q))
        if published_after_minutes is not None:
            params.append(("published-after", published_after_minutes))
        params += [("occupation-group", code) for code in occupation_group]
        params += [("employment-type", code) for code in employment_type]
        url = f"{API_SEARCH_URL}?{urlencode(params)}"

        result = fetch_page_raw(url)
        if not isinstance(result, RawFetchResult):
            raise JobSearchApiFetchFailed(f"{url}: {result.reason}")
        if classify_fetch_status(result.status) is FetchStatusOutcome.FAILED:
            raise JobSearchApiFetchFailed(f"{url}: HTTP {result.status}")

        try:
            envelope = receive_fetch_response(result.url, result.status, result.headers, result.body)
            page = parse_job_search_api_response(envelope)
        except (RejectedResponse, RejectedJobSearchApiResponse) as exc:
            raise JobSearchApiFetchFailed(str(exc)) from exc

        for posting in page.postings:
            save_job_posting(posting, fetched_at=run_started_at)
        saved += len(page.postings)

        offset += PAGE_SIZE
        if decide_pagination_action(offset, page.total, len(page.postings)) is PaginationAction.STOP:
            break

        time.sleep(DELAY_SECONDS)

    save_fetch_watermark(query_key, run_started_at)
    return saved


def _build_query_key(
    region: str | None, occupation_group: Sequence[str], employment_type: Sequence[str], q: str | None
) -> str:
    return "|".join(
        [
            f"region={region or ''}",
            f"occupation-group={','.join(sorted(occupation_group))}",
            f"employment-type={','.join(sorted(employment_type))}",
            f"q={q or ''}",
        ]
    )
