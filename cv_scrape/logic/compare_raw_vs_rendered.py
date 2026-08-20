"""Logic: decide whether a page needs JS execution to show its real content. Pure
decision over a raw body and a rendered body already in hand — the diff between what
a naive HTTP client sees and what a real browser sees.
"""

from enum import Enum, auto

_MIN_MEANINGFUL_LENGTH = 200
_SIGNIFICANT_GROWTH_RATIO = 1.5


class JsRequirement(Enum):
    STATIC_OK = auto()
    JS_REQUIRED = auto()
    INCONCLUSIVE = auto()


def compare_raw_vs_rendered(raw_body: bytes | None, rendered_body: bytes | None) -> JsRequirement:
    if raw_body is None or rendered_body is None:
        return JsRequirement.INCONCLUSIVE

    raw_len = len(raw_body.decode("utf-8", errors="ignore").strip())
    rendered_len = len(rendered_body.decode("utf-8", errors="ignore").strip())

    if raw_len < _MIN_MEANINGFUL_LENGTH and rendered_len >= _MIN_MEANINGFUL_LENGTH:
        return JsRequirement.JS_REQUIRED
    if rendered_len > raw_len * _SIGNIFICANT_GROWTH_RATIO:
        return JsRequirement.JS_REQUIRED
    return JsRequirement.STATIC_OK
