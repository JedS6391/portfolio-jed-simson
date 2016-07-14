from flask_wtf import Form, RecaptchaField
from wtforms import StringField, TextAreaField
from wtforms.validators import Required, Email
from wtforms.fields.html5 import EmailField


class ContactForm(Form):
    name = StringField('Name', validators=[Required()])
    email = EmailField('Email Address', validators=[Required(), Email()])
    message = TextAreaField('Message', validators=[Required()])
    recaptcha = RecaptchaField()
