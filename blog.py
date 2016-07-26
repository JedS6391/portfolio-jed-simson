import os
import codecs
import time
from util import count_words

from portfolio.models import Post


class Blog(object):

    def __init__(self, path=None, parser=None, app=None):
        self._cache = {}
        self.path = path
        self.parser = parser

        if app:
            self.init_app(path, parser, app)

    def init_app(self, path, parser, app):
        if 'blog' not in app.extensions:
            app.extensions['blog'] = {}

        app.extensions['blog'] = self

        self.path = path
        self.parser = parser

        self.app = app

    def _load(self, skip, limit):
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

        blog_posts = []
        filenames = os.listdir(self.path)

        # Handle hidden files that may exist on Mac
        if '.DS_Store' in filenames:
            filenames.remove('.DS_Store')

        current = 1

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

            post = Post(post_id, text, meta, last_modified)

            # Cache this post to prevent doing this every time the post
            # is requested
            self._cache[post_id] = (post, time.time())

            blog_posts.append(post)
            current += 1

        blog_posts = sorted(blog_posts, key=lambda p: p['date'], reverse=True)

        if limit:
            posts = blog_posts[skip:skip+limit]
        else:
            posts = blog_posts

        return posts, len(blog_posts)


blog_manager = Blog()
