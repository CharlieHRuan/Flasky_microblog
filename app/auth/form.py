from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from wtforms.validators import Length
from flask_babel import _, lazy_gettext as _l
from app.models import User


class LoginForm(FlaskForm):
    # 用户名，validator用于验证输入是否符合预期，DateRequired用于验证输入是否为空
    username = StringField(_l('Username'), validators=[DataRequired()])
    # 密码
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    # 记住我
    remember_me = BooleanField(_l('Remember me'))
    # 提交按钮
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    """注册视图"""
    username = StringField(_l('Username'), validators=[DataRequired()])
    # Email() 确保在当前字段中键入内容与电子邮件地址结构匹配
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    # 需要用户输入两次确认密码，减少错误风险
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    # 确认与Password输入内容相同
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        """
        验证是否有相同名称的用户，如果存在，则不予创建
        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))

    def validate_email(slef, email):
        """
        验证是否存在相同邮件地址，如有存在，不予创建
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different email address.'))


class ResetPasswordRequestForm(FlaskForm):
    """
    重置密码表单
    """
    email = StringField(_l('Email'), validators=[DataRequired(),  Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    """
    重置密码视图
    """
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'),
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))
