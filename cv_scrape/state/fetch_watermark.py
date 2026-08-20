"""State: the last time a given job-search query successfully completed a full
fetch run, keyed by the query's own filter signature (not by domain — two
differently-filtered runs against the same API must not clobber each other's
watermark, or one could silently blind the other to postings only it would match).
Mirrors state/session.py's per-domain shape, one level more specific.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FetchWatermark:
    query_key: str
    last_run_at: str
