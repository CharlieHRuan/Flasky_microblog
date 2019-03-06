# 导入render_template
from flask import render_template, flash, redirect, url_for
from app import app
# 从app.form模块中导入LoginForm类
from app.form import LoginForm
from flask_login import current_user, login_user
from app.models import User
# 设置用户登出函数
from flask_login import logout_user
# 设置登录认证，要求匿名用户必须登录后才能访问，用于保护某个视图
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse

# 装饰器：会修改跟在其后的函数，经常使用他们将函数注册为某些事件的回调函数


@app.route('/')
@app.route('/index')
# 设置当前页面需要登录才能查看
def index():
    user = {'username': 'RuanHeng'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The avengers movie was so cool!'
        }
    ]
    # 传入函数模板文件名，模板参数的变量列表，返回被渲染后的界面（被占位符替换后的结果）
    return render_template('index.html', title='Home', posts=posts)


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
        print("====url_for：====", url_for(next_page))
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


# 用户登出装饰器
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/about')
@login_required
def about():
    return render_template('about.html')
