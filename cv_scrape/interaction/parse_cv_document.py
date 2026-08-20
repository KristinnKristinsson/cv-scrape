"""Interaction: boundary for the user's own CV file (pdf/docx/txt). Validates/normalizes/
rejects before ParsedCv is trusted downstream.
"""

from pathlib import Path

from cv_scrape.state.cv import ParsedCv


class RejectedCvDocument(Exception):
    """Raised when the CV file can't be read or normalized into structured form."""


def parse_cv_document(path: Path) -> ParsedCv:
    raise NotImplementedError
