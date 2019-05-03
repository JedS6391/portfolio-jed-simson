import os

from flask import (
    Blueprint, 
    render_template, 
    flash, 
    redirect, 
    url_for, 
    abort,
    send_from_directory
)

from .forms import ContactForm
from .helpers import Pagination
from blog import blog_manager
from mail import email_manager
from cache import cache

portfolio = Blueprint('portfolio', __name__)

CONTACT_EMAIL = os.environ['CONTACT_EMAIL']
PER_PAGE = int(os.environ.get('PER_PAGE', 10))
DEFAULT_CACHE_CONTROL_TIME = 21600    # 6 hours


@portfolio.app_errorhandler(404)
def page_not_found(error):
    # Nice to have a custom 404 error handler.
    return render_template('errors/404.html'), 404

@portfolio.route('/.well-known/acme-challenge/mApkXLQFWzmY1klfIKc0a3cwZZhNMoiUwlqKoFWpfYU')
def acme_challenge_portfolio():
    return 'mApkXLQFWzmY1klfIKc0a3cwZZhNMoiUwlqKoFWpfYU.K2tT6yEn2xKfamcfv_y2hTXLbRbp3qeaqp6AC0yItFE'

@portfolio.route('/.well-known/acme-challenge/aCdATJ7Fe28t2tesajUoprKARyPnKOG7fbkvp_uYhs0')
def acme_challenge_www():
    return 'aCdATJ7Fe28t2tesajUoprKARyPnKOG7fbkvp_uYhs0.K2tT6yEn2xKfamcfv_y2hTXLbRbp3qeaqp6AC0yItFE'

@portfolio.route('/keybase.txt')
def keybase():
    # Let's keybase verify my domain actually belongs to me.
    return send_from_directory('static/', 'keybase.txt')

@portfolio.route('/')
@portfolio.route('/home/')
@portfolio.route('/index/')
@cache.cached(timeout=DEFAULT_CACHE_CONTROL_TIME)
def home():
    return render_template('home.html')

@portfolio.route('/about/')
@cache.cached(timeout=DEFAULT_CACHE_CONTROL_TIME)
def about():
    return render_template('about.html')

@portfolio.route('/blog/')
@portfolio.route('/blog/page/<int:page>/')
@cache.cached(timeout=DEFAULT_CACHE_CONTROL_TIME)
def blog(page=1):
    # Here, we handle two different routes: if the default /blog/
    # view is being accessed, where essentially rendering page 1
    # of the posts. Alternatively, if a page is specified, we
    # need to retrieve the posts for that page.

    # How far in are we?
    skip = (page - 1) * PER_PAGE

    # How many pages do we need?
    limit = PER_PAGE
    blog_posts, count = blog_manager.get_range(skip, limit)
    pagination = Pagination(page, PER_PAGE, count)

    # Handle the case where we're asked for a page that doesn't
    # actually exist because there are not enough posts to warrant
    # that number of pages.
    if not blog_posts and page != 1:
        return redirect(url_for('portfolio.blog'))

    return render_template('blog.html',
                           skip=skip,
                           blog_posts=blog_posts,
                           pagination=pagination)

@portfolio.route('/blog/<year>/<month>/<day>/<slug>')
@cache.cached(timeout=DEFAULT_CACHE_CONTROL_TIME)
def blog_post(year, month, day, slug):
    # Reconstruct key for the given post, so we can render just that post.
    key = '{}/{}/{}/{}'.format(year, month, day, slug)

    try:
        # Let the manager worry about getting the correct post.
        # If we get a key error, then we're probably getting an invalid request.
        post = blog_manager.get(key)

        return render_template('blog_post.html', post=post)
    except KeyError:
        # No post found... redirect to the 404 page.
        abort(404)

@portfolio.route('/blog/tag/<tag>/')
@cache.cached(timeout=DEFAULT_CACHE_CONTROL_TIME)
def blog_by_tag(tag):
    filtered_posts = blog_manager.get_with_tag(tag.lower())

    # We don't 404 if there are no matching posts -- it doesn't really make sense as the
    # page for showing matching posts exists, there is just no data to present.
    # Instead, we inform the user that there are no matching posts in the template.
    return render_template('blog_by_tag.html',
                           posts=filtered_posts,
                           tag=tag.lower())

@portfolio.route('/contact/', methods=['GET', 'POST'])
@cache.cached(timeout=DEFAULT_CACHE_CONTROL_TIME)
def contact():
    form = ContactForm()

    # Check that the information provided is alright.
    if form.validate_on_submit():
        name = str(form.name.data)
        email = str(form.email.data)
        message = str(form.message.data)

        # Build our email
        html = render_template('email/message.html',
                               name=name,
                               email=email,
                               message=message)

        subject = 'New message from {} <{}> | Portfolio'.format(name, email)

        email_manager.send_email(CONTACT_EMAIL, subject, html)

        flash('Your message has made its way to my inbox &mdash; ' +
              'I will try to respond promptly!')

        # Send the user back to the contact page so they can see the message.
        return redirect(url_for('portfolio.contact'))

    # Something invalid was provided -- let the user try again with the error information.
    return render_template('contact.html',
                           form=form,
                           errors=form.errors.keys())
