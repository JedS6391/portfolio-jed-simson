from typing import Optional, Text, Tuple, List, Callable
from collections import OrderedDict
from markdown import Markdown
import logging
from threading import Lock

import os
import codecs
import time
import datetime
import uuid

from portfolio.models import Post

class BlogNotInitialisedException(Exception):
    pass

class InvalidPathException(Exception):
    pass

class DuplicationPostException(Exception):
    pass

class Blog:
    ''' Provides mechanisms for interacting with blog posts.

        This custom implementation loads blog posts in the form of Markdown files
        and collects information about them as metadata. 
        
        The posts are stored so that a caller can query for specific posts, range of posts, or posts which match a tag.

        Loading of posts is done on demand and cached, with automatic cache invalidation after a certain time.
    '''

    def __init__(self):
        self._cache: OrderedDict[str, Post] = OrderedDict()
        self.path: Optional[Text] = None
        self.parser: Optional[Markdown] = None
        self.cache_age: float = 0.0
        self.max_cache_age: int = -1
        self.loading_lock = Lock()
        self.loaded: bool = False
        self.initialised = False

    def initialise(self, path: Text, parser: Markdown, max_cache_age: int):
        '''  Initialises the blog. '''
        self.path = path
        self.parser = parser
        self.max_cache_age = max_cache_age
        self.initialised = True  

    def check_loaded(self):
        ''' Verifies that the loading process has been completed. If not, then loading will be performed. '''
        if not self.initialised:
            raise BlogNotInitialisedException('Blog must first be initialised.')

        if not self.loaded:
            self._load()

    def maybe_clear_cache(self):
        ''' Clears the cache once it has reached ``self.max_cache_age``. '''

        if (time.time() - self.cache_age) > self.max_cache_age:
            # Expire the cache and reload any posts
            self._cache = OrderedDict()
            self.loaded = False
            
            self._load()

    def get_range(self, skip: int, limit: int) -> Tuple[List[Post], int]:
        ''' Fetches a range of posts.

            ``skip`` dictates how far into the list of posts to start the range.
            
            ``limit`` controls how far the range should extend.

            e.g. when skip = 1, limit = 3, posts = [p_1, p_2, p_3, p_4, p_5],
            ``get_range()`` would return [p_2, p_3, p_4].
        '''

        self.check_loaded()
        self.maybe_clear_cache()

        posts = list(self._cache.values())

        if limit:
            return posts[skip:skip+limit], len(posts)

        return posts, len(posts)

    def get(self, key: str) -> Post:
        ''' Returns the post identified by the key given. '''

        self.check_loaded()
        self.maybe_clear_cache()

        return self._cache[key]

    def get_matching(self, predicate: Callable[[Post], bool]) -> List[Post]:
        ''' Gets all posts matching the specified predicate. '''

        self.check_loaded()
        self.maybe_clear_cache()

        filtered_posts = filter(predicate, self._cache.values())

        return list(filtered_posts)

    def _load(self):
        '''
            Loads post information from markdown files in ``self.path``.

            Adapted from Flask-Portfolio:
            https://github.com/longboardcat/Flask-Portfolio
        '''
        with self.loading_lock:
            if self.loaded:
                # Another thread has loaded the posts while waiting for the lock so there's nothing to do.
                return

            logging.debug('Loading blog posts from {}'.format(self.path))

            if not os.path.exists(self.path):
                # The path given for searching for blog posts does not exist, so throw an early error.
                raise InvalidPathException('Supplied path for blog posts does not exist - {}'.format(self.path))

            blog_posts = {}
            filenames = os.listdir(self.path)            

            # Go through each file and construct an appropriate model
            for file in filenames:
                post = self.create_post(file)

                if post.route in blog_posts:
                    # A blog post made on the exact same day and with the same title as another? Unlikely!
                    # But if this happens we'll just throw an error so that the user can sort their posts out...
                    raise DuplicationPostException('Duplicate blog creation date + title combination {}'.format(post.route))
                else:
                    logging.debug('Processed post: {}'.format(post.route))

                    blog_posts[post.route] = post

            blog_posts = sorted(blog_posts.items(), key=lambda i: i[1].metadata_date, reverse=True)

            for route, post in blog_posts:
                self._cache[route] = post

            self.cache_age = time.time()
            self.loaded = True

    def create_post(self, filename: str) -> Post:
        # Get system info about the file
        st = os.stat(self.path + filename)
        last_modified = datetime.datetime.fromtimestamp(st.st_mtime)
        meta = {}

        post_id = 'blog_post_{}'.format(str(uuid.uuid4()))

        # Collect a bunch of metadata about this file (and the post it contains)
        meta['last modified'] = last_modified
        meta['filename'] = filename
        meta['filesize'] = st.st_size

        with codecs.open(self.path + filename, 'r', encoding='utf-8') as f:
            text = f.read()

        # Use the markdown parser to parse convert the raw text and collect metadata.
        if self.parser:
            self.parser.convert(text)
            meta.update({k: v[0] for (k, v) in self.parser.Meta.items()})

        # Split tags into list
        tag_string = meta['tags']
        meta['tags'] = tag_string.lower().split(', ')

        return Post(post_id, text, meta)

blog_manager = Blog()
