from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextAreaField
from wtforms.validators import Required, Email
from wtforms.fields.html5 import EmailField

class ContactForm(FlaskForm):
    ''' Form used on the /contact/ route for sending a message to the appropriate contact email. '''

    name = StringField('Name', validators=[Required()])
    email = EmailField('Email Address', validators=[Required(), Email()])
    message = TextAreaField('Message', validators=[Required()])
    recaptcha = RecaptchaField()
