from flask import Blueprint, render_template, flash, redirect, url_for, abort, jsonify
from flask_cachecontrol import (cache, cache_for, dont_cache)

import os

from .forms import ContactForm
from .helpers import Pagination
from blog import blog_manager
from mail import send_email


portfolio = Blueprint('portfolio', __name__)

CONTACT_EMAIL = os.environ['CONTACT_EMAIL']
PER_PAGE = int(os.environ.get('PER_PAGE', 10))
DEFAULT_CACHE_CONTROL_TIME = 21600    # 6 hours


@portfolio.app_errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@portfolio.route('/')
@portfolio.route('/home/')
@portfolio.route('/index/')
@cache(max_age=DEFAULT_CACHE_CONTROL_TIME, public=True)
def home():
    return render_template('home.html')


@portfolio.route('/about/')
@cache(max_age=DEFAULT_CACHE_CONTROL_TIME, public=True)
def about():
    return render_template('about.html')


@portfolio.route('/blog/')
@portfolio.route('/blog/page/<int:page>/')
@cache(max_age=10800, public=True)
def blog(page=1):
    # How far in are we?
    skip = (page - 1) * PER_PAGE

    # How many pages do we need?
    limit = PER_PAGE
    blog_posts, count = blog_manager.get(skip, limit)
    pagination = Pagination(page, PER_PAGE, count)

    if not blog_posts and page != 1:
        return redirect(url_for('portfolio.blog'))

    return render_template('blog.html',
                           skip=skip,
                           blog_posts=blog_posts,
                           pagination=pagination)


@portfolio.route('/blog/<int:post>/')
@cache(max_age=10800, public=True)
def blog_post(post):
    # Ensure that post number is greater than 0
    if post <= 0:
        abort(404)

    # Constructing blog posts with no limit/skip retreives all posts
    # ordered newest to oldest. We index the posts by the post
    # number given. The contract is that lower indices reference
    # newer posts, i.e. posts[1] is more recent than posts[2], etc.
    blog_posts, count = blog_manager.get(0, None)

    try:
        post = blog_posts[post-1]

        return render_template('blog_post.html',
                               post=post)
    except IndexError:
        # No post found... redirect to the 404 page
        abort(404)


@portfolio.route('/blog/tag/<tag>/')
@cache(max_age=10800, public=True)
def blog_by_tag(tag):
    blog_posts, _ = blog_manager.get_with_tag(tag.lower())

    if blog_posts:
        return render_template('blog_by_tag.html',
                               posts=blog_posts,
                               tag=tag.lower())
        #return jsonify([post.__dict__ for post in blog_posts])

    abort(404)

@portfolio.route('/contact/', methods=['GET', 'POST'])
@cache(max_age=DEFAULT_CACHE_CONTROL_TIME, public=True)
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        name = str(form.name.data)
        email = str(form.email.data)
        message = str(form.message.data)

        html = render_template('email/message.html',
                               name=name,
                               email=email,
                               message=message)
        subject = 'New message from {} <{}> | Portfolio'.format(name, email)

        send_email(CONTACT_EMAIL, subject, html)

        flash('Your message was successfully sent.<br> I will try to' +
              ' respond promptly!')

        return redirect(url_for('portfolio.contact'))

    return render_template('contact.html',
                           form=form,
                           errors=form.errors.keys())
