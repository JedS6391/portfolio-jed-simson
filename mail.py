from flask import current_app
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail
import os

class Mailer(object):

    def __init__(self, api_key, default_from):
        self.api_key = api_key
        self.default_from = default_from

    def send_email(self, to, subject, template):
        message = self.create_message(to, subject, template)

        self.send_message(message)

    def send_message(self, message):
        sg = sendgrid.SendGridAPIClient(apikey=self.api_key)

        response = sg.client.mail.send.post(request_body=message.get())
        
        if response.status_code != 200:
            current_app.logger.error('Failed to send email')
            current_app.logger.error(response)
        else:
            current_app.logger.debug('Email sent')

    def create_message(self, to, subject, template):
        from_email = Email(self.default_from)
        to_email = Email(to)
        content = Content('text/html', template)
        message = Mail(from_email, subject, to_email, content)

        return message

email_manager = Mailer(
    api_key=os.environ['SENDGRID_API_KEY'],
    default_from=os.environ['SENDGRID_DEFAULT_FROM']
)
