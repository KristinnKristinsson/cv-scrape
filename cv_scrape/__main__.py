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

    ingest_cv = subparsers.add_parser("ingest-cv", help="Parse and store a CV file.")
    ingest_cv.add_argument("path", help="Path to the CV file (pdf/docx/txt).")

    subparsers.add_parser("match", help="Score stored job postings against the stored CV.")

    probe = subparsers.add_parser("probe", help="Investigate a site before writing a spider for it.")
    probe.add_argument("url", help="Full target URL, including scheme, e.g. https://example.com/jobs")
    probe.add_argument(
        "--pages", type=int, default=3, help="Sample size: the target page plus this many extra same-domain links."
    )

    args = parser.parse_args(argv)

    if args.command == "ingest-cv":
        from cv_scrape.flow.ingest_cv import ingest_cv as run_ingest_cv

        run_ingest_cv(args.path)
        return 0

    if args.command == "match":
        from cv_scrape.flow.match_jobs_to_cv import match_jobs_to_cv

        match_jobs_to_cv()
        return 0

    if args.command == "probe":
        from cv_scrape.flow.probe_site import probe_site

        probe_site(args.url, pages=args.pages)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
