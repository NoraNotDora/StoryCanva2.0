from flask import Blueprint, jsonify, request, render_template, session, current_app, flash, redirect, url_for
import os
import re
import uuid
from ..models import User, Post, Comment
from ..utils import login_required, allowed_file
from werkzeug.utils import secure_filename

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.get_all()
    return jsonify(users)

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User.create(username=data['username'], email=data['email'])
    return jsonify({'message': '用户创建成功'}), 201

@user_bp.route('/profile/<username>')
def profile(username):
    # 获取用户信息
    user = User.get_by_username(username)
    
    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('main_bp.index'))
    
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

@user_bp.route('/profile')
@login_required
def current_user_profile():
    """当前登录用户的个人主页"""
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    
    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('main_bp.index'))
    
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

@user_bp.route('/users/<int:user_id>')
def user_profile(user_id):
    """查看指定用户的个人主页"""
    # 获取用户信息
    user = User.get_by_id(user_id)
    
    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('main_bp.index'))
    
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

@user_bp.route('/edit_profile', methods=['GET', 'POST'])
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
            return redirect(url_for('user_bp.edit_profile'))
        
        # 检查邮箱是否被其他用户使用
        existing_user = User.get_by_email(email)
        if existing_user and existing_user['id'] != session['user_id']:
            flash('该邮箱已被使用', 'error')
            return redirect(url_for('user_bp.edit_profile'))
        
        # 处理头像上传
        avatar_path = None
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                try:
                    # 检查文件类型
                    if not allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                        flash('不支持的文件类型，请上传 JPG、PNG 或 GIF 格式的图片', 'error')
                        return redirect(url_for('user_bp.edit_profile'))
                    
                    # 检查文件大小（2MB限制）
                    if len(file.read()) > 2 * 1024 * 1024:  # 2MB in bytes
                        flash('文件大小超过2MB限制', 'error')
                        return redirect(url_for('user_bp.edit_profile'))
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
                    return redirect(url_for('user_bp.edit_profile'))
        
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
        
        return redirect(url_for('user_bp.current_user_profile'))
    
    # GET 请求显示编辑表单
    user = User.get_by_id(session['user_id'])
    return render_template('edit_profile.html', user=user)

@user_bp.route('/users/<username>/posts')
def user_posts(username):
    # 获取用户信息
    user = User.get_by_username(username)
    
    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('main_bp.index'))
    
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

@user_bp.route('/users/<username>/comments')
def user_comments(username):
    # 获取用户信息
    user = User.get_by_username(username)
    
    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('main_bp.index'))
    
    # 获取用户所有评论
    user_comments = User.get_user_comments(user['id'])
    
    return render_template(
        'user_comments.html',
        user=user,
        comments=user_comments
    )