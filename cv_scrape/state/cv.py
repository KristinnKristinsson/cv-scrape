"""State: the user's own CV, parsed into structured form."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ParsedCv:
    raw_text: str
    skills: tuple[str, ...] = field(default_factory=tuple)
    titles_held: tuple[str, ...] = field(default_factory=tuple)
    years_experience: float | None = None
