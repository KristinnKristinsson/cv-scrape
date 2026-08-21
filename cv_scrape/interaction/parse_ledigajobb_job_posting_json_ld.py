"""Interaction: boundary for ledigajobb.se's job-detail page's embedded JobPosting
JSON-LD block. Same mechanism and shape as parse_job_posting_json_ld.py (jobbsafari.se)
-- title/description/hiringOrganization.name/jobLocation.address/datePosted -- confirmed
live on two detail pages (data/probes/ledigajobb.se's report flagged this as unverified
since no detail page was sampled during probing; both live pages checked here
(sap-logistics-consultant, mekaniker) carried exactly one schema.org JobPosting block
with every field populated).

A separate piece rather than reusing jobbsafari's, per this project's convention (see
parse_job_listing_page.py's docstring): a second site gets its own piece, not a shared
one parameterized by a flag -- even when, as here, the two sites' JSON-LD happens to
line up field-for-field. Reuses RejectedJobPosting since "doesn't satisfy JobPosting's
shape" is the same determination regardless of source format or mechanism.
"""

import html
import json
import re

from cv_scrape.interaction.parse_job_posting_html import RejectedJobPosting
from cv_scrape.state.job_posting import JobPosting
from cv_scrape.state.response_envelope import ResponseEnvelope

SOURCE_DOMAIN = "ledigajobb.se"

_JSON_LD_BLOCK = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE
)
_TAG = re.compile(r"<[^>]+>")


def parse_ledigajobb_job_posting_json_ld(envelope: ResponseEnvelope) -> JobPosting:
    body_text = envelope.body.decode("utf-8", errors="ignore")

    posting = None
    for block in _JSON_LD_BLOCK.findall(body_text):
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError:
            continue
        for candidate in parsed if isinstance(parsed, list) else [parsed]:
            if _is_job_posting(candidate):
                posting = candidate
                break
        if posting is not None:
            break

    if posting is None:
        raise RejectedJobPosting(f"{envelope.url}: no JobPosting JSON-LD block found")

    title = posting.get("title")
    description_html = posting.get("description")
    company = (posting.get("hiringOrganization") or {}).get("name")
    if not (title and description_html and company):
        raise RejectedJobPosting(f"{envelope.url}: JobPosting JSON-LD missing required field(s)")

    address = (posting.get("jobLocation") or {}).get("address") or {}
    location = address.get("addressLocality") or address.get("addressRegion")

    return JobPosting(
        url=envelope.url,
        source_domain=SOURCE_DOMAIN,
        title=title,
        company=company,
        description=_strip_html(description_html),
        location=location,
        posted_at=posting.get("datePosted"),
    )


def _is_job_posting(candidate: object) -> bool:
    if not isinstance(candidate, dict):
        return False
    type_ = candidate.get("@type")
    return "JobPosting" in type_ if isinstance(type_, list) else type_ == "JobPosting"


def _strip_html(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub(" ", text))).strip()
