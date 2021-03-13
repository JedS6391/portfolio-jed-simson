from typing import Text
from flask import current_app as app
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail, To
import os

class Mailer(object):

    def __init__(self, api_key: str, default_from: str):
        self.api_key = api_key
        self.default_from = default_from

    def send_email(self, to: str, subject: str, template: Text) -> None:
        message = self.create_message(to, subject, template)

        self.send_message(message)

    def send_message(self, message: Mail):
        sendgrid_client = sendgrid.SendGridAPIClient(self.api_key)

        try:            
            app.logger.debug('Sending email...')

            sendgrid_client.send(message)

            app.logger.debug('Email successfully sent')
        except Exception as e:
            app.logger.exception('Email failed to send.')            

    def create_message(self, to: str, subject: str, template: Text) -> Mail:
        from_email = Email(self.default_from)
        to_email = To(to)
        content = Content('text/html', template)
        message = Mail(from_email, to_email, subject, content)

        return message

email_manager = Mailer(
    api_key=os.environ['SENDGRID_API_KEY'],
    default_from=os.environ['SENDGRID_DEFAULT_FROM']
)
