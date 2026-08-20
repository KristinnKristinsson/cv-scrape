"""Logic: which cloud platforms are named in a posting's text. Split from
extract_technologies_mentioned.py rather than folded into it — "which cloud is
this" is a narrower, differently-purposed question (scoring the user's GCP
evidence specifically) than "what's the full tech list," even though both scan
the same text; per Behavioral Architecture.md's "same thing" test, unifying them
would need a caller-selecting flag, so they stay separate pieces.
"""

from cv_scrape.state.job_posting import JobPosting

_CLOUD_PLATFORM_MARKERS = {
    "gcp": ("gcp", "google cloud"),
    "aws": ("aws", "amazon web services"),
    "azure": ("azure",),
}


def extract_cloud_platforms_mentioned(job: JobPosting) -> tuple[str, ...]:
    text = f"{job.title}\n{job.description}".lower()
    return tuple(platform for platform, markers in _CLOUD_PLATFORM_MARKERS.items() if any(m in text for m in markers))
