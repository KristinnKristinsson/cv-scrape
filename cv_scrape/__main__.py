"""Thin CLI dispatcher. Flow: parses argv, calls into flow/*, does not decide or mutate itself.

argv is uncontrolled input, so parsing it is technically an interaction-boundary concern —
but argparse *is* the validate/reject/normalize step (it rejects bad input itself, via
SystemExit), and there is no further trust decision left for a separate interaction/
module to make. Kept inline as framework wiring, same as settings.py, rather than split
into its own piece for a boundary the stdlib already fully guards.
"""

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cv_scrape")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("evaluate", help="Evaluate curated stored postings against candidate.yaml.")

    probe = subparsers.add_parser("probe", help="Investigate a site before writing a spider for it.")
    probe.add_argument("url", help="Full target URL, including scheme, e.g. https://example.com/jobs")
    probe.add_argument(
        "--pages", type=int, default=3, help="Sample size: the target page plus this many extra same-domain links."
    )

    fetch_jobs = subparsers.add_parser(
        "fetch-jobs", help="Fetch job postings from Arbetsformedlingen's public JobSearch API."
    )
    fetch_jobs.add_argument("--region", help="Taxonomy region code, e.g. CifL_Rzy_Mku for Stockholms lan.")
    fetch_jobs.add_argument(
        "--occupation-group",
        action="append",
        default=[],
        help="Taxonomy occupation-group (SSYK level 4) code. Repeatable.",
    )
    fetch_jobs.add_argument(
        "--employment-type", action="append", default=[], help="Taxonomy employment-type code. Repeatable."
    )
    fetch_jobs.add_argument("--q", help="Free-text query (searches headline, description, employer name).")

    subparsers.add_parser(
        "extract-signals", help="Extract inferred signals (role family, seniority, ...) for every stored job posting."
    )

    args = parser.parse_args(argv)

    if args.command == "evaluate":
        from collections import Counter

        from cv_scrape.flow.evaluate_candidate_fit import evaluate_candidate_fit

        evaluations = evaluate_candidate_fit()
        counts = Counter(e.recommendation for e in evaluations)
        print(f"Evaluated {len(evaluations)} curated job posting(s) against candidate.yaml.")
        for tag in ("APPLY", "APPLY_STRETCH", "LOW_PRIORITY", "SKIP"):
            print(f"  {tag}: {counts.get(tag, 0)}")
        return 0

    if args.command == "probe":
        from cv_scrape.flow.probe_site import probe_site

        probe_site(args.url, pages=args.pages)
        return 0

    if args.command == "fetch-jobs":
        from cv_scrape.flow.fetch_jobs_from_api import fetch_jobs_from_api

        saved = fetch_jobs_from_api(
            region=args.region,
            occupation_group=args.occupation_group,
            employment_type=args.employment_type,
            q=args.q,
        )
        print(f"Saved {saved} job posting(s).")
        return 0

    if args.command == "extract-signals":
        from cv_scrape.flow.extract_job_signals import extract_job_signals

        extracted = extract_job_signals()
        print(f"Extracted signals for {extracted} job posting(s).")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
