import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # 这个秘钥用于防止被跨域请求攻击（CSRF）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # 获取当前数据库位置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    # 设置数据发生变更之后是否发送信号给应用
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 设置邮件服务器配置
    # 服务器地址
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    # 端口号
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    # 服务器凭证默认不启用
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    # 用户名
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # 密码
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # 收到错误邮件的地址
    ADMINS = ['ruanheng1995@gmail.com']
    # 配置分页，每页的数据展示量
    POSTS_PER_PAGE = 25
