from flask import Blueprint, render_template, flash, redirect, url_for, request, session, current_app, jsonify
from ..models import User, Comment, Post
from ..utils import login_required, allowed_file
import re
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/create')
@login_required
def create():
    return render_template('create.html')

@main_bp.route('/achievement')
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

@main_bp.route('/community')
def community():
    return render_template('community.html')

@main_bp.route('/detail.html')
def serve_detail():
    """显示帖子详情页面"""
    post_id = request.args.get('id')
    
    if not post_id:
        flash('帖子ID不能为空', 'error')
        return redirect(url_for('main_bp.community'))
    
    # 获取帖子详情
    post = Post.get_by_id(post_id)
    
    if not post:
        flash('帖子不存在', 'error')
        return redirect(url_for('main_bp.community'))
    
    # 增加浏览量
    Post.increment_views(post_id)
    
    # 获取评论
    comments = Comment.get_by_post_id(post_id)
    
    return render_template('detail.html', post=post, comments=comments)

@main_bp.route('/detail/<int:id>')
def detail_redirect(id):
    """重定向到详情页面"""
    return redirect(url_for('main_bp.serve_detail', id=id))

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/login')
def login():
    return render_template('login.html')

@main_bp.route('/test')
def test():
    return "应用程序正常运行！"
