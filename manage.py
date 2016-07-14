from flask_script import Manager
from app import create_app

from util import construct_blog_posts

app = create_app()

manager = Manager(app)

blog = Manager(usage='Manage Blog posts')
manager.add_command('blog', blog)


@blog.command
def list():
    for post in construct_blog_posts('static/assets/posts/'):
        print('<ID: {}, Title: {}, Date: {}>'
              .format(post['id'], post['title'], post['date']))

if __name__ == '__main__':
    manager.run()
