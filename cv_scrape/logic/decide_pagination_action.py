"""Logic: decide whether another page of JobSearch API results should be fetched,
given the offset about to be used and the page that just came back. Pure decision
over values already in hand.
"""

from enum import Enum, auto


class PaginationAction(Enum):
    CONTINUE = auto()
    STOP = auto()


def decide_pagination_action(next_offset: int, page_total: int, postings_on_page: int) -> PaginationAction:
    if next_offset >= page_total or postings_on_page == 0:
        return PaginationAction.STOP
    return PaginationAction.CONTINUE
