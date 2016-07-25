import os
from datetime import datetime
import time
import string
import re

from portfolio.models import Post


def count_words(text):
    html_tags = re.compile('<.*?>')
    text = re.sub(html_tags, '', text)

    punctuation = re.compile('[{}]'.format(re.escape(string.punctuation)))
    text = punctuation.sub(' ', text)
    words = text.split()

    return len(words)


def construct_blog_posts(path, skip, limit):
    '''
        Adapted from Flask-Portfolio:
        https://github.com/longboardcat/Flask-Portfolio

        TODO: Refactor so that Post objects are created and possibly
              cache metadata for posts
    '''
    if not os.path.exists(path):
        return [], 0

    def remove_extension(title, extension):
        return title.replace(extension, '')

    def construct_post_id(counter):
        return 'blog_post_' + str(counter)

    blog_posts = []
    filenames = os.listdir(path)

    # Handle hidden files that may exist
    # on Mac
    if '.DS_Store' in filenames:
        filenames.remove('.DS_Store')

    current = 1

    for file in filenames:
        name = remove_extension(file, '.md')
        split_filename = file.split('-')
        date_string = '-'.join(split_filename[:3])
        st = os.stat(path + file)
        last_modified = time.ctime(st.st_mtime)
        meta = {}

        post_id = construct_post_id(current)
        meta['title'] = ''.join(name.split('-')[3:])
        meta['date'] = datetime.strptime(date_string, '%Y-%m-%d')
        meta['filename'] = file
        meta['filesize'] = st.st_size

        with open(path + file, 'r', encoding='utf-8') as f:
            text = f.read()
            meta['words'] = count_words(text)

        post = Post(post_id, text, meta, last_modified)

        blog_posts.append(post)
        current += 1

    blog_posts = sorted(blog_posts, key=lambda p: p['date'], reverse=True)

    if limit:
        posts = blog_posts[skip:skip+limit]
    else:
        posts = blog_posts

    return posts, len(blog_posts)
