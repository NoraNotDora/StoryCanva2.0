from flask import Flask, render_template, flash, redirect, url_for, request, session, current_app, jsonify, Blueprint
from flask_cors import CORS
import os
from .models import db, init_db, User, Comment, Post, get_db_connection
from .controllers import blueprints
from .utils import login_required, allowed_file
import re
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import uuid
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image

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
    
    # 注册API蓝图
    for blueprint in blueprints:
        print(f"注册蓝图: {blueprint.name}")
        app.register_blueprint(blueprint, url_prefix='/api')
    
    # 直接添加路由到应用程序
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/create')
    @login_required
    def create():
        return render_template('create.html')
    
    @app.route('/achievement')
    @login_required
    def achievement():
        """用户成就页面"""
        user_id = session.get('user_id')
        
        # 获取用户创作的故事数量
        story_count = User.count_user_posts(user_id)
        
        # 定义成就列表
        achievements = [
            {
                'id': 'explorer',
                'name': '故事探险家',
                'description': '累计创作1个故事',
                'image': 'picture/故事探险家.png',
                'required': 1,
                'unlocked': story_count >= 1
            },
            {
                'id': 'skilled',
                'name': '故事小能手',
                'description': '累计创作5个故事',
                'image': 'picture/故事小能手.png',
                'required': 5,
                'unlocked': story_count >= 5
            },
            {
                'id': 'genius',
                'name': '故事小天才',
                'description': '累计创作10个故事',
                'image': 'picture/故事小天才.png',
                'required': 10,
                'unlocked': story_count >= 10
            },
            {
                'id': 'writer',
                'name': '奇趣小作家',
                'description': '累计创作20个故事',
                'image': 'picture/奇趣小作家.png',
                'required': 20,
                'unlocked': story_count >= 20
            },
            {
                'id': 'master',
                'name': '梦幻编织师',
                'description': '累计创作50个故事',
                'image': 'picture/梦幻编织师.png',
                'required': 50,
                'unlocked': story_count >= 50
            }
        ]
        
        return render_template('achievement.html', achievements=achievements, story_count=story_count)
    
    @app.route('/community')
    def community():
        return render_template('community.html')
    
    @app.route('/detail.html')
    def serve_detail():
        """显示帖子详情页面"""
        post_id = request.args.get('id')
        
        if not post_id:
            flash('帖子ID不能为空', 'error')
            return redirect(url_for('community'))
        
        # 获取帖子详情
        post = Post.get_by_id(post_id)
        
        if not post:
            flash('帖子不存在', 'error')
            return redirect(url_for('community'))
        
        # 增加浏览量
        Post.increment_views(post_id)
        
        # 获取评论
        comments = Comment.get_by_post_id(post_id)
        
        return render_template('detail.html', post=post, comments=comments)
    
    @app.route('/contact')
    def contact():
        return render_template('contact.html')
    
    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/test')
    def test():
        return "应用程序正常运行！"

    @app.route('/profile/<username>')
    def profile(username):
        # 获取用户信息
        user = User.get_by_username(username)
        
        if not user:
            flash('用户不存在', 'error')
            return redirect(url_for('index'))
        
        # 获取用户统计信息
        user_stats = User.get_user_stats(user['id'])
        
        # 获取用户最近的5篇帖子
        user_posts = User.get_user_posts(user['id'], limit=5)
        
        # 获取用户最近的5条评论
        user_comments = User.get_user_comments(user['id'], limit=5)
        
        # 为每个帖子添加评论数量
        for post in user_posts:
            comments = Comment.get_by_post_id(post['id'])
            post['comment_count'] = len(comments)
        
        return render_template('profile.html', user=user, user_stats=user_stats, user_posts=user_posts, user_comments=user_comments)
    
    @app.route('/profile')
    @login_required
    def current_user_profile():
        """当前登录用户的个人主页"""
        user_id = session.get('user_id')
        user = User.get_by_id(user_id)
        
        if not user:
            flash('用户不存在', 'error')
            return redirect(url_for('index'))
        
        # 获取用户统计信息
        user_stats = {
            'post_count': User.count_user_posts(user_id),
            'comment_count': User.count_user_comments(user_id),
            'total_likes': User.count_user_total_likes(user_id)
        }
        
        # 获取用户最近的帖子（限制5条）
        user_posts = User.get_user_posts(user_id, limit=5)
        
        # 获取用户最近的评论（限制5条）
        user_comments = User.get_user_comments(user_id, limit=5)
        
        return render_template(
            'profile.html',
            user=user,
            user_stats=user_stats,
            user_posts=user_posts,
            user_comments=user_comments
        )

    @app.route('/users/<int:user_id>')
    def user_profile(user_id):
        """查看指定用户的个人主页"""
        # 获取用户信息
        user = User.get_by_id(user_id)
        
        if not user:
            flash('用户不存在', 'error')
            return redirect(url_for('index'))
        
        # 获取用户统计信息
        user_stats = {
            'post_count': User.count_user_posts(user_id),
            'comment_count': User.count_user_comments(user_id),
            'total_likes': User.count_user_total_likes(user_id)
        }
        
        # 获取用户最近的帖子（限制5条）
        user_posts = User.get_user_posts(user_id, limit=5)
        
        # 获取用户最近的评论（限制5条）
        user_comments = User.get_user_comments(user_id, limit=5)
        
        return render_template(
            'profile.html',
            user=user,
            user_stats=user_stats,
            user_posts=user_posts,
            user_comments=user_comments
        )

    @app.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        if request.method == 'POST':
            email = request.form.get('email')
            nickname = request.form.get('nickname')
            age = request.form.get('age')
            gender = request.form.get('gender')
            
            # 获取多选值并转换为JSON
            favorite_colors = request.form.getlist('favorite_colors')
            story_preferences = request.form.getlist('story_preferences')
            favorite_characters = request.form.getlist('favorite_characters')
            fear_list = request.form.getlist('fear_list')
            
            # 验证邮箱格式
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('邮箱格式不正确', 'error')
                return redirect(url_for('edit_profile'))
            
            # 检查邮箱是否被其他用户使用
            existing_user = User.get_by_email(email)
            if existing_user and existing_user['id'] != session['user_id']:
                flash('该邮箱已被使用', 'error')
                return redirect(url_for('edit_profile'))
            
            # 处理头像上传
            avatar_path = None
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and file.filename:
                    try:
                        # 检查文件类型
                        if not allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                            flash('不支持的文件类型，请上传 JPG、PNG 或 GIF 格式的图片', 'error')
                            return redirect(url_for('edit_profile'))
                        
                        # 检查文件大小（2MB限制）
                        if len(file.read()) > 2 * 1024 * 1024:  # 2MB in bytes
                            flash('文件大小超过2MB限制', 'error')
                            return redirect(url_for('edit_profile'))
                        file.seek(0)  # 重置文件指针
                        
                        # 生成安全的文件名
                        filename = secure_filename(file.filename)
                        # 确保文件名是唯一的
                        ext = os.path.splitext(filename)[1]
                        unique_filename = f"{uuid.uuid4()}{ext}"
                        # 保存文件
                        avatar_path = os.path.join('uploads', unique_filename)
                        upload_path = os.path.join(current_app.static_folder, avatar_path)
                        
                        # 确保上传目录存在
                        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                        file.save(upload_path)
                        
                    except Exception as e:
                        flash(f'头像上传失败：{str(e)}', 'error')
                        print(f"Error uploading avatar: {e}")
                        return redirect(url_for('edit_profile'))
            
            try:
                # 使用User模型的方法更新用户信息
                user_data = {
                    'email': email,
                    'nickname': nickname,
                    'age': age,
                    'gender': gender,
                    'favorite_colors': favorite_colors,
                    'story_preferences': story_preferences,
                    'favorite_characters': favorite_characters,
                    'fear_list': fear_list
                }
                
                if avatar_path:
                    user_data['avatar'] = avatar_path
                
                success = User.update_profile(session['user_id'], user_data)
                
                if success:
                    flash('个人资料更新成功！', 'success')
                else:
                    flash('更新失败，请稍后重试', 'error')
                
            except Exception as e:
                flash('更新失败，请稍后重试', 'error')
                print(f"Error updating profile: {e}")
            
            return redirect(url_for('current_user_profile'))
        
        # GET 请求显示编辑表单
        user = User.get_by_id(session['user_id'])
        return render_template('edit_profile.html', user=user)

    @app.route('/users/<username>/posts')
    def user_posts(username):
        # 获取用户信息
        user = User.get_by_username(username)
        
        if not user:
            flash('用户不存在', 'error')
            return redirect(url_for('index'))
        
        # 获取用户所有帖子
        user_posts = User.get_user_posts(user['id'])
        
        # 为每个帖子添加评论数量
        for post in user_posts:
            comments = Comment.get_by_post_id(post['id'])
            post['comment_count'] = len(comments)
        
        return render_template(
            'user_posts.html',
            user=user,
            posts=user_posts
        )

    @app.route('/users/<username>/comments')
    def user_comments(username):
        # 获取用户信息
        user = User.get_by_username(username)
        
        if not user:
            flash('用户不存在', 'error')
            return redirect(url_for('index'))
        
        # 获取用户所有评论
        user_comments = User.get_user_comments(user['id'])
        
        return render_template(
            'user_comments.html',
            user=user,
            comments=user_comments
        )

    @app.route('/my-stories')
    @login_required
    def my_stories():
        user_id = session.get('user_id')
        stories = Post.get_by_user_id(user_id)
        return render_template('my_stories.html', stories=stories)

    @app.route('/stories/<int:story_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_story(story_id):
        """编辑故事页面"""
        # 获取故事信息
        story = Post.get_by_id(story_id)
        
        if not story:
            flash('故事不存在', 'error')
            return redirect(url_for('my_stories'))
        
        # 检查是否是故事的作者
        user_id = session.get('user_id')
        if story['user_id'] != user_id:
            flash('您没有权限编辑此故事', 'error')
            return redirect(url_for('my_stories'))
        
        if request.method == 'POST':
            # 处理表单提交
            title = request.form.get('title')
            content = request.form.get('content')
            is_public = int(request.form.get('is_public', 0))
            
            if not title or not content:
                flash('标题和内容不能为空', 'error')
                return render_template('edit_story.html', story=story)
            
            # 处理图片上传
            image_path = story['image_path']  # 默认保持原图片
            if 'image' in request.files:
                image_file = request.files['image']
                if image_file and image_file.filename and allowed_file(image_file.filename):
                    # 生成安全的文件名
                    filename = secure_filename(image_file.filename)
                    # 生成唯一文件名
                    unique_filename = f"{user_id}_{int(datetime.now().timestamp())}_{filename}"
                    
                    # 确保上传目录存在
                    upload_folder = os.path.join(current_app.static_folder, 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    # 保存文件
                    file_path = os.path.join(upload_folder, unique_filename)
                    image_file.save(file_path)
                    
                    # 存储相对路径
                    image_path = f"uploads/{unique_filename}"
            
            # 更新故事
            Post.update(
                story_id=story_id,
                title=title,
                content=content,
                is_public=is_public,
                image_path=image_path
            )
            
            flash('故事更新成功', 'success')
            return redirect(url_for('serve_detail', id=story_id))
        
        # GET 请求，显示编辑表单
        return render_template('edit_story.html', story=story)

    @app.route('/detail/<int:id>')
    def detail_redirect(id):
        """重定向到详情页面"""
        return redirect(url_for('serve_detail', id=id))

    @app.route('/api/upload', methods=['POST'])
    @login_required
    def upload_image():
        try:
            if 'image' not in request.files:
                return jsonify({'error': '没有上传文件'}), 400
            
            image_file = request.files['image']
            if not image_file or not allowed_file(image_file.filename):
                return jsonify({'error': '不支持的文件类型'}), 400
            
            # 生成安全的文件名
            filename = secure_filename(image_file.filename)
            # 生成唯一文件名
            user_id = session.get('user_id')
            unique_filename = f"{user_id}_{int(datetime.now().timestamp())}_{filename}"
            
            # 确保上传目录存在
            upload_folder = os.path.join(current_app.static_folder, 'elements')
            os.makedirs(upload_folder, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(upload_folder, unique_filename)
            image_file.save(file_path)
            
            # 返回相对路径
            image_path = f"elements/{unique_filename}"
            
            return jsonify({
                'success': True,
                'path': image_path
            }), 200
        
        except Exception as e:
            print(f"上传图片时出错: {str(e)}")
            return jsonify({'error': f'服务器错误: {str(e)}'}), 500

    # 定义图像保存的目录
    # 确保这个目录存在，并且Flask应用可以访问和提供静态文件
    # 我们假设在 backend/app 目录下创建 static/generated_images
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    GENERATED_IMAGES_DIR = os.path.join(STATIC_DIR, 'generated_images')

    # 如果目录不存在，则创建
    os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True) # 确保static目录也存在

    # 加载图像生成模型
    # 注意：这是一个耗时操作，模型只加载一次
    # 尝试使用GPU，如果不可用则使用CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device} for image generation")

    try:
        pipe = StableDiffusionPipeline.from_pretrained("IDEA-CCNL/Taiyi-Stable-Diffusion-1B-Chinese-v0.1", torch_dtype=torch.float16 if device == "cuda" else torch.float32)
        pipe = pipe.to(device)
        print("Image generation model loaded successfully.")
    except Exception as e:
        print(f"Error loading image generation model: {e}")
        pipe = None # 如果加载失败，将pipe设为None

    # 定义蓝图，虽然当前views.py可能直接定义路由，但使用蓝图是更好的实践
    bp = Blueprint('main', __name__) # 假设视图逻辑使用了一个名为 'main' 的蓝图

    @bp.route('/generate-image', methods=['POST'])
    def generate_image():
        """
        图像生成路由
        接收POST请求，包含JSON格式的prompt字段
        返回生成的图像URL
        """
        if pipe is None:
            return jsonify({"error": "Image generation model not loaded."}), 500

        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Invalid request. 'prompt' field is required."}), 400

        prompt = data['prompt']
        print(f"Received image generation request with prompt: {prompt}")

        try:
            # 调用模型生成图像
            # num_inference_steps 可以调整生成质量和速度
            image = pipe(prompt, num_inference_steps=50).images[0]

            # 生成唯一的图片文件名 (使用uuid确保唯一性)
            image_filename = f"{uuid.uuid4()}.png"
            image_path = os.path.join(GENERATED_IMAGES_DIR, image_filename)

            # 保存图片
            image.save(image_path)
            print(f"Image saved to {image_path}")

            # 构建图片的静态访问URL
            # 假设你的Flask应用将 /static 映射到 backend/app/static 目录
            image_url = f"/static/generated_images/{image_filename}"

            return jsonify({"success": True, "image_url": image_url})

        except Exception as e:
            print(f"Error during image generation: {e}")
            return jsonify({"error": f"Failed to generate image: {e}"}), 500

    # 注册蓝图 (如果使用了蓝图)
    app.register_blueprint(bp)

    return app
