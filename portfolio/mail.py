from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Content, Mail, To
from typing import Optional, Text

import logging

class Mailer:
    ''' Responsible for sending emails from the portfolio. '''

    def __init__(self):
        self.api_key: Optional[str] = None
        self.default_from: Optional[str] = None

    def initialise(self, api_key: str, default_from: str):
        ''' Initialises the mailer. '''
        self.api_key = api_key
        self.default_from = default_from

    def send_email(self, to: str, subject: str, content: Text):
        ''' Sends an email to the email address provided with the specified subject and content. '''
        message = self.create_message(to, subject, content)

        self.send_message(message)

    def send_message(self, message: Mail):
        ''' Sends an email message via SendGrid. ''' 
        sendgrid_client = SendGridAPIClient(self.api_key)

        try:            
            logging.debug('Sending email...')

            sendgrid_client.send(message)

            logging.debug('Email successfully sent')
        except Exception:
            logging.exception('Email failed to send.')            

    def create_message(self, to: str, subject: str, content: Text) -> Mail:
        ''' Creates an email message that can be sent via SendGrid. '''
        from_email = Email(self.default_from)
        to_email = To(to)
        content = Content('text/html', content)
        message = Mail(from_email, to_email, subject, content)

        return message

email_manager = Mailer()
