from flask import jsonify
from backend.models.post import Post

@post_bp.route('/posts', methods=['GET'])
def get_posts():
    """获取所有公开帖子"""
    posts = Post.get_all_public()
    
    # 确保图片路径正确
    for post in posts:
        if post['image_path'] and not post['image_path'].startswith('uploads/'):
            post['image_path'] = f"uploads/{post['image_path']}"
    
    return jsonify(posts) 