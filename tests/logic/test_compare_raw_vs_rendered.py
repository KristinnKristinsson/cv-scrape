from cv_scrape.logic.compare_raw_vs_rendered import JsRequirement, compare_raw_vs_rendered


def test_missing_either_body_is_inconclusive():
    assert compare_raw_vs_rendered(None, b"<html>content</html>" * 20) is JsRequirement.INCONCLUSIVE
    assert compare_raw_vs_rendered(b"<html>content</html>" * 20, None) is JsRequirement.INCONCLUSIVE


def test_empty_raw_but_populated_rendered_needs_js():
    raw = b"<html><body></body></html>"
    rendered = b"<html><body>" + b"job listing content " * 50 + b"</body></html>"
    assert compare_raw_vs_rendered(raw, rendered) is JsRequirement.JS_REQUIRED


def test_similar_raw_and_rendered_is_static_ok():
    body = b"<html><body>" + b"job listing content " * 50 + b"</body></html>"
    assert compare_raw_vs_rendered(body, body) is JsRequirement.STATIC_OK
