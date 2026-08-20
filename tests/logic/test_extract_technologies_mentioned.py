from cv_scrape.logic.extract_technologies_mentioned import extract_technologies_mentioned
from cv_scrape.state.job_posting import JobPosting


def _job(description: str) -> JobPosting:
    return JobPosting(url="https://example.com/1", source_domain="example.com", title="Data Engineer", company="Acme", description=description)


def test_matches_known_technologies():
    signals = extract_technologies_mentioned(_job("We use Python, SQL, Docker and Kafka every day."))
    assert set(signals) == {"python", "sql", "docker", "kafka"}


def test_no_matches_returns_empty_tuple():
    assert extract_technologies_mentioned(_job("We value teamwork and communication.")) == ()
