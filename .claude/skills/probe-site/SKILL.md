---
name: probe-site
description: Investigate a job-listing site before writing a spider for it — checks for a real public API/feed first, then runs the mechanical prober (cv_scrape probe) to profile WAF/challenge behavior, framework, robots.txt posture, and whether JS rendering is required, and turns the result into a recommendation plus a draft SitePolicy.
---

# Probe a site before scraping it

Use this before writing a spider for a new job-listing site (or when re-evaluating one
that's started failing). It combines a judgment step only you can do well
(recognizing a documented public API) with a mechanical step the project already
implements (`cv_scrape probe`).

## Steps

1. **Confirm the target.** Get the full URL (including scheme) of a representative
   listing page on the target site, and the organization/site name.

2. **Check for a real API or feed first — before anything else.** Use WebSearch for
   something like `"<organization/site name>" public API job listings` or
   `"<organization/site name>" developer API jobs`. Government employment agencies
   and larger job boards often publish one (e.g. Sweden's Arbetsförmedlingen /
   Platsbanken has a public JobSearch API at jobtechdev.se). No header or markup
   signature can prove a *documented* API exists — that's why this is a judgment
   step, not something `cv_scrape probe` tries to do. If a usable API exists, say so
   plainly: that's very likely the right answer, and scraping HTML would be solving
   a problem that's already solved. Still worth running the mechanical probe for the
   record, but lead the recommendation with the API.

3. **Run the mechanical prober:**
   ```
   uv run python -m cv_scrape probe <url> [--pages N]
   ```
   This fetches robots.txt (and stops sampling further if the target path is
   disallowed — respect that), then samples the target page (and a few same-domain
   links) both via plain HTTP and a real headless browser, classifying each
   response, detecting a known WAF vendor by signature, reading framework hints,
   finding structured data (JSON-LD, RSS/Atom, sitemap, API-looking hints), and
   diffing raw vs. rendered content to see if JS execution is required. It's a
   small, paced sample — not a crawl.

   If this is the first probe run in this environment, headless-browser fetches may
   fail with a "Playwright was just installed... run `playwright install`" message.
   That's expected until browser binaries are installed — flag it to the user rather
   than trying to work around it; don't run the install yourself without asking,
   it's a real download.

4. **Read the output.** The canonical result is
   `data/probes/<domain>/profile.json`, with raw and rendered HTML snapshots saved
   alongside under `data/probes/<domain>/raw/` and `data/probes/<domain>/rendered/`
   (files are indexed in fetch order — cross-reference against `profile.json`'s
   `samples` list, filtered by `renderer`, in the same order). Read the JSON and the
   snapshots that matter (usually `raw/0.html`, the primary page).

5. **Write the human summary** to `data/probes/<domain>/report.md`: API/feed found?,
   robots.txt verdict (allowed/disallowed + crawl-delay), WAF vendor, framework,
   JS-requirement verdict, rate-limit signals seen, and an explicit recommendation —
   one of: use the API, scrape static HTML, needs browser rendering, or defer
   (blocked by WAF or disallowed by robots.txt).

6. **If scraping looks viable and no API exists**, read the saved HTML and propose
   CSS/XPath selectors for the listing/title/company/description fields, then draft
   a ready-to-paste snippet:
   ```python
   SitePolicy(
       domain="...",
       listing_selector="...",
       title_selector="...",
       company_selector="...",
       description_selector="...",
   )
   ```
   (`cv_scrape/state/site_policy.py` defines the shape.) This is a draft for a human
   to review and wire into a real spider — don't write spider files yourself unless
   asked.

## What not to do

- Don't increase `--pages` or re-run the probe repeatedly against the same site to
  "get more signal" — the small paced sample is deliberate, to avoid tripping the
  exact WAF being characterized or burning the site before real scraping starts.
- Don't attempt to bypass or defeat a detected WAF/challenge — this skill is for
  reconnaissance and recommendation, not evasion.
- Don't scrape a path robots.txt disallows just because the probe reported it;
  surface it and let the human decide.
