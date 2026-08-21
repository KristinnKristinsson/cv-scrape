"""Interaction: boundary for www.regionstockholm.se's job-detail page. Reads company,
location, description, and posted_at from the page's embedded JobPosting JSON-LD block
(same mechanism as parse_job_posting_json_ld.py), but title has to come from the page's
own `<h1>` instead -- confirmed live across five detail pages spanning three
organizations (Trafikforvaltningen, Danderyds sjukhus, Karolinska
Universitetssjukhuset, MediCarrier AB, Tiohundra AB) that the JSON-LD's `title` field
is not the job title at all: it's always the category label from whichever
`categories` filter was active on the listing page that linked here (e.g.
"Administration, HR, ekonomi, juridik, IT"), while the page's one `<h1>` reliably
holds the real title ("Projektledare till tunnelbanan", "HR-partner till Danderyds
sjukhus", etc.) matching the page's own `<title>` tag. A real site bug, not a probing
artifact -- reproduced on every sampled page regardless of which category filter was
used to reach it.

`jobLocation` here is a bare city-name string (e.g. "Stockholm", "Danderyd", "Norrtälje"),
not the nested Place/PostalAddress object jobbsafari.se's and ledigajobb.se's JSON-LD
use -- read directly rather than digging into a nonexistent `.address` key.

regionstockholm.se-specific, same reasoning as the other sites' JSON-LD pieces: a
second site gets its own piece rather than a shared one parameterized by a flag.
Reuses RejectedJobPosting since "doesn't satisfy JobPosting's shape" is the same
determination regardless of source format or mechanism.
"""

import html
import json
import re

from cv_scrape.interaction.parse_job_posting_html import RejectedJobPosting
from cv_scrape.state.job_posting import JobPosting
from cv_scrape.state.response_envelope import ResponseEnvelope

SOURCE_DOMAIN = "www.regionstockholm.se"

_JSON_LD_BLOCK = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE
)
_TITLE_TAG = re.compile(r"<h1[^>]*>(.*?)</h1>", re.DOTALL | re.IGNORECASE)
_TAG = re.compile(r"<[^>]+>")


def parse_regionstockholm_job_posting_json_ld(envelope: ResponseEnvelope) -> JobPosting:
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

    title_match = _TITLE_TAG.search(body_text)
    description_html = posting.get("description")
    company = (posting.get("hiringOrganization") or {}).get("name")
    if not (title_match and description_html and company):
        raise RejectedJobPosting(f"{envelope.url}: missing title/description/company")

    return JobPosting(
        url=envelope.url,
        source_domain=SOURCE_DOMAIN,
        title=_strip_html(title_match.group(1)),
        company=company,
        description=_strip_html(description_html),
        location=posting.get("jobLocation") or None,
        posted_at=posting.get("datePosted"),
    )


def _is_job_posting(candidate: object) -> bool:
    if not isinstance(candidate, dict):
        return False
    type_ = candidate.get("@type")
    return "JobPosting" in type_ if isinstance(type_, list) else type_ == "JobPosting"


def _strip_html(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub(" ", text))).strip()
