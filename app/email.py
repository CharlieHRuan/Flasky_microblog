from threading import Thread
from flask_mail import Message
from app import mail
from flask import render_template
from app import app


def send_async_email(app, msg):
    """异步发送电子邮件"""
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    """
    发送邮件
    """
    # 创建消息对象，传入主题、发送人、接收人
    msg = Message(subject, sender=sender, recipients=recipients)
    # 创建邮件主体
    msg.body = text_body
    # 创建html主体
    msg.html = html_body
    # 发送邮件
    # mail.send(msg)
    # 异步发送
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    """
    发送重置密码邮件
    """
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
