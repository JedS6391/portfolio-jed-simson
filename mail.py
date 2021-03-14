from typing import Optional, Text
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail, To
import logging

class Mailer(object):

    def __init__(self):
        self.api_key: Optional[str] = None
        self.default_from: Optional[str] = None

    def initialise(self, api_key: str, default_from: str):
        self.api_key = api_key
        self.default_from = default_from

    def send_email(self, to: str, subject: str, template: Text):
        message = self.create_message(to, subject, template)

        self.send_message(message)

    def send_message(self, message: Mail):
        sendgrid_client = sendgrid.SendGridAPIClient(self.api_key)

        try:            
            logging.debug('Sending email...')

            sendgrid_client.send(message)

            logging.debug('Email successfully sent')
        except Exception:
            logging.exception('Email failed to send.')            

    def create_message(self, to: str, subject: str, template: Text) -> Mail:
        from_email = Email(self.default_from)
        to_email = To(to)
        content = Content('text/html', template)
        message = Mail(from_email, to_email, subject, content)

        return message

email_manager = Mailer()
