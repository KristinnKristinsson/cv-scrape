from cv_scrape.logic.extract_technologies_mentioned import extract_technologies_mentioned
from cv_scrape.state.job_posting import JobPosting


def _job(description: str) -> JobPosting:
    return JobPosting(url="https://example.com/1", source_domain="example.com", title="Data Engineer", company="Acme", description=description)


def test_matches_known_technologies():
    signals = extract_technologies_mentioned(_job("We use Python, SQL, Docker and Kafka every day."))
    assert set(signals) == {"python", "sql", "docker", "kafka"}


def test_no_matches_returns_empty_tuple():
    assert extract_technologies_mentioned(_job("We value teamwork and communication.")) == ()


def test_matches_named_cicd_tools():
    # "git" also matches here as a substring of "GitHub" — a pre-existing quirk of
    # substring matching, not introduced by the ci/cd keywords.
    signals = extract_technologies_mentioned(_job("You'll own our Jenkins and GitHub Actions pipelines."))
    assert set(signals) == {"jenkins", "github actions", "git"}


def test_matches_generic_cicd_phrasing_without_a_named_tool():
    signals = extract_technologies_mentioned(_job("Experience with CI/CD and continuous delivery is expected."))
    assert set(signals) == {"ci/cd", "continuous delivery"}


def test_matches_bi_and_warehouse_tools():
    signals = extract_technologies_mentioned(
        _job("BI tools such as Looker, Tableau, or Power BI is a plus. Delta Lake and Iceberg experience helps.")
    )
    assert set(signals) == {"looker", "tableau", "power bi", "delta lake", "iceberg"}


def test_matches_mongodb_and_sql_server():
    # "sql" also matches here as a substring of "SQL Server" — expected, same
    # generic-plus-specific double-match pattern as "postgres"/"postgresql".
    signals = extract_technologies_mentioned(_job("Experience with SQL Server/SSIS-legacy and MongoDB is a plus."))
    assert set(signals) == {"sql", "sql server", "ssis", "mongodb"}


def test_does_not_match_common_words_that_only_resemble_dropped_candidates():
    # "rust", "excel", "nifi", "sap" were considered and rejected as keywords —
    # near-total false-positive traps on the real sample (see the module's
    # deliberately-absent note). This guards against silently reintroducing them.
    signals = extract_technologies_mentioned(
        _job("We are a trusted partner. You are an excellent communicator. ASAP start, significant impact.")
    )
    assert signals == ()
