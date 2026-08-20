"""Interaction: boundary for external site HTML. Validates/normalizes/rejects before
JobPosting is trusted downstream.
"""

from cv_scrape.state.job_posting import JobPosting
from cv_scrape.state.response_envelope import ResponseEnvelope
from cv_scrape.state.site_policy import SitePolicy


class RejectedJobPosting(Exception):
    """Raised when a response's fields don't satisfy the site's expected shape."""


def parse_job_posting_html(envelope: ResponseEnvelope, policy: SitePolicy) -> JobPosting:
    raise NotImplementedError
