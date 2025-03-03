from flask import Flask, render_template
from flask_cors import CORS
import os
from .models import db, init_db
from .controllers import blueprints

def create_app():
    app = Flask(__name__, 
                template_folder='../../frontend/templates/',
                static_folder='../../frontend/static/')
    CORS(app)
    
    # 配置数据库
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'bbs', 'story.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化数据库
    db.init_app(app)
    init_db(app)
    
    # 注册API蓝图
    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix='/api')
    
    # 直接添加路由到应用程序
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/create')
    def create():
        return render_template('create.html')
    
    @app.route('/achievement')
    def achievement():
        return render_template('achievement.html')
    
    @app.route('/community')
    def community():
        return render_template('community.html')
    
    @app.route('/detail.html')
    def serve_detail():
        return render_template('detail.html')
    
    @app.route('/contact')
    def contact():
        return render_template('contact.html')
    
    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/test')
    def test():
        return "应用程序正常运行！"

    return app
