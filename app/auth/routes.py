# 导入render_template
from flask import render_template, flash, redirect, url_for, \
    request, g
# 从app.form模块中导入LoginForm类,导入注册表单
from flask_login import current_user, login_user, login_required, \
    logout_user
from app.models import User, Post
# 设置登录认证，要求匿名用户必须登录后才能访问，用于保护某个视图
from werkzeug.urls import url_parse
from app import db
# 导入时间模块，我们需要记录最后一次用户请求操作时间
from app.auth import bp
from app.auth.form import ResetPasswordRequestForm, \
    ResetPasswordForm, LoginForm, RegistrationForm
from app.auth.email import send_password_reset_email

# 导入翻译模块
from flask_babel import _, get_locale

# 添加帖子发表识别语言
from guess_language import guess_language

# 装饰器：会修改跟在其后的函数，经常使用他们将函数注册为某些事件的回调函数


# Flask视图函数接受GET和POST请求，并且覆盖了默认的GET请求，因为HTTP协议规定GET请求需要返回信息给客户端（这里是浏览器）
# 之前的Method Not Allowed是由于没有允许POST请求，所以报错
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    # 生成一个表单实例
    form = LoginForm()
    # 执行Form校验工作，当浏览器发起GET请求，它会返回False，这样视图会直接跳过if块代码，直接转到最后一局渲染模板
    # 但是当点击Submit按钮的时候，浏览器会发起POST请求，然后验证生成的页面中，进行验证页面自定义验证（非空、长度等等）
    # 若每个字段都验证通过，则会继续执行下面语句，否则会直接跳到最后一句执行
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        # 处理登录后重定向问题
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)


# 用户登出装饰器
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# 注册页面
@bp.route('/register', methods=['GET', 'POST'])
def register():
    # 如果当前用户已经登录，则重定向到index
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/register.html', title=_('Register'), form=form)


# 重置密码请求（发送邮件）
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    重置密码
    """
    # 如果用户已经登录，那么重置密码没有意义，必须是非登录用户
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check you email for the instruction to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)


# 重置密码(来源邮箱)
@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # 查看当前用户是否已经登录
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    # 根据验证路径，查看是否存在相应的用户
    user = User.verify_reset_password_token(token)
    print(user.username)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
