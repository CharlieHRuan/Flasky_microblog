from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    # 用户名，validator用于验证输入是否符合预期，DateRequired用于验证输入是否为空
    username = StringField('Username', validators=[DataRequired()])
    # 密码
    password = PasswordField('Password', validators=[DataRequired()])
    # 记住我
    remember_me = BooleanField('Remember me')
    # 提交按钮
    submit = SubmitField('Sign In')
