from flask_mail import Message
from twilio.rest import Client

from private import settings


def send_email(mail, message_subject, message_body):
    try:
        message = Message(message_subject,
                          sender=settings.mail_username,
                          recipients=[settings.email_to])
        message.body = message_body
        mail.send(message)

        return True

    except Exception as e:
        return False


def send_sms(message_body):
    try:
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

        message = client.messages.create(
            to=settings.twilio_to,
            from_=settings.twilio_from,
            body=message_body)

        return True

    except Exception as e:
        return False