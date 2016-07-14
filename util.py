import os
import codecs
from datetime import datetime


def construct_blog_posts(path):
    '''
        Adapted from Flask-Portfolio:
        https://github.com/longboardcat/Flask-Portfolio
    '''
    if not os.path.exists(path):
        return []

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

    post_id = 1

    for post in filenames:
        name = remove_extension(post, '.md')
        split_filename = post.split('-')

        post_info = {}
        date_string = '-'.join(split_filename[:5])
        post_info['date'] = datetime.strptime(date_string, '%Y-%m-%d-%H-%M')
        post_info['title'] = ''.join(name.split('-')[5:])
        post_info['id'] = construct_post_id(post_id)

        with codecs.open(path + post, 'r', encoding='utf-8') as f:
            post_info['text'] = f.read()

        blog_posts.append(post_info)
        post_id += 1

    return reversed(sorted(blog_posts, key=lambda p: p['date']))
