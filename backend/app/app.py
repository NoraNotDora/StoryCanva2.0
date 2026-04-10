from flask import Flask
from flask_cors import CORS
import os
from .models import db, init_db
from .controllers import blueprints

def create_app():
    app = Flask(__name__, 
                static_folder='../../frontend/static',
                template_folder='../../frontend/templates')
    
    # 配置 JSON 处理
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # 配置 CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 设置会话密钥
    app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_development_only')
    
    # 配置数据库
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'bbs', 'story.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 确保上传目录存在
    upload_folder = os.path.join(app.static_folder, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # 设置上传目录权限
    try:
        import stat
        os.chmod(upload_folder, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
    except Exception as e:
        print(f"设置上传目录权限失败: {str(e)}")
    
    # 初始化数据库
    db.init_app(app)
    init_db(app)
    
    # 注册蓝图
    for blueprint, prefix in blueprints:
        print(f"注册蓝图: {blueprint.name} at prefix: {prefix}")
        app.register_blueprint(blueprint, url_prefix=prefix)
        
    return app
