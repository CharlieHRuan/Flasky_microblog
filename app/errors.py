# 展示错误界面给用户

from flask import render_template
from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


# 当应用程序引发数据库的错误调用后，触发
@app.errorhandler(500)
def internal_error(error):
    # 防止操作失败的数据库会话影响其他会话，将当前数据库会话重置为干净状态
    db.session.rollback()
    return render_template('500.html'), 500
