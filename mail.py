import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail
import threading
import os

class Mail(object):

    def __init__(self, api_key, default_from):
        self.api_key = api_key
        self.default_from = default_from

    def send_email(self, to, subject, template):
        sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
        message = self.create_message(to, subject, template)

        def send_message(message):
            response = sg.client.mail.send.post(request_body=message.get())

            print('Email response status: {}'.format(response.status_code))
            return response.status_code == 200

        sender = threading.Thread(name='mail_sender',
                                  target=send_message,
                                  args=(message,))
        sender.start()

    def create_message(self, to, subject, template):
        from_email = Email(self.default_from)
        to_email = Email(to)
        content = Content('text/html', template)
        message = Mail(from_email, subject, to_email, content)

        return message

email_manager = Mail(
    api_key=os.environ['SENDGRID_API_KEY'],
    default_from=os.environ['SENDGRID_DEFAULT_FROM']
)
