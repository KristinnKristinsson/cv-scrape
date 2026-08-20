"""Logic: find structured data / API / feed hints in an already-fetched envelope's
body. Pure decision over values already in hand — this is the mechanical half of
"check for a real API before profiling scrape difficulty"; confirming a *documented*
public API is a judgment call left to the skill (WebSearch), not something a header
or markup signature can prove.
"""

import re

from cv_scrape.state.response_envelope import ResponseEnvelope
from cv_scrape.state.structured_data_findings import StructuredDataFindings

_JSON_LD_BLOCK = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE
)
_JSON_LD_TYPE = re.compile(r'"@type"\s*:\s*"([^"]+)"')
_FEED_LINK = re.compile(
    r'<link[^>]+type=["\'](?:application/rss\+xml|application/atom\+xml)["\'][^>]+href=["\']([^"\']+)',
    re.IGNORECASE,
)
_SITEMAP_HINT = re.compile(r"sitemap[^\"'\s]*\.xml", re.IGNORECASE)
_API_HINT = re.compile(r'["\'](/[a-zA-Z0-9_\-./]*\bapi\b[a-zA-Z0-9_\-./]*)["\']', re.IGNORECASE)

_MAX_API_HINTS = 20


def discover_structured_data(envelope: ResponseEnvelope) -> StructuredDataFindings:
    body_text = envelope.body.decode("utf-8", errors="ignore")

    json_ld_blocks = _JSON_LD_BLOCK.findall(body_text)
    json_ld_types = tuple(sorted({m for block in json_ld_blocks for m in _JSON_LD_TYPE.findall(block)}))
    feed_links = tuple(sorted(set(_FEED_LINK.findall(body_text))))
    sitemap_hints = tuple(sorted(set(_SITEMAP_HINT.findall(body_text))))
    api_hints = tuple(sorted(set(_API_HINT.findall(body_text))))[:_MAX_API_HINTS]

    return StructuredDataFindings(
        has_json_ld=bool(json_ld_blocks),
        json_ld_types=json_ld_types,
        feed_links=feed_links,
        sitemap_hints=sitemap_hints,
        api_hints=api_hints,
    )
