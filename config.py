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

