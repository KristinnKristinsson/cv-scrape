"""Logic: read framework/CMS hints off an already-fetched envelope. Pure decision
over values already in hand.
"""

import re

from cv_scrape.state.framework_signals import FrameworkSignals
from cv_scrape.state.response_envelope import ResponseEnvelope

_GENERATOR_PATTERN = re.compile(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)', re.IGNORECASE)

_MARKER_PATTERNS = {
    "wordpress": ("wp-content", "wp-includes"),
    "next.js": ("_next/static", "__next_data__"),
    "react": ("data-reactroot", "react-dom"),
    "shopify": ("cdn.shopify.com", "shopify.theme"),
    "drupal": ("drupal.settings", "/sites/default/files"),
}


def detect_framework_signals(envelope: ResponseEnvelope) -> FrameworkSignals:
    headers = {k.lower(): v for k, v in envelope.headers.items()}
    body_text = envelope.body.decode("utf-8", errors="ignore")
    lowered_body_text = body_text.lower()

    generator_match = _GENERATOR_PATTERN.search(body_text)
    matched_markers = tuple(
        name for name, markers in _MARKER_PATTERNS.items() if any(m in lowered_body_text for m in markers)
    )

    return FrameworkSignals(
        generator=generator_match.group(1) if generator_match else None,
        powered_by=headers.get("x-powered-by"),
        server=headers.get("server"),
        matched_markers=matched_markers,
    )
