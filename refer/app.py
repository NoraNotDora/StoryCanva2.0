from flask import Flask, render_template,request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os


app = Flask(__name__)
app.template_folder = '../frontend/templates/'
app.static_folder = '../frontend/static/'
CORS(app)

# 连接数据库
DATABASE = './bbs/story.db'

# 数据库连接设置
def get_db_connection():
    try:
        # 获取当前文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建数据库的绝对路径
        db_path = os.path.join(current_dir, 'bbs', 'story.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"数据库连接错误: {e}")
        # 如果连接失败，尝试创建新的数据库文件
        create_new_database()
        # 再次尝试连接
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'bbs', 'story.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

# 创建新的数据库函数
def create_new_database():
    try:
        # 获取当前文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 确保bbs目录存在
        bbs_dir = os.path.join(current_dir, 'bbs')
        os.makedirs(bbs_dir, exist_ok=True)
        
        # 构建数据库的绝对路径
        db_path = os.path.join(bbs_dir, 'story.db')
        
        # 创建新的数据库连接
        conn = sqlite3.connect(db_path)
        
        # 读取schema.sql文件并执行
        schema_path = os.path.join(bbs_dir, 'schema.sql')
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
        
        conn.commit()
        conn.close()
        print(f"成功创建新的数据库文件: {db_path}")
    except Exception as e:
        print(f"创建数据库时出错: {e}")
        raise

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

# 基础路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/achievement')
def achievement():
    return render_template('achievement.html')

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/detail.html')
def serve_detail():
    return render_template('detail.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(app.static_folder, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(app.static_folder, 'js'), filename)

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(app.static_folder, 'images'), filename)

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



@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

# 将debug判断移到路由注册之后
if __name__ == '__main__':
    import datetime #  导入 datetime 模块

    # 先设置debug模式
    app.debug = True

    #  检查数据库文件是否存在，如果不存在则初始化数据库
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'bbs', 'story.db')
    if not os.path.exists(db_path):
        create_new_database()
    
    # 注册测试路由（仅在开发模式）
    if app.debug:
        @app.route('/base')
        def show_base_template():
            return render_template('base.html')
    
    app.run(debug=True, port=5000) 