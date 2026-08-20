"""Flow: Scrapy item pipeline. Sequences observation -> effect. No decision, no
direct mutation of its own — only ordered calls and routing on tags they return.
"""

from datetime import datetime, timezone

from cv_scrape.effect.save_job_posting import save_job_posting
from cv_scrape.observation.read_clock import read_clock
from cv_scrape.state.job_posting import JobPosting


class JobPostingPipeline:
    def process_item(self, item: JobPosting, spider) -> JobPosting:
        fetched_at = datetime.fromtimestamp(read_clock(), tz=timezone.utc).isoformat()
        save_job_posting(item, fetched_at=fetched_at)
        return item
