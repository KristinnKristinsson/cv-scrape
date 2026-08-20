"""Scrapy-mandated static config. Wiring only — not app logic. See structure.md."""

BOT_NAME = "cv_scrape"

SPIDER_MODULES = ["cv_scrape.spiders"]
NEWSPIDER_MODULE = "cv_scrape.spiders"

ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    "cv_scrape.flow.pipelines.JobPostingPipeline": 300,
}

DOWNLOADER_MIDDLEWARES = {
    "cv_scrape.flow.middlewares.WafCountermeasureMiddleware": 543,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
