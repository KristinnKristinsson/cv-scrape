"""State: the persisted findings from probing one site before deciding how to scrape
it — framework, WAF vendor, robots.txt posture, structured-data/API discovery, JS
requirement, rate-limit signals, and the raw sample of requests behind them all.
"""

from dataclasses import dataclass, field

from cv_scrape.state.framework_signals import FrameworkSignals
from cv_scrape.state.probe_sample import ProbeSample
from cv_scrape.state.rate_limit_findings import RateLimitFindings
from cv_scrape.state.robots_evaluation import RobotsEvaluation
from cv_scrape.state.structured_data_findings import StructuredDataFindings


@dataclass(frozen=True)
class SiteProfile:
    domain: str
    probed_at: str
    robots: RobotsEvaluation
    waf_vendor: str
    framework: FrameworkSignals
    structured_data: StructuredDataFindings
    js_requirement: str
    rate_limit: RateLimitFindings
    samples: tuple[ProbeSample, ...] = field(default_factory=tuple)
