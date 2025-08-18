from albumy.extensions import mail
from flask_mail import Message
from flask import render_template, current_app
from threading import Thread


def _send_async_email(app, message):
    try:
        with app.app_context():
            mail.send(message)
            print('邮件发送成功')
    except Exception as e:
        print(f"错误描述：{e}")


def send_email(subject, to, template, **kwargs):
    message = Message(subject=subject, recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.body = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()
    thr = Thread(target=_send_async_email, args=[app, message])
    thr.start()
    return thr


def send_confirm_email(user, token, to=None):
    send_email(subject='Confirm Email', to=to or user.email, template='emails/confirm', user=user, token=token)
