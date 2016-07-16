from flask import Blueprint, render_template, flash, redirect, url_for

import os

from .forms import ContactForm
from .helpers import Pagination
from mail import send_email
from util import construct_blog_posts

portfolio = Blueprint('portfolio', __name__)

CONTACT_EMAIL = os.environ['CONTACT_EMAIL']
PER_PAGE = int(os.environ.get('PER_PAGE', 10))


@portfolio.app_errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@portfolio.route('/')
@portfolio.route('/home/')
@portfolio.route('/index/')
def home():
    return render_template('home.html')


@portfolio.route('/blog/')
@portfolio.route('/blog/page/<int:page>/')
def blog(page=1):
    path = 'static/assets/posts/'

    # How far in are we?
    skip = (page - 1) * PER_PAGE

    # How many pages do we need?
    limit = PER_PAGE
    blog_posts, count = construct_blog_posts(path, skip, limit)
    pagination = Pagination(page, PER_PAGE, count)

    if not blog_posts and page != 1:
        return redirect(url_for('portfolio.blog'))

    return render_template('blog.html',
                           skip=skip,
                           blog_posts=blog_posts,
                           pagination=pagination)


@portfolio.route('/contact/', methods=['GET', 'POST'])
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
