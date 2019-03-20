from hashlib import md5
from datetime import datetime
from app import db
from app import login
# 导入哈希密码生成、验证函数
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from time import time
import jwt
from app import current_app
from app.search import add_to_index, query_index, remove_from_index

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        """
        将查询返回的动态ID，以及查询到的总数，重新组装数据
        返回 查询到的模型，查询到的总数
        """
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        """提交前处理数据"""
        session._changes = {
            'add': [obj for obj in session.new if isinstance(obj, cls)],
            'update': [obj for obj in session.dirty if isinstance(obj, cls)],
            'delete': [obj for obj in session.deleted if isinstance(obj, cls)]
        }

    @classmethod
    def after_commit(cls, session):
        """提交后处理数据"""
        for obj in session._changes['add']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['update']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['delete']:
            remove_from_index(cls.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        """
        重新将所有索引对象添加到Elasticsearch，功能类似于刷新，
        因为ID只要一致，那么数据源发生改变，索引名称不便，则会改变数据中的值
        """
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


class User(UserMixin, db.Model):
    # User类继承自db.Model基类
    # db.Column()传入字段类型，字段可索引（对数据检索很重要），字段唯一
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # 这不是实际的数据库字段，而是用户和其动态关系的高级师徒，因此它不在表中
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # 丰富个人主页信息
    # 添加个人介绍，个人最后访问时间
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """
        repr 用于调试的时候，打印用户实例，表示操作成功
        >>> from app.models import User
        >>> u = User(username='susan',email='susan@example.com')
        >>> u
        <User susan>
        """
        return "<User {}>".format(self.username)

    # 添加生成密码、验证密码函数
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 用户加载函数
    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def avatar(self, size):
        """
        生成随机图片
        """
        # 根据用户邮箱，生成md5哈希值，如果是没有注册的用户，则自动根据邮箱的哈希值生成随机头像
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size
        )

    # 声明用户的多对多关系
    # 代表左侧用户（followed）关注右侧用户（follower）
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    # 添加、删除关注关系
    def follow(self, user):
        """
        关注某用户
        """
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """
        取消关注某用户
        """
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        """
        判断当前用户是否已关注传入参数的这个用户
        """
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """
        查询自身动态，以及关注用户的动态，合并到一块展示,按照最新发布时间排序
        """
        # 查询当前用户已关注用户的动态
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        # 查询自身动态
        own = Post.query.filter_by(user_id=self.id)
        # 使用union将二者查询出的数据合并到一块返回，按照动态发布时间排序
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expire_in=600):
        """
        生成重置密码令牌
        """
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expire_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    # 静态方法，可以直接在类中调用
    @staticmethod
    def verify_reset_password_token(token):
        """
        验证重置密码令牌
        """
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Post(SearchableMixin, db.Model):
    """
    用户发表状态
    """
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    # 默认一个用户发表状态的时间，utcnow表示函数本身，而不是其返回值
    # 在服务器中使用当前时间，可以根据用户所在位置获取当前时间
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # 设置外键，引用user表的主键，
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "<Post {}>".format(self.body)

    # 在用户提交的时候，确认当前发布的语言属于哪种
    language = db.Column(db.String(5))


db.event.listen(db.session, 'before_commit', Post.before_commit)
db.event.listen(db.session, 'after_commit', Post.after_commit)
