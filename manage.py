from flask_script import Manager
from app import create_app

from util import construct_blog_posts

BLOG_PATH = 'static/assets/posts/'

app = create_app()

manager = Manager(app)

blog = Manager(usage='Manage Blog posts')
manager.add_command('blog', blog)


@blog.command
def list():
    posts, count = construct_blog_posts(BLOG_PATH, 0, None)

    print('{} post(s) found in {} (sorted newest to oldest).\n'
          .format(count, BLOG_PATH))

    for count, post in enumerate(posts, 1):
        print('{}:\t<ID: {}, Title: {}, Date: {}, Words: {}, Modified: {}>'
              .format(count, post.id, post['title'],
                      post['date'].strftime('%a, %d %b %Y'),
                      post['words'],
                      post.last_modified))


if __name__ == '__main__':
    manager.run()
