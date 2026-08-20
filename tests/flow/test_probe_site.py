"""Integration-style: mocks the network (raw fetch, via pytest-httpx) and the browser
(rendered fetch, via monkeypatch) so this runs without real network access or an
installed browser.
"""

import cv_scrape.flow.probe_site as probe_site_module
from cv_scrape.observation.fetch_page_rendered import RenderedFetchResult


def test_probe_site_saves_a_profile(httpx_mock, monkeypatch):
    monkeypatch.setattr(probe_site_module.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(
        probe_site_module,
        "fetch_page_rendered",
        lambda url, timeout=20.0: RenderedFetchResult(
            url=url, status=200, headers={}, body=b"<html><body>jobs here</body></html>", elapsed_ms=5.0
        ),
    )

    httpx_mock.add_response(url="https://example.com/robots.txt", status_code=200, text="User-agent: *\nDisallow:\n")
    httpx_mock.add_response(
        url="https://example.com/jobs",
        status_code=200,
        text='<html><body><a href="/jobs/2">Next</a></body></html>',
    )
    httpx_mock.add_response(url="https://example.com/jobs/2", status_code=200, text="<html>job two</html>")

    saved = []
    monkeypatch.setattr(
        probe_site_module,
        "save_site_profile",
        lambda profile, raw_bodies, rendered_bodies: saved.append((profile, raw_bodies, rendered_bodies)),
    )

    probe_site_module.probe_site("https://example.com/jobs", pages=2)

    assert len(saved) == 1
    profile, raw_bodies, rendered_bodies = saved[0]
    assert profile.domain == "example.com"
    assert profile.robots.allowed is True
    assert len(profile.samples) == 3  # primary raw, primary rendered, one extra link
    assert len(raw_bodies) == 2  # primary + extra link
    assert len(rendered_bodies) == 1


def test_disallowed_robots_txt_stops_sampling(httpx_mock, monkeypatch):
    monkeypatch.setattr(probe_site_module.time, "sleep", lambda seconds: None)

    httpx_mock.add_response(
        url="https://example.com/robots.txt", status_code=200, text="User-agent: *\nDisallow: /jobs\n"
    )

    saved = []
    monkeypatch.setattr(
        probe_site_module,
        "save_site_profile",
        lambda profile, raw_bodies, rendered_bodies: saved.append((profile, raw_bodies, rendered_bodies)),
    )

    probe_site_module.probe_site("https://example.com/jobs", pages=2)

    assert len(saved) == 1
    profile, raw_bodies, rendered_bodies = saved[0]
    assert profile.robots.allowed is False
    assert profile.samples == ()
    assert raw_bodies == []
    assert rendered_bodies == []
