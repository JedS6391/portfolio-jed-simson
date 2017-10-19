from math import ceil

class Pagination(object):
    '''
        Helper class to facilitate the paging logic for blog posts.

        The object will always represent the current page.
    '''

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        ''' The number of pages the posts are split into. '''
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        ''' Specifies whether the current page has a preceding page. '''
        return self.page > 1

    @property
    def has_next(self):
        ''' Specifies whether there is another page after the current one. '''
        return self.page < self.pages

    def generate(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        ''' Generates the sequence of pages. '''
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
