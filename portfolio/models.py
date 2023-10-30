from datetime import datetime 
from typing import Text, Dict, List, Any
from unicodedata import normalize

import re

PUNCTUATION_RE = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text: str) -> str:
    result = []

    for word in PUNCTUATION_RE.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')

        if word:
            result.append(word.decode('utf-8'))

    return '-'.join(result)

PostMetadata = Dict[str, Any]

class Post:
    ''' Represents a blog post.

        A post is essentially a wrapper around its text content and a bunch of metadata.
    '''

    def __init__(self, post_id: str, text: Text, html: Text, meta: PostMetadata):
        self.id = post_id
        self.text = text
        self.html = html
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

class Project:
    ''' Represents a project. 

        A project will be included as part of the project feed and can be loaded from different sources as appropriate.
    '''

    def __init__(self, project_id: str, name: str, description: str, link: str, link_description: str):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.link = link
        self.link_description = link_description

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return 'Project<{}, {}, {}, {}>'.format(self.project_id, self.name, self.description, self.link)