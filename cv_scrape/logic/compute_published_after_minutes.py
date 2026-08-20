"""Logic: decide how far back (in minutes) to ask the JobSearch API for postings,
given a prior run's watermark and this run's start time. Pure decision over values
already in hand — no fetch, no clock read; both cross in from the flow.
"""

import math
from datetime import datetime

WATERMARK_SAFETY_MARGIN_MINUTES = 30  # covers clock skew / in-run drift; overlap is harmless (convergent upsert)


def compute_published_after_minutes(run_started_at: datetime, last_run_at: str) -> int:
    elapsed_minutes = (run_started_at - datetime.fromisoformat(last_run_at)).total_seconds() / 60
    return max(WATERMARK_SAFETY_MARGIN_MINUTES, math.ceil(elapsed_minutes) + WATERMARK_SAFETY_MARGIN_MINUTES)
