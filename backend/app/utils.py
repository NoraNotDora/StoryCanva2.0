from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"检查登录状态: session={session}")
        if 'user_id' not in session:
            print("用户未登录，重定向到登录页面")
            flash('请先登录', 'error')
            return redirect(url_for('auth_bp.login'))
        print(f"用户已登录: user_id={session['user_id']}")
        return f(*args, **kwargs)
    return decorated_function 

def allowed_file(filename):
    """检查文件类型是否允许上传"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 