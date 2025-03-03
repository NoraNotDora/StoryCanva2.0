# 首先导入基础模块
from flask import Flask
from flask_cors import CORS

# 然后导入自定义模块
# 注意：如果models.py中导入了app，这里可能会导致循环导入
# 在这种情况下，应该在函数内部导入
__version__ = '1.0.0'

def get_models():
    from .models import db, User, Post, Comment
    return db, User, Post, Comment

def get_blueprints():
    from .controllers import blueprints
    return blueprints

# 导出所有应该在包级别可用的符号
__all__ = ['get_models', 'get_blueprints']
