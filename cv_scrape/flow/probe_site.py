"""Flow: CLI-triggered. Sequences observation -> interaction -> logic -> effect for
one site: robots.txt posture first (stops sampling further if disallowed, but still
saves what was gathered), then a small multi-page sample fetched both raw and
rendered. No decision, no mutation of its own — routes on tags the logic pieces
already returned (fetch succeeded/failed, response accepted/rejected, allowed/not).
"""

import time
from datetime import datetime, timezone
from urllib.parse import urlparse

from cv_scrape.effect.save_site_profile import save_site_profile
from cv_scrape.interaction.receive_fetch_response import RejectedResponse, receive_fetch_response
from cv_scrape.logic.classify_response import classify_response
from cv_scrape.logic.compare_raw_vs_rendered import JsRequirement, compare_raw_vs_rendered
from cv_scrape.logic.detect_framework_signals import detect_framework_signals
from cv_scrape.logic.detect_rate_limit_signal import RateLimitSignal, detect_rate_limit_signal
from cv_scrape.logic.detect_waf_vendor import WafVendor, detect_waf_vendor
from cv_scrape.logic.discover_structured_data import discover_structured_data
from cv_scrape.logic.evaluate_robots_txt import evaluate_robots_txt
from cv_scrape.logic.extract_same_domain_links import extract_same_domain_links
from cv_scrape.logic.summarize_rate_limit_signals import summarize_rate_limit_signals
from cv_scrape.observation.fetch_page_raw import PROBE_USER_AGENT, RawFetchResult, fetch_page_raw
from cv_scrape.observation.fetch_page_rendered import RenderedFetchResult, fetch_page_rendered
from cv_scrape.observation.read_clock import read_clock
from cv_scrape.state.framework_signals import FrameworkSignals
from cv_scrape.state.probe_sample import ProbeSample
from cv_scrape.state.site_profile import SiteProfile
from cv_scrape.state.structured_data_findings import StructuredDataFindings

DEFAULT_SAMPLE_PAGES = 3
DEFAULT_DELAY_SECONDS = 1.5


def probe_site(target_url: str, pages: int = DEFAULT_SAMPLE_PAGES) -> None:
    parsed_target = urlparse(target_url)
    domain = parsed_target.netloc
    target_path = parsed_target.path or "/"

    samples: list[ProbeSample] = []
    raw_bodies: list[bytes] = []
    rendered_bodies: list[bytes] = []
    rate_limit_signals: list[RateLimitSignal] = []

    robots_result = fetch_page_raw(f"{parsed_target.scheme}://{domain}/robots.txt")
    robots_txt = robots_result.body.decode("utf-8", errors="ignore") if isinstance(robots_result, RawFetchResult) else None
    robots = evaluate_robots_txt(robots_txt, target_path, PROBE_USER_AGENT)

    waf_vendor = WafVendor.UNKNOWN.name
    framework = FrameworkSignals(generator=None, powered_by=None, server=None, matched_markers=())
    structured_data = StructuredDataFindings(has_json_ld=False)
    js_requirement = JsRequirement.INCONCLUSIVE.name

    if robots.allowed:
        delay = robots.crawl_delay or DEFAULT_DELAY_SECONDS

        raw_result = fetch_page_raw(target_url)
        raw_accepted_body: bytes | None = None
        if isinstance(raw_result, RawFetchResult):
            raw_bodies.append(raw_result.body)
            rate_limit_signals.append(detect_rate_limit_signal(raw_result.status, raw_result.headers))

            tag_name = None
            try:
                envelope = receive_fetch_response(raw_result.url, raw_result.status, raw_result.headers, raw_result.body)
                tag_name = classify_response(envelope).name
                waf_vendor = detect_waf_vendor(envelope).name
                framework = detect_framework_signals(envelope)
                structured_data = discover_structured_data(envelope)
                raw_accepted_body = envelope.body
            except RejectedResponse:
                pass

            samples.append(
                ProbeSample(
                    url=raw_result.url,
                    renderer="raw",
                    fetched=True,
                    status=raw_result.status,
                    response_tag=tag_name,
                    elapsed_ms=raw_result.elapsed_ms,
                    error=None,
                )
            )
        else:
            samples.append(
                ProbeSample(
                    url=target_url,
                    renderer="raw",
                    fetched=False,
                    status=None,
                    response_tag=None,
                    elapsed_ms=None,
                    error=raw_result.reason,
                )
            )

        time.sleep(delay)

        rendered_result = fetch_page_rendered(target_url)
        rendered_accepted_body: bytes | None = None
        if isinstance(rendered_result, RenderedFetchResult):
            rendered_bodies.append(rendered_result.body)

            tag_name = None
            try:
                envelope = receive_fetch_response(
                    rendered_result.url, rendered_result.status, rendered_result.headers, rendered_result.body
                )
                tag_name = classify_response(envelope).name
                rendered_accepted_body = envelope.body
            except RejectedResponse:
                pass

            samples.append(
                ProbeSample(
                    url=rendered_result.url,
                    renderer="rendered",
                    fetched=True,
                    status=rendered_result.status,
                    response_tag=tag_name,
                    elapsed_ms=rendered_result.elapsed_ms,
                    error=None,
                )
            )
        else:
            samples.append(
                ProbeSample(
                    url=target_url,
                    renderer="rendered",
                    fetched=False,
                    status=None,
                    response_tag=None,
                    elapsed_ms=None,
                    error=rendered_result.reason,
                )
            )

        js_requirement = compare_raw_vs_rendered(raw_accepted_body, rendered_accepted_body).name

        extra_links = extract_same_domain_links(target_url, raw_accepted_body or b"", limit=max(pages - 1, 0))
        for link in extra_links:
            time.sleep(delay)

            extra_result = fetch_page_raw(link)
            if isinstance(extra_result, RawFetchResult):
                raw_bodies.append(extra_result.body)
                rate_limit_signals.append(detect_rate_limit_signal(extra_result.status, extra_result.headers))

                tag_name = None
                try:
                    envelope = receive_fetch_response(
                        extra_result.url, extra_result.status, extra_result.headers, extra_result.body
                    )
                    tag_name = classify_response(envelope).name
                except RejectedResponse:
                    pass

                samples.append(
                    ProbeSample(
                        url=extra_result.url,
                        renderer="raw",
                        fetched=True,
                        status=extra_result.status,
                        response_tag=tag_name,
                        elapsed_ms=extra_result.elapsed_ms,
                        error=None,
                    )
                )
            else:
                samples.append(
                    ProbeSample(
                        url=link,
                        renderer="raw",
                        fetched=False,
                        status=None,
                        response_tag=None,
                        elapsed_ms=None,
                        error=extra_result.reason,
                    )
                )

    rate_limit = summarize_rate_limit_signals(rate_limit_signals)

    profile = SiteProfile(
        domain=domain,
        probed_at=datetime.fromtimestamp(read_clock(), tz=timezone.utc).isoformat(),
        robots=robots,
        waf_vendor=waf_vendor,
        framework=framework,
        structured_data=structured_data,
        js_requirement=js_requirement,
        rate_limit=rate_limit,
        samples=tuple(samples),
    )

    path = save_site_profile(profile, raw_bodies, rendered_bodies)
    print(f"Saved probe profile to {path}")
