class Post:

    def __init__(self, post_id, text, meta, modified, tags=[]):

        self.id = post_id
        self.text = text
        self.meta = meta
        self.last_modified = modified
        self.tags = tags

    def __getitem__(self, name):
        return self.meta[name]
