from datetime import datetime, timezone

from cv_scrape.logic.compute_published_after_minutes import (
    WATERMARK_SAFETY_MARGIN_MINUTES,
    compute_published_after_minutes,
)


def test_elapsed_time_plus_margin_is_rounded_up():
    run_started_at = datetime(2026, 8, 20, 12, 47, 30, tzinfo=timezone.utc)
    last_run_at = "2026-08-20T12:00:00+00:00"

    minutes = compute_published_after_minutes(run_started_at, last_run_at)

    assert minutes == 47 + 1 + WATERMARK_SAFETY_MARGIN_MINUTES


def test_result_never_drops_below_the_safety_margin():
    # last_run_at ahead of run_started_at (clock skew) drives elapsed negative.
    run_started_at = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)
    last_run_at = "2026-08-20T12:05:00+00:00"

    minutes = compute_published_after_minutes(run_started_at, last_run_at)

    assert minutes == WATERMARK_SAFETY_MARGIN_MINUTES
