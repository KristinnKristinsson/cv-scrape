from cv_scrape.logic.evaluate_robots_txt import evaluate_robots_txt


def test_missing_robots_txt_defaults_to_allowed():
    result = evaluate_robots_txt(None, "/jobs", "cv-scrape-probe")
    assert result.fetched is False
    assert result.allowed is True
    assert result.crawl_delay is None


def test_disallowed_path_is_not_allowed():
    robots_txt = "User-agent: *\nDisallow: /jobs\n"
    result = evaluate_robots_txt(robots_txt, "/jobs", "cv-scrape-probe")
    assert result.fetched is True
    assert result.allowed is False


def test_crawl_delay_parsed():
    robots_txt = "User-agent: *\nCrawl-delay: 5\nDisallow:\n"
    result = evaluate_robots_txt(robots_txt, "/jobs", "cv-scrape-probe")
    assert result.allowed is True
    assert result.crawl_delay == 5.0
