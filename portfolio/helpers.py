from math import ceil
import os
import json

VIEW_COUNT_FILE = os.environ.get('VIEW_COUNT_FILE', 'view_count.json')


def get_view_count(title):
    with open(VIEW_COUNT_FILE, 'r') as f:
        views = json.load(f)

    # Raises KeyError if title is not in views.
    # Caller must handle
    return views[title]


def update_view_count(post):
    with open(VIEW_COUNT_FILE, 'r') as f:
        views = json.load(f)

    title = post['title']

    if title in views:
        views[title] += 1
    else:
        views[title] = 1

    print('Updated {} : {}'.format(title, views[title]))

    with open(VIEW_COUNT_FILE, 'w+') as f:
        f.write(json.dumps(views))


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def generate(self, left_edge=2, left_current=2,
                 right_current=5, right_edge=2):
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
