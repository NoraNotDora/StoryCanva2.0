from flask import Blueprint, jsonify, request, render_template, session, current_app, flash, redirect, url_for
import os
from datetime import datetime
from ..models import Post, Comment, User
from ..utils import login_required, allowed_file
from werkzeug.utils import secure_filename
import uuid

post_bp = Blueprint('post_bp', __name__)

@post_bp.route('/posts', methods=['GET'])
def get_posts():
    """获取所有公开帖子"""
    posts = Post.get_all_public()
    return jsonify(posts)

@post_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """获取单个帖子"""
    post = Post.get_by_id(post_id)
    if post:
        Post.update_views(post_id)
        return jsonify(post)
    else:
        return jsonify({'message': '帖子未找到'}), 404

@post_bp.route('/posts', methods=['POST'])
@login_required
def create_post():
    """创建新帖子"""
    try:
        title = request.form.get('title')
        content = request.form.get('content')
        is_public = int(request.form.get('is_public', 0))
        
        user_id = session.get('user_id')
        author = session.get('username', '匿名用户')
        
        if not title or not content:
            return jsonify({'message': '标题和内容是必需的'}), 400
        
        image_path = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                unique_filename = f"{user_id}_{int(datetime.now().timestamp())}_{filename}"
                
                upload_folder = os.path.join(current_app.static_folder, 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join(upload_folder, unique_filename)
                image_file.save(file_path)
                
                image_path = f"uploads/{unique_filename}"
        
        post = Post.create(title, content, author, user_id, image_path, is_public)
        
        if post and 'id' in post:
            return jsonify({'success': True, 'id': post['id']}), 201
        else:
            return jsonify({'message': '创建帖子失败'}), 500
            
    except Exception as e:
        return jsonify({'message': f'服务器错误: {str(e)}'}), 500

@post_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """获取帖子的所有评论"""
    comments = Comment.get_by_post_id(post_id)
    return jsonify(comments)

@post_bp.route('/comments', methods=['POST'])
@login_required
def create_comment():
    """创建新评论"""
    try:
        data = request.get_json()
        post_id = data.get('postId')
        content = data.get('content')
        
        user_id = session.get('user_id')
        author = session.get('username', '匿名用户')
        
        if not post_id or not content:
            return jsonify({'message': '帖子ID和内容是必需的'}), 400
        
        post = Post.get_by_id(post_id)
        if not post:
            return jsonify({'message': '帖子不存在'}), 404
        
        new_comment = Comment.create(post_id=post_id, content=content, author=author, user_id=user_id)
        
        return jsonify({'success': True, 'id': new_comment['id']}), 201
    except Exception as e:
        return jsonify({'message': f'服务器错误: {str(e)}'}), 500

@post_bp.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """点赞帖子"""
    try:
        post = Post.get_by_id(post_id)
        if not post:
            return jsonify({'message': '帖子不存在'}), 404
        
        Post.increment_likes(post_id)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'message': f'服务器错误: {str(e)}'}), 500

@post_bp.route('/comments/<int:comment_id>/like', methods=['POST'])
def like_comment(comment_id):
    """点赞评论"""
    try:
        comment = Comment.get_by_id(comment_id)
        if not comment:
            return jsonify({'message': '评论不存在'}), 404
        
        Comment.increment_likes(comment_id)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'message': f'服务器错误: {str(e)}'}), 500

@post_bp.route('/posts/<int:post_id>/public', methods=['PUT'])
@login_required
def update_post_public_status(post_id):
    """更新帖子公开状态"""
    try:
        data = request.get_json()
        is_public = data.get('is_public', 0)
        
        post = Post.get_by_id(post_id)
        if not post:
            return jsonify({'message': '帖子不存在'}), 404
        
        user_id = session.get('user_id')
        if post['user_id'] != user_id:
            return jsonify({'message': '您没有权限修改此帖子'}), 403
        
        Post.update_public_status(post_id, is_public)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'message': f'服务器错误: {str(e)}'}), 500

@post_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    """删除帖子"""
    try:
        post = Post.get_by_id(post_id)
        if not post:
            return jsonify({'message': '帖子不存在'}), 404
        
        user_id = session.get('user_id')
        if post['user_id'] != user_id:
            return jsonify({'message': '您没有权限删除此帖子'}), 403
        
        Post.delete(post_id)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'message': f'服务器错误: {str(e)}'}), 500

@post_bp.route('/my-stories')
@login_required
def my_stories():
    user_id = session.get('user_id')
    stories = Post.get_by_user_id(user_id)
    return render_template('my_stories.html', stories=stories)

@post_bp.route('/stories/<int:story_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_story(story_id):
    """编辑故事页面"""
    story = Post.get_by_id(story_id)
    
    if not story:
        flash('故事不存在', 'error')
        return redirect(url_for('post_bp.my_stories'))
    
    user_id = session.get('user_id')
    if story['user_id'] != user_id:
        flash('您没有权限编辑此故事', 'error')
        return redirect(url_for('post_bp.my_stories'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_public = int(request.form.get('is_public', 0))
        
        if not title or not content:
            flash('标题和内容不能为空', 'error')
            return render_template('edit_story.html', story=story)
        
        image_path = story['image_path']
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                unique_filename = f"{user_id}_{int(datetime.now().timestamp())}_{filename}"
                
                upload_folder = os.path.join(current_app.static_folder, 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join(upload_folder, unique_filename)
                image_file.save(file_path)
                
                image_path = f"uploads/{unique_filename}"
        
        Post.update(
            story_id=story_id,
            title=title,
            content=content,
            is_public=is_public,
            image_path=image_path
        )
        
        flash('故事更新成功', 'success')
        return redirect(url_for('main_bp.serve_detail', id=story_id))
    
    return render_template('edit_story.html', story=story)