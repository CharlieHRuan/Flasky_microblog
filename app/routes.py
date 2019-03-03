# 导入render_template
from flask import render_template, flash, redirect, url_for
from app import app
# 从app.form模块中导入LoginForm类
from app.form import LoginForm
# 装饰器：会修改跟在其后的函数，经常使用他们将函数注册为某些事件的回调函数


@app.route('/')
@app.route('/index')
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
    return render_template('index.html', title='Home', user=user, posts=posts)


# Flask视图函数接受GET和POST请求，并且覆盖了默认的GET请求，因为HTTP协议规定GET请求需要返回信息给客户端（这里是浏览器）
# 之前的Method Not Allowed是由于没有允许POST请求，所以报错
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 生成一个实例
    form = LoginForm()
    # 执行Form校验工作，当浏览器发起GET请求，它会返回False，这样视图会直接跳过if块代码，直接转到最后一局渲染模板
    # 但是当点击Submit按钮的时候，浏览器会发起POST请求，然后验证生成的页面中，进行验证页面自定义验证（非空、长度等等）
    # 若每个字段都验证通过，则会继续执行下面语句，否则会直接跳到最后一句执行
    if form.validate_on_submit():
        # 闪现消息，对用户进行提示
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        # 重定向页面到主页
        return redirect(url_for('index'))
    # form = form
    # 当前引用变量 = 传入模板的form实例
    return render_template('login.html', title='Sign In', form=form)
