"""Logic: decide what a fetched robots.txt means for one target path. Pure decision
over already-fetched text — no fetch happens here, that's
observation/fetch_page_raw.py.
"""

from urllib.robotparser import RobotFileParser

from cv_scrape.state.robots_evaluation import RobotsEvaluation


def evaluate_robots_txt(robots_txt: str | None, target_path: str, user_agent: str) -> RobotsEvaluation:
    if robots_txt is None:
        return RobotsEvaluation(fetched=False, allowed=True, crawl_delay=None)

    parser = RobotFileParser()
    parser.parse(robots_txt.splitlines())

    return RobotsEvaluation(
        fetched=True,
        allowed=parser.can_fetch(user_agent, target_path),
        crawl_delay=parser.crawl_delay(user_agent),
    )
