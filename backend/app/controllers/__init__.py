from .user_controller import user_bp
from .auth_controller import auth_bp
from .api_controller import api_bp
from .main_controller import main_bp
from .post_controller import post_bp

# 导出所有蓝图列表，方便在应用程序初始化时注册
blueprints = [
    (user_bp, '/api'),      # 用户相关 API
    (auth_bp, '/auth'),     # 认证相关路由和API
    (api_bp, '/api'),       # 其他通用 API
    (main_bp, '/'),         # 主页面路由
    (post_bp, '/')          # 帖子和评论相关路由
]