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
from chatTest.chat import chat, chat_stream
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
        
        # 设置超时时间
        timeout_seconds = 30
        start_time = time.time()
        
        response = chat(model, messages)
        
        if not response:
            return jsonify({'error': '没有收到AI回复，请重试'}), 500
            
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': f'聊天请求失败: {str(e)}'}), 500

@api_bp.route('/chat_stream', methods=['POST'])
def chat_stream_api():
    """处理流式聊天请求"""
    data = request.json
    messages = data.get('messages', [])
    print(messages)
    
    if not messages:
        return jsonify({'error': '消息不能为空'}), 400
    
    # 使用 chat.py 中的函数处理流式聊天
    try:
        # 默认使用 gpt-3.5-turbo 模型，可以根据需要修改
        model = data.get('model', "gpt-4o-mini")
        
        def generate():
            has_content = False
            for chunk in chat_stream(model, messages):
                if chunk is not None:
                    has_content = True
                    print(chunk)
                    yield chunk
            
            # 如果没有内容返回，发送错误消息
            if not has_content:
                yield json.dumps({"error": "没有收到AI回复，请重试"})
        
        return Response(stream_with_context(generate()), mimetype='text/plain')
    except Exception as e:
        return jsonify({'error': f'流式聊天请求失败: {str(e)}'}), 500 
    

