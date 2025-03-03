# user_controller.py in app/controllers
from flask import Blueprint, jsonify, request, render_template, send_from_directory
import os
import datetime
from ..models import User, Post, Comment, db, get_db_connection

# 创建蓝图
user_bp = Blueprint('user_bp', __name__)

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
    posts = Post.get_all()
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
def create_post():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    author = data.get('author') or '匿名用户'

    if not title or not content:
        return jsonify({'message': '标题和内容是必需的'}), 400

    new_post = Post.create(title=title, content=content, author=author)
    return jsonify({'id': new_post['id']}), 201

# 获取帖子的所有评论
@user_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    comments = Comment.get_by_post_id(post_id)
    return jsonify(comments)

# 创建新评论
@user_bp.route('/comments', methods=['POST'])
def create_comment():
    data = request.get_json()
    post_id = data.get('postId')
    content = data.get('content')
    author = data.get('author') or '匿名用户'

    if not post_id or not content:
        return jsonify({'message': '帖子ID和内容是必需的'}), 400

    new_comment = Comment.create(post_id=post_id, content=content, author=author)
    return jsonify({'id': new_comment['id']}), 201

# 点赞帖子
@user_bp.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    post = Post.get_by_id(post_id)
    if post:
        Post.update_likes(post_id)
        return jsonify({'success': True})
    else:
        return jsonify({'message': '帖子未找到'}), 404

# 点赞评论
@user_bp.route('/comments/<int:comment_id>/like', methods=['POST'])
def like_comment(comment_id):
    # 这里需要添加一个方法来检查评论是否存在
    Comment.update_likes(comment_id)
    return jsonify({'success': True})

@user_bp.route('/contact')
def contact():
    return render_template('contact.html')

@user_bp.route('/login')
def login():
    return render_template('login.html')
