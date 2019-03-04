# 从app包，导入成员app对象,db数据库对象
from app import app, db

# 从models中导入用户、动态对象
from app.models import User, Post


# 装饰器将该函数注册为一个shell上下文函数，函数返回一个字典，
# 因为shell中使用的是提供的一个名称，然后加以调用
@app.shell_context_processor
def make_shell_content():
    return {'db': db, 'User': User, 'Post': Post}
