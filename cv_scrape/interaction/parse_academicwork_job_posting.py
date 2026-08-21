"""Interaction: boundary for www.academicwork.se's job-detail page HTML. Unlike
jobbsafari.se's detail pages (parse_job_posting_json_ld.py), academicwork.se's detail
pages carry no JobPosting JSON-LD at all (confirmed: `structured_data.has_json_ld` is
false in data/probes/www.academicwork.se's probe, and a manual detail-page fetch found
no `application/ld+json` block either) — so extraction goes through the visible
Tailwind markup instead, anchored on structural landmarks that survive Tailwind's
class churn rather than the (long, arbitrary) class names themselves:

- title: the page's one `<h1>`.
- company: the job-card logo `<img>`'s `alt` text — the only `<img>` whose `src` is
  pinned to `awlogo.azureedge.net` regardless of layout. Must be searched for only in
  the markup *before* the `<h1>`, not the whole page: when a listing has no client
  logo uploaded, its own header `<img>` falls back to a generic per-category icon at
  `cdn.academicwork.com/business-areas/*.png` with alt text `"Company logo"` (not an
  `awlogo.azureedge.net` src, so it's correctly skipped) — but the same page's
  "similar jobs" carousel further down still renders *other* postings' real
  `awlogo.azureedge.net` logos. An unbounded search matches one of those unrelated
  companies instead (confirmed live: a confidential "International Bank" posting and
  an unnamed-client posting both picked up a random carousel company this way). Some
  listings (confidential client engagements) never show a real company name or logo
  anywhere on the page at all — those are correctly rejected below, not misattributed.
- location: the "Plats:"/"Location:" meta label's sibling value — the site serves
  both a Swedish and an English page per posting, and the label text (not just the ad
  body copy) switches language with it; other meta labels like "Startdatum"/"Start
  date" sit alongside it in the same shape but aren't part of JobPosting's fields.
- description: everything between the closing `</h1>` and the end of the single
  `<section>` that wraps the whole ad body — verified on two live detail pages that
  exactly one `<section>` opens before the first one closes, and everything `<main>`
  holds after that close is a "similar jobs" section this project doesn't need.

academicwork.se-specific, same reasoning as parse_job_posting_json_ld.py and
parse_academicwork_listing_page.py: a second static-HTML site gets its own piece
rather than a shared one parameterized by a flag. Reuses RejectedJobPosting from
parse_job_posting_html.py since "doesn't satisfy JobPosting's shape" is the same
determination regardless of source format or mechanism.
"""

import html
import re

from cv_scrape.interaction.parse_job_posting_html import RejectedJobPosting
from cv_scrape.state.job_posting import JobPosting
from cv_scrape.state.response_envelope import ResponseEnvelope

SOURCE_DOMAIN = "www.academicwork.se"

_TITLE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.DOTALL | re.IGNORECASE)
_COMPANY = re.compile(r'<img alt="([^"]*)"[^>]*src="https://awlogo\.azureedge\.net', re.IGNORECASE)
_LOCATION = re.compile(r">(?:Plats|Location)<!--\s*-->:</label><p[^>]*>([^<]+)</p>", re.IGNORECASE)
_TAG = re.compile(r"<[^>]+>")


def parse_academicwork_job_posting(envelope: ResponseEnvelope) -> JobPosting:
    body_text = envelope.body.decode("utf-8", errors="ignore")

    title_match = _TITLE.search(body_text)
    if not title_match:
        raise RejectedJobPosting(f"{envelope.url}: missing title markup")

    company_match = _COMPANY.search(body_text[: title_match.start()])
    if not (company_match and company_match.group(1)):
        raise RejectedJobPosting(f"{envelope.url}: missing company markup (no client logo — likely confidential)")

    description = _strip_html(body_text[title_match.end() : _ad_section_end(body_text)])
    if not description:
        raise RejectedJobPosting(f"{envelope.url}: no description content found")

    location_match = _LOCATION.search(body_text)

    return JobPosting(
        url=envelope.url,
        source_domain=SOURCE_DOMAIN,
        title=_strip_html(title_match.group(1)),
        company=html.unescape(company_match.group(1)),
        description=description,
        location=html.unescape(location_match.group(1)).strip() if location_match else None,
    )


def _ad_section_end(body_text: str) -> int:
    main_start = body_text.find("<main>")
    section_close = body_text.find("</section>", main_start if main_start != -1 else 0)
    return section_close if section_close != -1 else len(body_text)


def _strip_html(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub(" ", text))).strip()
