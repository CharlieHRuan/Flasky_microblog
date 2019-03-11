# 导入render_template
from flask import render_template, flash, redirect, url_for
from app import app
# 从app.form模块中导入LoginForm类,导入注册表单
from app.form import LoginForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user
from app.models import User
# 设置用户登出函数
from flask_login import logout_user
# 设置登录认证，要求匿名用户必须登录后才能访问，用于保护某个视图
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db
# 导入时间模块，我们需要记录最后一次用户请求操作时间
from datetime import datetime

from app.form import PostForm, ResetPasswordRequestForm
from app.models import Post
from app.email import send_password_reset_email

from app.form import ResetPasswordForm


# 装饰器：会修改跟在其后的函数，经常使用他们将函数注册为某些事件的回调函数


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('You post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    # 如果下一页还有数据，那么next_url就有值
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    # 如果上一页还有数据，那么prev_url就有值
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    # 传入函数模板文件名，模板参数的变量列表，返回被渲染后的界面（被占位符替换后的结果）
    return render_template('index.html', title='Home',
                           form=form, posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)


# Flask视图函数接受GET和POST请求，并且覆盖了默认的GET请求，因为HTTP协议规定GET请求需要返回信息给客户端（这里是浏览器）
# 之前的Method Not Allowed是由于没有允许POST请求，所以报错
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # 生成一个表单实例
    form = LoginForm()
    # 执行Form校验工作，当浏览器发起GET请求，它会返回False，这样视图会直接跳过if块代码，直接转到最后一局渲染模板
    # 但是当点击Submit按钮的时候，浏览器会发起POST请求，然后验证生成的页面中，进行验证页面自定义验证（非空、长度等等）
    # 若每个字段都验证通过，则会继续执行下面语句，否则会直接跳到最后一句执行
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        # 处理登录后重定向问题
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


# 用户登出装饰器
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/about')
# 设置当前页面需要登录才能查看
@login_required
def about():
    return render_template('about.html')


# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    # 如果当前用户已经登录，则重定向到index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# 个人主页
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    # posts = [
    #     {'author': user, 'body': 'Test post #1'},
    #     {'author': user, 'body': 'Test post #2'}
    # ]
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


# 记录最后一次请求时间，每次请求之前调用该函数
@app.before_request
def before_request():
    if current_user.is_authenticated:
        # 使用国际化时间，不能使用当前系统时间
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# 编辑用户状态路由
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    # 如果当前方法返回True，则提交表单数据到数据库
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    # 这块代码主要是用与默认当前个人信息的，第一次进入当前界面
    # 会默认数据库中已有的数据，使用的GET请求
    # 如果提交表单出错，则代表POST提交，不执行
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


# 关注用户
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        # 未找到对应的用户
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        # 如果用户是当前用户
        flash('You cannot follow yourself!')
        print("关注成功跳转：", url_for('user', username=username))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


# 取关用户
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """
    取消关注用户路由
    """
    user = User.query.filter_by(username=username).first()
    print(user)
    if user is None:
        # 未找到当前用户
        flash('User {} not found.'.format(username))
        redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        print("取关成功跳转：", url_for('user', username=username))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}'.format(username))
    return redirect(url_for('user', username=username))


# 添加发现模块，让用户可以看到所有用户的动态
@app.route('/explore')
@login_required
def explore():
    """
    添加发现模块，让用户可以看到所有用户的动态
    """
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


# 重置密码
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    重置密码
    """
    # 如果用户已经登录，那么重置密码没有意义，必须是非登录用户
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check you email for the instruction to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Rqset Password', form=form)


# 重置密码
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # 查看当前用户是否已经登录
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # 根据验证路径，查看是否存在相应的用户
    user = User.verify_reset_password_token(token)
    print(user.username)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
