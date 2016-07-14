from flask import Blueprint, render_template

from .forms import ContactForm

portfolio = Blueprint('portfolio', __name__)


@portfolio.route('/')
@portfolio.route('/home/')
@portfolio.route('/index/')
@portfolio.route('/index.html')
def home():
    return render_template('home.html')


@portfolio.route('/contact/')
def contact():
    form = ContactForm()

    return render_template('contact.html', form=form)
