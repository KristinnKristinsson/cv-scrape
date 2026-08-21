"""Logic: build a ProbeSample from a fetch outcome already in hand. One piece,
reused for the raw fetch, the rendered fetch, and each same-domain extra-link
fetch in flow/probe_site.py — the same determination (fetched vs. failed, and
what to carry over) regardless of which of the three call sites it serves.
"""

from cv_scrape.observation.fetch_page_raw import RawFetchFailure, RawFetchResult
from cv_scrape.observation.fetch_page_rendered import RenderedFetchFailure, RenderedFetchResult
from cv_scrape.state.probe_sample import ProbeSample

FetchOutcome = RawFetchResult | RawFetchFailure | RenderedFetchResult | RenderedFetchFailure


def assemble_probe_sample(renderer: str, fetch_result: FetchOutcome, response_tag: str | None) -> ProbeSample:
    if isinstance(fetch_result, (RawFetchResult, RenderedFetchResult)):
        return ProbeSample(
            url=fetch_result.url,
            renderer=renderer,
            fetched=True,
            status=fetch_result.status,
            response_tag=response_tag,
            elapsed_ms=fetch_result.elapsed_ms,
            error=None,
        )

    return ProbeSample(
        url=fetch_result.url,
        renderer=renderer,
        fetched=False,
        status=None,
        response_tag=None,
        elapsed_ms=None,
        error=fetch_result.reason,
    )
