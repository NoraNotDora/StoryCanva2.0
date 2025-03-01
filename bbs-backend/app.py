from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, static_folder='../') #  设置静态文件目录为上级目录，以便访问 index.html, css, js, images
CORS(app)

DATABASE = 'story.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row #  将行数据以字典形式返回
    return conn

def init_db():
    with app.app_context():
        db = get_db_connection()
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()
        db.close()

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT,
            date TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            postId INTEGER NOT NULL,
            content TEXT NOT NULL,
            author TEXT,
            date TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            FOREIGN KEY (postId) REFERENCES posts(id)
        )
    """)
    conn.commit()
    conn.close()

create_tables() #  确保表在应用启动时被创建

#  提供静态文件服务，包括 index.html 和 detail.html
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/detail.html')
def serve_detail():
    return send_from_directory(app.static_folder, 'detail.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(app.static_folder, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(app.static_folder, 'js'), filename)

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(app.static_folder, 'images'), filename)


# API 接口

# 获取所有帖子
@app.route('/api/posts', methods=['GET'])
def get_posts():
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM posts ORDER BY date DESC").fetchall()
    conn.close()
    return jsonify([dict(post) for post in posts])

# 获取单个帖子
@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if post:
        conn.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (post_id,)) #  增加浏览量
        conn.commit()
        conn.close()
        return jsonify(dict(post))
    else:
        conn.close()
        return jsonify({'message': 'Post not found'}), 404

# 创建新帖子
@app.route('/api/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    author = data.get('author') or '匿名用户' #  默认作者
    date = datetime.datetime.now().isoformat() #  获取当前时间

    if not title or not content:
        return jsonify({'message': 'Title and content are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (title, content, author, date) VALUES (?, ?, ?, ?)",
                   (title, content, author, date))
    post_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'id': post_id}), 201

# 获取帖子的所有评论
@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    conn = get_db_connection()
    comments = conn.execute("SELECT * FROM comments WHERE postId = ? ORDER BY date DESC", (post_id,)).fetchall()
    conn.close()
    return jsonify([dict(comment) for comment in comments])

# 创建新评论
@app.route('/api/comments', methods=['POST'])
def create_comment():
    data = request.get_json()
    post_id = data.get('postId')
    content = data.get('content')
    author = data.get('author') or '匿名用户' #  默认作者
    date = datetime.datetime.now().isoformat() #  获取当前时间

    if not post_id or not content:
        return jsonify({'message': 'Post ID and content are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comments (postId, content, author, date) VALUES (?, ?, ?, ?)",
                   (post_id, content, author, date))
    comment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'id': comment_id}), 201

# 点赞帖子
@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# 点赞评论
@app.route('/api/comments/<int:comment_id>/like', methods=['POST'])
def like_comment(comment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE comments SET likes = likes + 1 WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    import datetime #  导入 datetime 模块

    #  检查数据库文件是否存在，如果不存在则初始化数据库
    if not os.path.exists(DATABASE):
        init_db()

    app.run(debug=True, port=5000) #  Flask 默认端口是 5000，debug=True 方便开发 