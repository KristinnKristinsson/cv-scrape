from cv_scrape.logic.classify_role_family import RoleFamily, classify_role_family
from cv_scrape.state.job_posting import JobPosting


def _job(title: str, description: str = "") -> JobPosting:
    return JobPosting(url="https://example.com/1", source_domain="example.com", title=title, company="Acme", description=description)


def test_data_engineer_title_matches():
    assert classify_role_family(_job("Junior Data Engineer")) is RoleFamily.DATA_ENGINEER
    assert classify_role_family(_job("Dataingenjör till PTS")) is RoleFamily.DATA_ENGINEER


def test_analytics_engineer_title_matches():
    assert classify_role_family(_job("Senior Analytics Engineer, Finance")) is RoleFamily.ANALYTICS_ENGINEER


def test_etl_integration_title_matches():
    assert classify_role_family(_job("Integrationsutvecklare inom E-Commerce")) is RoleFamily.ETL_INTEGRATION


def test_data_platform_title_matches():
    assert classify_role_family(_job("Data Platform Engineer")) is RoleFamily.DATA_PLATFORM


def test_python_developer_requires_data_hint_in_description():
    assert (
        classify_role_family(_job("Python Developer", "You will build our data pipelines and warehouse."))
        is RoleFamily.PYTHON_DATA_DEVELOPER
    )
    assert classify_role_family(_job("Full-stack Python/Django developer", "Build our e-commerce website.")) is RoleFamily.UNMATCHED


def test_backend_developer_requires_data_hint_in_description():
    assert (
        classify_role_family(_job("Backendutvecklare", "Fokus på ETL, dataintegration och datakvalitet."))
        is RoleFamily.DATA_HEAVY_BACKEND
    )
    assert classify_role_family(_job("Backend Engineer", "Build our gameplay systems in C#.")) is RoleFamily.UNMATCHED


def test_unrelated_title_is_unmatched():
    assert classify_role_family(_job("Grävmaskinist")) is RoleFamily.UNMATCHED
