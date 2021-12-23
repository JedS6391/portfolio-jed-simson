from math import ceil
from typing import Iterator, Optional

class Pagination:
    ''' Provides functionality to facilitate paging logic. '''

    def __init__(self, page: int, per_page: int, total_count: int):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self) -> int:
        ''' The number of pages that are available. '''
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self) -> bool:
        ''' Indicates whether there is a page before the current. '''
        return self.page > 1

    @property
    def has_next(self) -> bool:
        ''' Indicates whether there is a page after the current. '''
        return self.page < self.pages

    def generate(self, left_edge=2, left_current=2, right_current=5, right_edge=2) -> Iterator[Optional[int]]:
        ''' Generates the sequence of pages. 
        
            The parameters control how many page numbers should be generated either side of the current page.
        '''
        last = 0

        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
