from app import db


class User(db.Model):
    # User类继承自db.Model基类
    # db.Column()传入字段类型，字段可索引（对数据检索很重要），字段唯一
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        """
        repr 用于调试的时候，打印用户实例，表示操作成功
        >>> from app.models import User
        >>> u = User(username='susan',email='susan@example.com')
        >>> u
        <User susan>
        """
        return "<User {}>".format(self.username)
