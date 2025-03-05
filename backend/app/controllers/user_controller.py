# user_controller.py in app/controllers
from flask import Blueprint, jsonify, request, render_template, send_from_directory, session, current_app
import os
from datetime import datetime
from ..models import User, Post, Comment, db, get_db_connection
from ..utils import login_required
from werkzeug.utils import secure_filename

# 创建蓝图
user_bp = Blueprint('user_bp', __name__)

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 基础路由
@user_bp.route('/')
def index():
    return render_template('index.html')

@user_bp.route('/create')
def create():
    return render_template('create.html')

@user_bp.route('/achievement')
def achievement():
    return render_template('achievement.html')

@user_bp.route('/community')
def community():
    return render_template('community.html')

@user_bp.route('/detail.html')
def serve_detail():
    return render_template('detail.html')

@user_bp.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(user_bp.root_path, '../../frontend/static/css'), filename)

@user_bp.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(user_bp.root_path, '../../frontend/static/js'), filename)

@user_bp.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(user_bp.root_path, '../../frontend/static/images'), filename)

# 用户相关API
@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.get_all()
    return jsonify(users)

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User.create(username=data['username'], email=data['email'])
    return jsonify({'message': '用户创建成功'}), 201

# 帖子相关API
# 获取所有帖子
@user_bp.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.get_all_public()
    return jsonify(posts)

# 获取单个帖子
@user_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.get_by_id(post_id)
    if post:
        Post.update_views(post_id)
        return jsonify(post)
    else:
        return jsonify({'message': '帖子未找到'}), 404

# 创建新帖子
@user_bp.route('/posts', methods=['POST'])
@login_required
def create_post():
    try:
        print("接收到创建帖子请求")
        print(f"请求表单: {request.form}")
        print(f"请求文件: {request.files}")
        
        # 获取表单数据
        title = request.form.get('title')
        content = request.form.get('content')
        is_public = int(request.form.get('is_public', 0))
        
        # 使用当前登录用户的信息
        user_id = session.get('user_id')
        author = session.get('username', '匿名用户')
        
        print(f"接收到的数据: title={title}, content={content}, user_id={user_id}, author={author}, is_public={is_public}")
        
        if not title or not content:
            return jsonify({'message': '标题和内容是必需的'}), 400
        
        # 处理图片上传
        image_path = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
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
        
        # 创建帖子
        post = Post.create(title, content, author, user_id, image_path, is_public)
        
        print(f"创建的帖子: {post}")
        
        if post and 'id' in post:
            return jsonify({'success': True, 'id': post['id']}), 201
        else:
            return jsonify({'message': '创建帖子失败'}), 500
            
    except Exception as e:
        import traceback
        print(f"创建帖子时出错: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'服务器错误: {str(e)}'}), 500

# 获取帖子的所有评论
@user_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    comments = Comment.get_by_post_id(post_id)
    return jsonify(comments)

# 创建新评论
@user_bp.route('/comments', methods=['POST'])
@login_required
def create_comment():
    try:
        data = request.get_json()
        post_id = data.get('postId')
        content = data.get('content')
        
        # 使用当前登录用户的信息
        user_id = session.get('user_id')
        author = session.get('username', '匿名用户')
        
        if not post_id or not content:
            return jsonify({'message': '帖子ID和内容是必需的'}), 400
        
        # 检查帖子是否存在
        post = Post.get_by_id(post_id)
        if not post:
            return jsonify({'message': '帖子不存在'}), 404
        
        # 创建评论
        new_comment = Comment.create(post_id=post_id, content=content, author=author, user_id=user_id)
        
        return jsonify({'success': True, 'id': new_comment['id']}), 201
    except Exception as e:
        print(f"创建评论时出错: {str(e)}")
        return jsonify({'message': f'服务器错误: {str(e)}'}), 500

# 点赞帖子
@user_bp.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    try:
        # 检查帖子是否存在
        post = Post.get_by_id(post_id)
        if not post:
            return jsonify({'message': '帖子不存在'}), 404
        
        # 增加点赞数
        Post.increment_likes(post_id)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"点赞帖子时出错: {str(e)}")
        return jsonify({'message': f'服务器错误: {str(e)}'}), 500

# 点赞评论
@user_bp.route('/comments/<int:comment_id>/like', methods=['POST'])
def like_comment(comment_id):
    try:
        # 检查评论是否存在
        comment = Comment.get_by_id(comment_id)
        if not comment:
            return jsonify({'message': '评论不存在'}), 404
        
        # 增加点赞数
        Comment.increment_likes(comment_id)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"点赞评论时出错: {str(e)}")
        return jsonify({'message': f'服务器错误: {str(e)}'}), 500

@user_bp.route('/contact')
def contact():
    return render_template('contact.html')

@user_bp.route('/login')
def login():
    return render_template('login.html')

# 更新帖子公开状态
@user_bp.route('/posts/<int:post_id>/public', methods=['PUT'])
@login_required
def update_post_public_status(post_id):
    try:
        data = request.get_json()
        is_public = data.get('is_public', 0)
        
        # 检查帖子是否存在
        post = Post.get_by_id(post_id)
        if not post:
            return jsonify({'message': '帖子不存在'}), 404
        
        # 检查是否是帖子的作者
        user_id = session.get('user_id')
        if post['user_id'] != user_id:
            return jsonify({'message': '您没有权限修改此帖子'}), 403
        
        # 更新公开状态
        Post.update_public_status(post_id, is_public)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"更新帖子公开状态时出错: {str(e)}")
        return jsonify({'message': f'服务器错误: {str(e)}'}), 500

# 删除帖子
@user_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    try:
        # 检查帖子是否存在
        post = Post.get_by_id(post_id)
        if not post:
            return jsonify({'message': '帖子不存在'}), 404
        
        # 检查是否是帖子的作者
        user_id = session.get('user_id')
        if post['user_id'] != user_id:
            return jsonify({'message': '您没有权限删除此帖子'}), 403
        
        # 删除帖子
        Post.delete(post_id)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"删除帖子时出错: {str(e)}")
        return jsonify({'message': f'服务器错误: {str(e)}'}), 500
