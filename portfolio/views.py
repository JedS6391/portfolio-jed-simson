from flask import Blueprint, render_template, request, flash, redirect, url_for

import os

from .forms import ContactForm
from mail import send_email
from util import construct_blog_posts

portfolio = Blueprint('portfolio', __name__)

CONTACT_EMAIL = os.environ['CONTACT_EMAIL']


@portfolio.route('/')
@portfolio.route('/home/')
@portfolio.route('/index/')
@portfolio.route('/index.html')
def home():
    return render_template('home.html')


@portfolio.route('/blog/', defaults={'page': 1})
@portfolio.route('/blog.html', defaults={'page': 1})
@portfolio.route('/blog/page/<int:page>/')
def blog(page):
    path = 'static/assets/posts/'
    return render_template('blog.html', blog_posts=construct_blog_posts(path))


@portfolio.route('/contact/', methods=['GET', 'POST'])
@portfolio.route('/contact.html', methods=['GET', 'POST'])
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

    return render_template('contact.html', form=form, errors=form.errors.keys())
