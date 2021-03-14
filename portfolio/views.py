import os

from flask import (
    Blueprint, 
    render_template, 
    flash, 
    redirect, 
    url_for, 
    abort,
    send_from_directory,
    current_app as app
)

from .forms import ContactForm
from .helpers import Pagination
from blog import blog_manager
from mail import email_manager

portfolio = Blueprint('portfolio', __name__)

@portfolio.app_errorhandler(404)
def page_not_found(error):
    ''' Renders a 404 error page. '''
    return render_template('errors/404.html'), 404

@portfolio.route('/.well-known/acme-challenge/mApkXLQFWzmY1klfIKc0a3cwZZhNMoiUwlqKoFWpfYU')
def acme_challenge_portfolio():
    # To support Let's Encrypt verification
    return 'mApkXLQFWzmY1klfIKc0a3cwZZhNMoiUwlqKoFWpfYU.K2tT6yEn2xKfamcfv_y2hTXLbRbp3qeaqp6AC0yItFE'

@portfolio.route('/.well-known/acme-challenge/aCdATJ7Fe28t2tesajUoprKARyPnKOG7fbkvp_uYhs0')
def acme_challenge_www():
    # To support Let's Encrypt verification
    return 'aCdATJ7Fe28t2tesajUoprKARyPnKOG7fbkvp_uYhs0.K2tT6yEn2xKfamcfv_y2hTXLbRbp3qeaqp6AC0yItFE'

@portfolio.route('/keybase.txt')
def keybase():
    # To support Keybase verification
    return send_from_directory('static/', 'keybase.txt')

@portfolio.route('/')
@portfolio.route('/home/')
@portfolio.route('/index/')
def home():
    ''' Renders the home page. '''
    return render_template('home.html')

@portfolio.route('/about/')
def about():
    ''' Renders the about page. '''
    return render_template('about.html')

@portfolio.route('/blog/')
@portfolio.route('/blog/page/<int:page>/')
def blog(page=1):
    ''' Renders the main blog list page. '''
    # Here, we handle two different routes: 
    #   1. '/blog/': we render page 1 of the posts. 
    #   2. '/blog/page/<int:page>/': we render the posts for the specific page.
    
    posts_per_page = app.config['POSTS_PER_PAGE']
    skip = (page - 1) * posts_per_page

    limit = posts_per_page
    blog_posts, count = blog_manager.get_range(skip, limit)
    pagination = Pagination(page, posts_per_page, count)

    # If we're asked for a page that doesn't actually exist just redirect back to the main blog page.
    if not blog_posts and page != 1:
        return redirect(url_for('portfolio.blog'))

    return render_template('blog.html',
                           skip=skip,
                           blog_posts=blog_posts,
                           pagination=pagination)

@portfolio.route('/blog/<year>/<month>/<day>/<slug>')
def blog_post(year, month, day, slug):
    ''' Renders the blog post page. '''
    key = '{}/{}/{}/{}'.format(year, month, day, slug)

    try:    
        post = blog_manager.get(key)

        return render_template('blog_post.html', post=post)
    except KeyError:
        # If we get a key error, then we're probably getting an invalid request.
        abort(404)

@portfolio.route('/blog/tag/<tag>/')
def blog_by_tag(tag):
    ''' Renders the blog list page, with the posts filtered by the specified tag. '''
    filtered_posts = blog_manager.get_with_tag(tag.lower())

    # Note we don't 404 if there are no matching posts - it just means there 
    # will be no posts to render on the page.
    return render_template('blog_by_tag.html',
                           posts=filtered_posts,
                           tag=tag.lower())

@portfolio.route('/contact/', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        name = str(form.name.data)
        email = str(form.email.data)
        message = str(form.message.data)

        # The email content is rendered as HTML.
        html = render_template('email/message.html',
                               name=name,
                               email=email,
                               message=message)

        subject = 'New message from {} [{}] | Portfolio'.format(name, email)

        email_manager.send_email(app.config['CONTACT_EMAIL'], subject, html)

        flash('Your message has made its way to my inbox. I will try to respond promptly!')
        
        return redirect(url_for('portfolio.contact'))

    # Something invalid was provided. Let the user try again with the error information.
    return render_template('contact.html',
                           form=form,
                           errors=form.errors.keys())
