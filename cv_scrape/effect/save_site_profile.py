"""Effect: writes each run to its own directory under data/probes/<domain>/<run_id>/,
never overwriting a prior run — this is investigation output for the skill and the
user to read, not scrape results, so unlike save_job_posting's convergent upsert we
deliberately keep every run's evidence intact and dated rather than converging
runs onto one shared, possibly-shrinking set of files. Site data itself (job
postings) stays on the convergent-upsert path; only this investigation output
works this way. run_id is profile.probed_at (already unique per run, since it
comes from observation/read_clock.py), sanitized for use as a path segment.

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
    run_id = profile.probed_at.replace(":", "-")
    run_dir = PROBES_DIR / profile.domain / run_id
    raw_dir = run_dir / "raw"
    rendered_dir = run_dir / "rendered"
    raw_dir.mkdir(parents=True, exist_ok=True)
    rendered_dir.mkdir(parents=True, exist_ok=True)

    for index, body in enumerate(raw_bodies):
        (raw_dir / f"{index}.html").write_bytes(body)
    for index, body in enumerate(rendered_bodies):
        (rendered_dir / f"{index}.html").write_bytes(body)

    profile_path = run_dir / "profile.json"
    profile_path.write_text(json.dumps(asdict(profile), indent=2), encoding="utf-8")
    return profile_path
