"""Flow: Scrapy item pipeline. Sequences interaction -> logic -> effect. No decision,
no direct mutation of its own — only ordered calls and routing on tags they return.
"""

from cv_scrape.effect.save_job_posting import save_job_posting
from cv_scrape.state.job_posting import JobPosting


class JobPostingPipeline:
    def process_item(self, item: JobPosting, spider) -> JobPosting:
        save_job_posting(item)
        return item
