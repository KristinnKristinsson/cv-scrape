from cv_scrape.logic.extract_same_domain_links import extract_same_domain_links


def test_extracts_same_domain_links_only():
    body = b"""
    <a href="/jobs/1">One</a>
    <a href="/jobs/2">Two</a>
    <a href="https://other-domain.com/jobs/3">Three</a>
    """
    links = extract_same_domain_links("https://example.com/jobs", body, limit=5)
    assert links == ("https://example.com/jobs/1", "https://example.com/jobs/2")


def test_respects_limit():
    body = b'<a href="/a">a</a><a href="/b">b</a><a href="/c">c</a>'
    links = extract_same_domain_links("https://example.com/", body, limit=2)
    assert len(links) == 2


def test_excludes_base_url_and_duplicates():
    body = b'<a href="/">home</a><a href="/x">x</a><a href="/x">x again</a>'
    links = extract_same_domain_links("https://example.com/", body, limit=5)
    assert links == ("https://example.com/x",)
