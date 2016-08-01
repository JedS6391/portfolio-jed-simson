from .helpers import get_view_count


class Post:
    def __init__(self, post_id, text, meta, modified):
        self.id = post_id
        self.text = text
        self.meta = meta
        self.last_modified = modified

        self.get_view_count()

    def __getitem__(self, name):
        return self.meta[name]

    def get_view_count(self):
        try:
            views = get_view_count(self.meta['title'])
            self.meta['views'] = views
        except KeyError:
            self.meta['views'] = 0

    @property
    def info(self):
        info = {}
        info['Post ID'] = self.id
        info['Modified'] = self.last_modified

        info.update({k.title(): v for (k, v) in self.meta.items()})

        return info.items()

