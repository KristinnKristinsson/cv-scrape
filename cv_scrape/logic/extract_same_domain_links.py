"""Logic: pick a handful of same-domain links out of an already-fetched body, for the
probe's small multi-page sample. Pure decision over values already in hand.
"""

import re
from urllib.parse import urljoin, urlparse

_HREF_PATTERN = re.compile(r'href=["\']([^"\'#]+)["\']', re.IGNORECASE)


def extract_same_domain_links(base_url: str, body: bytes, limit: int) -> tuple[str, ...]:
    domain = urlparse(base_url).netloc
    body_text = body.decode("utf-8", errors="ignore")

    found: list[str] = []
    for href in _HREF_PATTERN.findall(body_text):
        resolved = urljoin(base_url, href)
        parsed = urlparse(resolved)
        if parsed.scheme not in ("http", "https") or parsed.netloc != domain:
            continue
        if resolved == base_url or resolved in found:
            continue
        found.append(resolved)
        if len(found) >= limit:
            break

    return tuple(found)
