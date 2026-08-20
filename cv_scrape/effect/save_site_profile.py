"""Effect: convergent write — safe to repeat, overwrites in place. Persists probe
findings as files under data/probes/, not the SQLite store: this is investigation
output for the skill and the user to read, not scrape results.

raw_bodies/rendered_bodies are the fetched bytes for each ProbeSample in profile.samples
whose renderer matches, in the same order — sample i's snapshot is
{renderer}/{index within that renderer's samples}.html.
"""

import json
from dataclasses import asdict
from pathlib import Path

from cv_scrape.state.site_profile import SiteProfile

PROBES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "probes"


def save_site_profile(profile: SiteProfile, raw_bodies: list[bytes], rendered_bodies: list[bytes]) -> Path:
    site_dir = PROBES_DIR / profile.domain
    raw_dir = site_dir / "raw"
    rendered_dir = site_dir / "rendered"
    raw_dir.mkdir(parents=True, exist_ok=True)
    rendered_dir.mkdir(parents=True, exist_ok=True)

    for index, body in enumerate(raw_bodies):
        (raw_dir / f"{index}.html").write_bytes(body)
    for index, body in enumerate(rendered_bodies):
        (rendered_dir / f"{index}.html").write_bytes(body)

    profile_path = site_dir / "profile.json"
    profile_path.write_text(json.dumps(asdict(profile), indent=2), encoding="utf-8")
    return profile_path
