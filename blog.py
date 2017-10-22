import os
import codecs
import time
from collections import OrderedDict
from util import count_words

from portfolio.models import Post

class Blog(object):

    def __init__(self, path=None, parser=None, max_age=None, app=None):
        self._cache = OrderedDict()
        self.path = path
        self.parser = parser
        self.max_age = max_age

        if app:
            self.init_app(path, parser, app)

    def init_app(self, path, parser, max_age, app):
        if 'blog' not in app.extensions:
            app.extensions['blog'] = {}

        app.extensions['blog'] = self

        self.path = path
        self.parser = parser
        self.max_age = max_age

        self.app = app
        self._load()

    def maybe_clear_cache(self):
        if (time.time() - self.cache_age) > self.max_age:
            # Expire the cache and reload any posts
            self._cache = OrderedDict()
            self._load()

    def get_range(self, skip, limit):
        self.maybe_clear_cache()

        posts = list(self._cache.values())

        if limit:
            return posts[skip:skip+limit], len(posts)

        return posts, len(posts)

    def get(self, key):
        return self._cache[key]

    def get_with_tag(self, tag):
        self.maybe_clear_cache()

        posts = list(self._cache.values())

        filtered = [
            post for post in posts
            if tag in post['tags']
        ]

        return filtered

    def _load(self):
        '''
            Adapted from Flask-Portfolio:
            https://github.com/longboardcat/Flask-Portfolio

            TODO: Refactor so that Post objects are created and possibly
                  cache metadata for posts
        '''
        if not os.path.exists(self.path):
            # TODO: Better to return None?
            raise OSError('Supplied path for blog posts does not exist - {}'
                          .format(self.path))

        def remove_extension(title, extension):
            return title.replace(extension, '')

        def construct_post_id(counter):
            return 'blog_post_' + str(counter)

        blog_posts = {}
        filenames = os.listdir(self.path)

        # Handle hidden files that may exist on Mac
        if '.DS_Store' in filenames:
            filenames.remove('.DS_Store')

        current = 1

        # Go through each file and construct an appropriate model
        for file in filenames:
            st = os.stat(self.path + file)
            last_modified = time.ctime(st.st_mtime)
            meta = {}

            post_id = construct_post_id(current)

            # TODO: Better to construct this information using Meta Extension
            # Markdown Preprocessor?
            meta['filename'] = file
            meta['filesize'] = st.st_size

            with codecs.open(self.path + file, 'r', encoding='utf-8') as f:
                text = f.read()
                meta['words'] = count_words(text)

            if self.parser:
                self.parser.convert(text)
                meta.update({k: v[0] for (k, v) in self.parser.Meta.items()})

            # Split tags into list
            tag_string = meta['tags']
            meta['tags'] = tag_string.lower().split(', ')

            post = Post(post_id, text, meta, last_modified)

            if post.route in blog_posts:
                # A blog post made on the exact same day and with the same title as another? Unlikely!
                # But if this happens we'll just throw an error so that the user can sort their posts out...
                raise OSError('Duplicate blog creation date + title combination {}'.format(post.route))
            else:
                blog_posts[post.route] = post

            current += 1

        blog_posts = sorted(blog_posts.items(), key=lambda i: i[1]['date'], reverse=True)

        for route, post in blog_posts:
            self._cache[route] = post

        self.cache_age = time.time()


# For use in ``app.py``, i.e. app.init_app(blog_manager)
blog_manager = Blog()
