from cv_scrape.logic.decide_pagination_action import PaginationAction, decide_pagination_action


def test_continues_while_offset_is_below_total_and_page_has_postings():
    assert decide_pagination_action(next_offset=100, page_total=250, postings_on_page=100) is PaginationAction.CONTINUE


def test_stops_once_offset_reaches_total():
    assert decide_pagination_action(next_offset=250, page_total=250, postings_on_page=50) is PaginationAction.STOP


def test_stops_on_an_empty_page_even_if_offset_is_still_below_total():
    assert decide_pagination_action(next_offset=100, page_total=250, postings_on_page=0) is PaginationAction.STOP
