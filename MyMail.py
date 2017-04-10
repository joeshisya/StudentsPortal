from flask import flash
from flask_mail import Message


def send_mail(mail, message_body):
    try:
        message = Message("Password Reset Request",
                          sender="ljshisya@gmail.com",
                          recipients=["ljshisya@gmail.com"])
        message.body = message_body
        mail.send(message)

        return True

    except Exception as e:
        flash(e)
        return False
