from flask import Blueprint, request, jsonify, Response, stream_with_context
import json
import sys
import os
import time
from dotenv import load_dotenv
load_dotenv()
# 添加 chatTest 目录到 Python 路径
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'chatTest'))
# 根据目录结构调整为正确的相对导入
from chatTest.chat import chat_stream
from ..models import Post

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
        model = data.get('model', "gpt-4o-mini")
        messages = [{"role": "user", "content": message}]
        
        response = chat_stream(model, messages)
        
        if not response:
            return jsonify({'error': '没有收到AI回复，请重试'}), 500
            
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': f'聊天请求失败: {str(e)}'}), 500
