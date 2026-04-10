from flask import Blueprint, request, jsonify, Response, stream_with_context, session, current_app
import json
import sys
import os
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from ..models import Post
from ..utils import login_required, allowed_file

load_dotenv()
# 添加 chatTest 目录到 Python 路径
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'chatTest'))
# 根据目录结构调整为正确的相对导入
from chatTest.chat import chat_stream

# 用于图像生成
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

# --- 图像生成模型加载 ---
# 定义图像保存的目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
GENERATED_IMAGES_DIR = os.path.join(STATIC_DIR, 'generated_images')

os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True) 

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device} for image generation")

try:
    pipe = StableDiffusionPipeline.from_pretrained("IDEA-CCNL/Taiyi-Stable-Diffusion-1B-Chinese-v0.1", torch_dtype=torch.float16 if device == "cuda" else torch.float32)
    pipe = pipe.to(device)
    print("Image generation model loaded successfully.")
except Exception as e:
    print(f"Error loading image generation model: {e}")
    pipe = None

@api_bp.route('/chat', methods=['POST'])
def chat_api():
    """处理聊天请求"""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': '消息不能为空'}), 400
    
    try:
        model = data.get('model', "gpt-4o-mini")
        messages = [{"role": "user", "content": message}]
        
        response = chat_stream(model, messages)
        
        if not response:
            return jsonify({'error': '没有收到AI回复，请重试'}), 500
            
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': f'聊天请求失败: {str(e)}'}), 500

@api_bp.route('/upload', methods=['POST'])
@login_required
def upload_image():
    """通用图片上传API"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        image_file = request.files['image']
        if not image_file or not allowed_file(image_file.filename):
            return jsonify({'error': '不支持的文件类型'}), 400
        
        filename = secure_filename(image_file.filename)
        user_id = session.get('user_id')
        unique_filename = f"{user_id}_{int(datetime.now().timestamp())}_{filename}"
        
        upload_folder = os.path.join(current_app.static_folder, 'elements')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        image_file.save(file_path)
        
        image_path = f"elements/{unique_filename}"
        
        return jsonify({
            'success': True,
            'path': image_path
        }), 200
    
    except Exception as e:
        print(f"上传图片时出错: {str(e)}")
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@api_bp.route('/generate-image', methods=['POST'])
def generate_image():
    """图像生成路由"""
    if pipe is None:
        return jsonify({"error": "Image generation model not loaded."}), 500

    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Invalid request. 'prompt' field is required."}), 400

    prompt = data['prompt']
    print(f"Received image generation request with prompt: {prompt}")

    try:
        image = pipe(prompt, num_inference_steps=50).images[0]

        image_filename = f"{uuid.uuid4()}.png"
        image_path = os.path.join(GENERATED_IMAGES_DIR, image_filename)

        image.save(image_path)
        print(f"Image saved to {image_path}")

        image_url = f"/static/generated_images/{image_filename}"

        return jsonify({"success": True, "image_url": image_url})

    except Exception as e:
        print(f"Error during image generation: {e}")
        return jsonify({"error": f"Failed to generate image: {e}"}), 500
