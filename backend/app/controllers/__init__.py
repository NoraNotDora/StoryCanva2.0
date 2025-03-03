# 导入所有控制器蓝图
from .user_controller import user_bp

# 导出所有蓝图列表，方便在应用程序初始化时注册
blueprints = [user_bp]
