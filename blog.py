import os
import codecs
import time
import datetime
from collections import OrderedDict
from util import count_words

from portfolio.models import Post

class PostsNotLoadedException(Exception):
    pass

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

    def __init__(self, path=None, parser=None, max_age=None, app=None):
        self._cache = OrderedDict()
        self.path = path
        self.parser = parser
        self.max_age = max_age
        self.loaded = False

        if app:
            self.init_app(path, parser, app)

    def init_app(self, path, parser, max_age, app):
        ''' Allows initialisation to be defered until Flask app creation. '''

        if 'blog' not in app.extensions:
            app.extensions['blog'] = {}

        app.extensions['blog'] = self

        self.path = path
        self.parser = parser
        self.max_age = max_age

        self.app = app
        self._load()

    def check_loaded(self):
        ''' Verifies that the loading process has been completed. '''

        if not self.loaded:
            raise PostsNotLoadedException('Posts were queried but were not loaded beforehand.')

    def maybe_clear_cache(self):
        ''' Clears the cache, but only if it has reached ``self.max_age``. '''

        if (time.time() - self.cache_age) > self.max_age:
            # Expire the cache and reload any posts
            self._cache = OrderedDict()
            self._load()

    def get_range(self, skip, limit):
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

    def get(self, key):
        ''' Returns the post identified by the key given. '''

        self.check_loaded()
        self.maybe_clear_cache()

        return self._cache[key]

    def get_with_tag(self, tag):
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

        if not os.path.exists(self.path):
            # The path given for searching for blog posts does not exist, so throw an early error.
            raise InvalidPathException('Supplied path for blog posts does not exist - {}'.format(self.path))

        blog_posts = {}
        filenames = os.listdir(self.path)

        # Handle hidden files that may exist on Mac
        if '.DS_Store' in filenames:
            filenames.remove('.DS_Store')

        current = 1

        # Go through each file and construct an appropriate model
        for file in filenames:
            # Get system info about the file
            st = os.stat(self.path + file)
            last_modified = datetime.datetime.fromtimestamp(st.st_mtime)
            meta = {}

            post_id = 'blog_post_{}'.format(str(current))

            # Collect a bunch of metadata about this file (and the post it contains)
            meta['last modified'] = last_modified
            meta['filename'] = file
            meta['filesize'] = st.st_size

            with codecs.open(self.path + file, 'r', encoding='utf-8') as f:
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

            post = Post(post_id, text, meta)

            if post.route in blog_posts:
                # A blog post made on the exact same day and with the same title as another? Unlikely!
                # But if this happens we'll just throw an error so that the user can sort their posts out...
                raise DuplicationPostException('Duplicate blog creation date + title combination {}'.format(post.route))
            else:
                blog_posts[post.route] = post

            current += 1

        blog_posts = sorted(blog_posts.items(), key=lambda i: i[1]['date'], reverse=True)

        for route, post in blog_posts:
            self._cache[route] = post

        self.cache_age = time.time()
        self.loaded = True


# For use in ``app.py``, i.e. app.init_app(blog_manager)
blog_manager = Blog()
