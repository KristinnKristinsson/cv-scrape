import json

import cv_scrape.effect.save_site_profile as save_site_profile_module
from cv_scrape.effect.save_site_profile import save_site_profile
from cv_scrape.state.framework_signals import FrameworkSignals
from cv_scrape.state.probe_sample import ProbeSample
from cv_scrape.state.rate_limit_findings import RateLimitFindings
from cv_scrape.state.robots_evaluation import RobotsEvaluation
from cv_scrape.state.site_profile import SiteProfile
from cv_scrape.state.structured_data_findings import StructuredDataFindings


def _profile() -> SiteProfile:
    return SiteProfile(
        domain="example.com",
        probed_at="2026-08-20T00:00:00+00:00",
        robots=RobotsEvaluation(fetched=True, allowed=True, crawl_delay=None),
        waf_vendor="NONE",
        framework=FrameworkSignals(generator=None, powered_by=None, server="nginx", matched_markers=()),
        structured_data=StructuredDataFindings(has_json_ld=False),
        js_requirement="STATIC_OK",
        rate_limit=RateLimitFindings(saw_rate_limit=False, retry_after_seconds=None),
        samples=(
            ProbeSample(
                url="https://example.com",
                renderer="raw",
                fetched=True,
                status=200,
                response_tag="OK",
                elapsed_ms=42.0,
                error=None,
            ),
        ),
    )


def test_writes_profile_json_and_snapshots(tmp_path, monkeypatch):
    monkeypatch.setattr(save_site_profile_module, "PROBES_DIR", tmp_path)

    path = save_site_profile(_profile(), raw_bodies=[b"<html>raw</html>"], rendered_bodies=[b"<html>rendered</html>"])

    assert path == tmp_path / "example.com" / "profile.json"
    saved = json.loads(path.read_text())
    assert saved["domain"] == "example.com"
    assert saved["waf_vendor"] == "NONE"

    assert (tmp_path / "example.com" / "raw" / "0.html").read_bytes() == b"<html>raw</html>"
    assert (tmp_path / "example.com" / "rendered" / "0.html").read_bytes() == b"<html>rendered</html>"


def test_rerunning_overwrites_in_place(tmp_path, monkeypatch):
    monkeypatch.setattr(save_site_profile_module, "PROBES_DIR", tmp_path)

    save_site_profile(_profile(), raw_bodies=[b"first"], rendered_bodies=[])
    save_site_profile(_profile(), raw_bodies=[b"second"], rendered_bodies=[])

    assert (tmp_path / "example.com" / "raw" / "0.html").read_bytes() == b"second"
