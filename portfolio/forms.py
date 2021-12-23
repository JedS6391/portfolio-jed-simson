from flask_wtf import FlaskForm, RecaptchaField
from wtforms.fields import EmailField, StringField, TextAreaField
from wtforms.validators import InputRequired, Email

class ContactForm(FlaskForm):
    ''' Form used on the /contact/ route for sending a message to the appropriate contact email. '''

    name = StringField('Name', validators=[InputRequired()])
    email = EmailField('Email Address', validators=[InputRequired(), Email()])
    message = TextAreaField('Message', validators=[InputRequired()])
    recaptcha = RecaptchaField()
