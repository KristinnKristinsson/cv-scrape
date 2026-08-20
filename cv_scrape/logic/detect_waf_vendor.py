"""Logic: identify a known anti-bot vendor from an already-fetched envelope's
headers/cookies/status/body. Pure decision over values already in hand — known-
signature matching, not raw evidence dumping.
"""

from enum import Enum, auto

from cv_scrape.state.response_envelope import ResponseEnvelope


class WafVendor(Enum):
    CLOUDFLARE = auto()
    AKAMAI = auto()
    DATADOME = auto()
    PERIMETERX = auto()
    IMPERVA = auto()
    NONE = auto()
    UNKNOWN = auto()


def detect_waf_vendor(envelope: ResponseEnvelope) -> WafVendor:
    headers = {k.lower(): v.lower() for k, v in envelope.headers.items()}
    cookie_header = headers.get("set-cookie", "")
    server = headers.get("server", "")
    body_text = envelope.body.decode("utf-8", errors="ignore").lower()

    if "cf-ray" in headers or "cf-mitigated" in headers or "__cf_bm" in cookie_header or "cloudflare" in server:
        return WafVendor.CLOUDFLARE
    if "akamaighost" in server or any(key.startswith("x-akamai") for key in headers):
        return WafVendor.AKAMAI
    if "datadome" in cookie_header or "x-datadome" in headers:
        return WafVendor.DATADOME
    if "_px" in cookie_header or "perimeterx" in body_text:
        return WafVendor.PERIMETERX
    if "incap_ses" in cookie_header or "visid_incap" in cookie_header or "x-iinfo" in headers:
        return WafVendor.IMPERVA

    if envelope.status in (403, 429, 503) or "challenge" in body_text:
        return WafVendor.UNKNOWN
    return WafVendor.NONE
