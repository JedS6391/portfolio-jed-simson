from typing import Optional, Text
from collections import OrderedDict
from util import count_words
from markdown import Markdown
from flask import Flask, current_app as app
from threading import Lock

import os
import codecs
import time
import datetime
import uuid

from portfolio.models import Post

class InvalidPathException(Exception):
    pass

class DuplicationPostException(Exception):
    pass

class Blog(object):
    '''
        Manager for blog posts.

        This custom implementation loads blog posts in the form of markdown files
        and collects information about them. The posts are stored so that a view
        can query for specific posts, range of posts, or posts which match a tag.

        The loading of posts should be done before any querying is done to ensure
        that all data is loaded and cached.
    '''

    def __init__(self):
        self._cache = OrderedDict()
        self.path: Optional[Text] = None
        self.parser: Optional[Markdown] = None
        self.max_age: int = -1
        self.loading_lock = Lock()
        self.loaded: bool = False

    def init_app(self, path: Text, parser: Markdown, app: Flask, max_age: int):
        ''' Allows initialisation to be defered until Flask app creation. '''

        if 'blog' not in app.extensions:
            app.extensions['blog'] = {}

        app.extensions['blog'] = self

        self.path = path
        self.parser = parser
        self.max_age = max_age

        self.app = app        

    def check_loaded(self):
        ''' Verifies that the loading process has been completed. '''

        if not self.loaded:
            self._load()

    def maybe_clear_cache(self):
        ''' Clears the cache, but only if it has reached ``self.max_age``. '''

        if (time.time() - self.cache_age) > self.max_age:
            # Expire the cache and reload any posts
            self._cache = OrderedDict()
            self.loaded = False
            
            self._load()

    def get_range(self, skip: int, limit: int):
        '''
            Fetches a range of posts.

            ``skip`` dictates how far into the list of posts to start the range,
            while ``limit`` controls how far the range should extend.

            e.g. when skip = 1, limit = 3, posts = [p_1, p_2, p_3, p_4, p_5],
            ``get_range()`` would return [p2, p3, p4].
        '''

        self.check_loaded()
        self.maybe_clear_cache()

        posts = list(self._cache.values())

        if limit:
            return posts[skip:skip+limit], len(posts)

        return posts, len(posts)

    def get(self, key: str):
        ''' Returns the post identified by the key given. '''

        self.check_loaded()
        self.maybe_clear_cache()

        return self._cache[key]

    def get_with_tag(self, tag: str):
        ''' Gets all posts with the specified tag. '''

        self.check_loaded()
        self.maybe_clear_cache()

        posts = list(self._cache.values())

        filtered = [
            post for post in posts
            if tag in post['tags']
        ]

        return filtered

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

            app.logger.debug('Loading blog posts from {}'.format(self.path))

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
                    app.logger.debug('Processed post: {}'.format(post.route))

                    blog_posts[post.route] = post

            blog_posts = sorted(blog_posts.items(), key=lambda i: i[1].route_date, reverse=True)

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

        # Get an approximate count of the number of words in the post.
        meta['words'] = count_words(text)

        # Use the markdown parser to parse convert the raw text and collect metadata.
        if self.parser:
            self.parser.convert(text)
            meta.update({k: v[0] for (k, v) in self.parser.Meta.items()})

        # Split tags into list
        tag_string = meta['tags']
        meta['tags'] = tag_string.lower().split(', ')

        return Post(post_id, text, meta)

# For use in ``app.py``, i.e. app.init_app(blog_manager)
blog_manager = Blog()
