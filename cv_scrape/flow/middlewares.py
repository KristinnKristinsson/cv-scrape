"""Flow: [WAF] Scrapy downloader middleware. See structure.md. Not implemented yet —
sequences calls into the logic/effect/observation WAF stubs, but those calls are
no-ops today, so requests pass through unthrottled. Fill in process_request /
process_response to call select_rate_limit_policy_for_domain -> consume_rate_limit_token,
select_header_pool_for_domain -> rotate_header_selection, classify_response ->
decide_retry_action, read/update_session_state — with zero restructuring here.
"""


class WafCountermeasureMiddleware:
    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response
