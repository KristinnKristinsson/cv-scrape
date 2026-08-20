"""Flow: CLI-triggered. Sequences interaction -> effect. No decision, no mutation of
its own.
"""

from pathlib import Path

from cv_scrape.effect.save_cv import save_cv
from cv_scrape.interaction.parse_cv_document import parse_cv_document


def ingest_cv(path: str) -> None:
    cv = parse_cv_document(Path(path))
    save_cv(cv)
