from flask import render_template, flash, redirect, url_for, \
    request, g
from app import app
from app.main.forms import PostForm, EditProfileForm
from flask_login import login_required, current_user
from app.models import User, Post
from werkzeug.urls import url_parse
from app import db
from app.main import bp
from datetime import datetime
from flask_babel import _, get_locale
from guess_language import guess_language


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        # 识别当前发表动态的语言类别，如果检测为未知，或者意想不到的长字符串结果
        # 则将当前语言设置为未知（即空字符串）
        language = guess_language(form.post.data)
        if language == "UNKNOWN" or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('You post is now live!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    # 如果下一页还有数据，那么next_url就有值
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    # 如果上一页还有数据，那么prev_url就有值
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    # 传入函数模板文件名，模板参数的变量列表，返回被渲染后的界面（被占位符替换后的结果）
    return render_template('index.html', title=_('Home'),
                           form=form, posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/about')
# 设置当前页面需要登录才能查看
@login_required
def about():
    return render_template('about.html')


# 个人主页
@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    # posts = [
    #     {'author': user, 'body': 'Test post #1'},
    #     {'author': user, 'body': 'Test post #2'}
    # ]
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


# 记录最后一次请求时间，每次请求之前调用该函数
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        # 使用国际化时间，不能使用当前系统时间
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


# 编辑用户状态路由
@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    # 如果当前方法返回True，则提交表单数据到数据库
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    # 这块代码主要是用与默认当前个人信息的，第一次进入当前界面
    # 会默认数据库中已有的数据，使用的GET请求
    # 如果提交表单出错，则代表POST提交，不执行
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


# 关注用户
@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        # 未找到对应的用户
        # flash('User {} not found.'.format(username))
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        # 如果用户是当前用户
        flash(_('You cannot follow yourself!'))
        print("关注成功跳转：", url_for('main.user', username=username))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    # flash('You are following {}!'.format(username))
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


# 取关用户
@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """
    取消关注用户路由
    """
    user = User.query.filter_by(username=username).first()
    print(user)
    if user is None:
        # 未找到当前用户
        flash(_('User %(username)s not found.', username=username))
        # flash('User {} not found.'.format(username))
        redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        # print("取关成功跳转：", url_for('user', username=username))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s', username=username))
    return redirect(url_for('main.user', username=username))


# 添加发现模块，让用户可以看到所有用户的动态
@bp.route('/explore')
@login_required
def explore():
    """
    添加发现模块，让用户可以看到所有用户的动态
    """
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'), posts=posts.items,
                           next_url=next_url, prev_url=prev_url)
