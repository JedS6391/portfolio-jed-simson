import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail
import threading
import os

API_KEY = os.environ['SENDGRID_API_KEY']
DEFAULT_FROM = os.environ['SENDGRID_DEFAULT_FROM']


def send_email(to, subject, template):
    sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
    message = create_message(to, subject, template)

    def send_message(message):
        response = sg.client.mail.send.post(request_body=message.get())

        print('Email response status: {}'.format(response.status_code))
        return response.status_code == 200

    sender = threading.Thread(name='mail_sender',
                              target=send_message,
                              args=(message,))
    sender.start()


def create_message(to, subject, template):
    from_email = Email(DEFAULT_FROM)
    to_email = Email(to)
    content = Content('text/html', template)
    message = Mail(from_email, subject, to_email, content)

    return message
