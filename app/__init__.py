from flask import Flask
# 从config模块中导入Config类
from config import Config
# 导入数据库插件
from flask_sqlalchemy import SQLAlchemy
# 导入数据库迁移引擎
from flask_migrate import Migrate

# 代表当前app实例
app = Flask(__name__)
# Flask需要读取配置并使用
app.config.from_object(Config)
# 声明一个对象来表示数据库
db = SQLAlchemy(app)
# 添加数据库迁移引擎
migrate = Migrate(app, db)


from app import routes, models 
