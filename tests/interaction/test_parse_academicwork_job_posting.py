import pytest

from cv_scrape.interaction.parse_academicwork_job_posting import parse_academicwork_job_posting
from cv_scrape.interaction.parse_job_posting_html import RejectedJobPosting
from cv_scrape.state.response_envelope import ResponseEnvelope

_DETAIL_URL = "https://www.academicwork.se/lediga-jobb/j/data-engineer-till-exempel/AB12CD"

_TITLE_TAG = b'<h1 class="font-serif">Data Engineer till Exempel</h1>'
_LOCATION_BLOCK = b"<div><label>Plats<!-- -->:</label><p>Stockholm</p></div>"

_VALID_BODY = (
    b'<html><body><main><div><div>'
    b'<section class="ad-body">'
    b'<div><img alt="Exempel AB" loading="lazy" src="https://awlogo.azureedge.net/logos/x.jpg"/>'
    + _TITLE_TAG
    + b"</div>"
    + _LOCATION_BLOCK
    + b'<div class="grid gap-3"><h2>Om tj&auml;nsten</h2>'
    b"<p>Vi s&ouml;ker en <strong>Data Engineer</strong> till v&aring;rt team.</p></div>"
    b"</section>"
    b'<section class="similar-jobs"><h3>9 liknande jobb</h3><p>Noise that must not leak in.</p></section>'
    b"</div></div></main></body></html>"
)


def _envelope(body: bytes) -> ResponseEnvelope:
    return ResponseEnvelope(url=_DETAIL_URL, status=200, headers={}, body=body)


def test_valid_job_posting_html_is_parsed():
    posting = parse_academicwork_job_posting(_envelope(_VALID_BODY))
    assert posting.url == _DETAIL_URL
    assert posting.source_domain == "www.academicwork.se"
    assert posting.title == "Data Engineer till Exempel"
    assert posting.company == "Exempel AB"
    assert posting.location == "Stockholm"


def test_description_is_stripped_unescaped_and_excludes_similar_jobs():
    posting = parse_academicwork_job_posting(_envelope(_VALID_BODY))
    assert posting.description == "Plats : Stockholm Om tjänsten Vi söker en Data Engineer till vårt team."
    assert "Noise that must not leak in" not in posting.description


def test_missing_title_is_rejected():
    body = _VALID_BODY.replace(_TITLE_TAG, b"")
    with pytest.raises(RejectedJobPosting):
        parse_academicwork_job_posting(_envelope(body))


def test_missing_company_logo_is_rejected():
    body = _VALID_BODY.replace(b'src="https://awlogo.azureedge.net/logos/x.jpg"', b'src="https://example.com/other.jpg"')
    with pytest.raises(RejectedJobPosting):
        parse_academicwork_job_posting(_envelope(body))


def test_missing_location_gives_none():
    body = _VALID_BODY.replace(_LOCATION_BLOCK, b"")
    posting = parse_academicwork_job_posting(_envelope(body))
    assert posting.location is None


def test_location_label_in_english_is_also_matched():
    body = _VALID_BODY.replace(b"<label>Plats<!-- -->:</label>", b"<label>Location<!-- -->:</label>")
    posting = parse_academicwork_job_posting(_envelope(body))
    assert posting.location == "Stockholm"


def test_similar_jobs_carousel_logo_after_the_h1_is_not_mistaken_for_the_company():
    # No client logo uploaded for this posting (generic per-category fallback icon
    # before the h1, like a real confidential/no-logo listing) — the only real
    # awlogo.azureedge.net logo on the page belongs to an unrelated "similar jobs"
    # entry after the ad section. Must be rejected, not misattributed.
    body = _VALID_BODY.replace(
        b'<img alt="Exempel AB" loading="lazy" src="https://awlogo.azureedge.net/logos/x.jpg"/>',
        b'<img alt="Company logo" loading="lazy" src="https://cdn.academicwork.com/business-areas/x.png"/>',
    ).replace(
        b"Noise that must not leak in.",
        b'Noise. <img alt="Unrelated AB" src="https://awlogo.azureedge.net/logos/other.jpg"/>',
    )
    with pytest.raises(RejectedJobPosting):
        parse_academicwork_job_posting(_envelope(body))
