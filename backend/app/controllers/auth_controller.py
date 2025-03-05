from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from ..models import User
import re

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 获取表单数据
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 表单验证
        if not username or not email or not password or not confirm_password:
            flash('所有字段都是必填的', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不匹配', 'error')
            return render_template('register.html')
        
        # 验证邮箱格式
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('请输入有效的电子邮件地址', 'error')
            return render_template('register.html')
        
        # 验证密码强度
        if len(password) < 8:
            flash('密码必须至少包含8个字符', 'error')
            return render_template('register.html')
        
        # 检查用户名和邮箱是否已存在
        if User.get_by_username(username):
            flash('用户名已被使用', 'error')
            return render_template('register.html')
        
        if User.get_by_email(email):
            flash('电子邮件已被注册', 'error')
            return render_template('register.html')
        
        # 创建新用户
        try:
            user = User.create(username, email, password)
            flash('注册成功！请登录', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'注册失败: {str(e)}', 'error')
            return render_template('register.html')
    
    # GET请求，显示注册表单
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('login.html')
        
        # 查找用户
        user = User.get_by_username(username)
        
        # 验证密码
        if user and User.verify_password(user, password):
            # 设置会话
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            # 加载用户成就信息
            story_count = User.count_user_posts(user['id'])
            unlocked_achievements = 0
            if story_count >= 1: unlocked_achievements += 1
            if story_count >= 5: unlocked_achievements += 1
            if story_count >= 10: unlocked_achievements += 1
            if story_count >= 20: unlocked_achievements += 1
            if story_count >= 50: unlocked_achievements += 1
            
            session['unlocked_achievements'] = unlocked_achievements
            
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'error')
            return render_template('login.html')
    
    # GET请求，显示登录表单
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    # 清除会话
    session.pop('user_id', None)
    session.pop('username', None)
    flash('您已成功退出登录', 'success')
    return redirect(url_for('index'))

# API端点，用于AJAX请求
@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # 验证数据...
    
    try:
        user = User.create(username, email, password)
        return jsonify({'success': True, 'message': '注册成功'}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.get_by_username(username)
    
    if user and User.verify_password(user, password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'success': True, 'user': {'id': user['id'], 'username': user['username']}}), 200
    else:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401 