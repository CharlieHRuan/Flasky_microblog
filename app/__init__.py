# 导入日志包
import logging
# 启用邮件记录器，本地基于文件的日志记录器
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import request

from flask import Flask, request
# 从config模块中导入Config类
from config import Config
# 导入数据库插件
from flask_sqlalchemy import SQLAlchemy
# 导入数据库迁移引擎
from flask_migrate import Migrate
# 添加应用登录插件
from flask_login import LoginManager
# 添加邮件发送功能
from flask_mail import Mail
# 添加FLask-Bootstrap框架
from flask_bootstrap import Bootstrap
# 导入Moment包，以便处理本地化时间
from flask_moment import Moment
# 导入Babel，用于翻译
from flask_babel import Babel, lazy_gettext as _l

# 代表当前app实例
app = Flask(__name__)
# Flask需要读取配置并使用
app.config.from_object(Config)
# 声明一个对象来表示数据库
db = SQLAlchemy(app)
# 添加数据库迁移引擎
migrate = Migrate(app, db)
# 添加登录对象
login = LoginManager(app)
# 设置login用于处理登录验证，以便需要用户登录查看的界面，必须登录后才能查看
login.login_view = 'login'
login.login_message = _l('Please log in to access this page')
# 添加邮件发送实例
mail = Mail(app)
# 添加Bootstrap实例
bootstrap = Bootstrap(app)
# 实例化Moment
moment = Moment(app)
# 实例化翻译插件
babel = Babel(app)


# 仅当应用的DEBUG模式未开启的时候，我们才执行发送邮件
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='MicroBlog Failure',
            credentials=auth, secure=secure)
        # 设置级别为严重级别，只报告错误信息
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        # 创建一个日志文件夹保存日志文件
        if not os.path.exists('logs'):
            os.mkdir('logs')
        # 确保创建文件单个大小在10kb，并只保留最后10个文件作为备份
        file_handler = RotatingFileHandler(
            'logs/microblog.log', maxBytes=10240, backupCount=10)
        # 设置日志文件格式
        # 时间戳、错误级别、信息、日志来源的源代码文件、行号
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        # 设置日志级别，什么等级的信息，才记录在日志文件中，这里选用INFO级别
        # 级别递增
        # DEBUG、INFO、WARNING、ERROR、CRITICAL
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        # 服务器每次启动的时候，都会写入一行表示服务器启动
        app.logger.info('Microblog startup')


# 选择最匹配的语言
@babel.localeselector
def get_locale():
    # return request.accept_languages.best_match(app.config['LANGUAGES'])
    # 强制选择相应语言展示翻译结果
    # return 'es'
    return 'zh'


from app import routes, models, errors
