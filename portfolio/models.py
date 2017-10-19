from util import slugify
from datetime import datetime

class Post:
    '''
        Models a blog post.

        A post is essentially a wrapper around its text and a bunch of metadata.
        Because posts are routed in the form /<year>/<month>/<day>/<slug>/, each
        post is responsible for handling the logic to generate those properties.
    '''

    def __init__(self, post_id, text, meta, modified):
        self.id = post_id
        self.text = text
        self.meta = meta
        self.last_modified = modified
        self.route_date = datetime.strptime(self['date'], '%B %d, %Y')
        self.year = self.route_date.strftime('%Y')
        self.month = self.route_date.strftime('%m')
        self.day = self.route_date.strftime('%d')

    def __getitem__(self, name):
        # Let's us access meta properties with obj['key'] syntax.
        return self.meta[name]

    @property
    def slug(self):
        ''' Generates a slugified version of the post's title. '''
        return slugify(self['title'])

    @property
    def route(self):
        ''' Builds a route string for this post in the format /<year>/<month>/<day>/<slug>/. '''
        return '{}/{}'.format(self.route_date.strftime('%Y/%m/%d'), self.slug)

    @property
    def info(self):
        ''' Gives a collection of the metadata attributes. '''
        info = {}
        info['Post ID'] = self.id
        info['Modified'] = self.last_modified

        info.update({k.title(): v for (k, v) in self.meta.items()})

        return info.items()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'Post<{}, {}, {}, {}>'.format(self.id, self['title'], self.slug, self.route)

