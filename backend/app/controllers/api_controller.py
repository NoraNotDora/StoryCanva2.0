from flask import Blueprint, request, jsonify, Response, stream_with_context
import json
import sys
import os

# 添加 chatTest 目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../chatTest'))
from chat import chat, chat_stream
from backend.models import Post

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

@api_bp.route('/posts', methods=['GET'])
def get_posts():
    """获取所有公开帖子"""
    posts = Post.get_all_public()
    return jsonify(posts)

@api_bp.route('/chat', methods=['POST'])
def chat_api():
    """处理聊天请求"""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': '消息不能为空'}), 400
    
    # 使用 chat.py 中的函数处理聊天
    try:
        # 默认使用 gpt-3.5-turbo 模型，可以根据需要修改
        model = "gpt-3.5-turbo"
        messages = [{"role": "user", "content": message}]
        response = chat(model, messages)
        
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/chat_stream', methods=['POST'])
def chat_stream_api():
    """处理流式聊天请求"""
    data = request.json
    messages = data.get('messages', [])
    
    if not messages:
        return jsonify({'error': '消息不能为空'}), 400
    
    # 使用 chat.py 中的函数处理流式聊天
    try:
        # 默认使用 gpt-3.5-turbo 模型，可以根据需要修改
        model = "gpt-3.5-turbo"
        
        def generate():
            for chunk in chat_stream(model, messages):
                if chunk is not None:
                    yield chunk
        
        return Response(stream_with_context(generate()), mimetype='text/plain')
    except Exception as e:
        return jsonify({'error': str(e)}), 500 