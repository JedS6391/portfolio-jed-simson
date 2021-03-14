from typing import Text, Dict, List, Any
from util import slugify
from datetime import datetime 

PostMetadata = Dict[str, Any]

class Post:
    ''' Represents a blog post.

        A post is essentially a wrapper around its text content and a bunch of metadata.
    '''

    def __init__(self, post_id: str, text: Text, meta: PostMetadata):
        self.id = post_id
        self.text = text
        self.meta = meta
        self.year = self.metadata_date.strftime('%Y')
        self.month = self.metadata_date.strftime('%m')
        self.day = self.metadata_date.strftime('%d')

    def __getitem__(self, name) -> Any:
        # Allows us access meta properties with obj['key'] syntax.
        return self.meta[name]

    @property
    def metadata_date(self) -> datetime:
        # Each post should have a date stored in metadata that we can extract components from.
        return datetime.strptime(self['date'], '%B %d, %Y')

    @property
    def slug(self) -> str:
        ''' Generates a slugified version of the post's title. '''
        return slugify(self['title'])

    @property
    def route(self) -> str:
        ''' Builds a route string for this post in the format /<year>/<month>/<day>/<slug>/. '''
        return '{}/{}/{}/{}'.format(self.year, self.month, self.day, self.slug)

    @property
    def info(self) -> List[Any]:
        ''' Gives a collection of the metadata attributes. '''
        info = {}
        info['Post ID'] = self.id

        info.update({k.title(): v for (k, v) in self.meta.items()})

        return sorted(info.items(), key=lambda t: t[0])

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return 'Post<{}, {}, {}, {}>'.format(self.id, self['title'], self.slug, self.route)

