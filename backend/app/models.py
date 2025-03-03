import sqlite3
import os
from datetime import datetime

# 创建一个简单的数据库接口类，替代 SQLAlchemy
class Database:
    def __init__(self):
        self.connection = None
        self.app = None
    
    def init_app(self, app):
        """初始化与Flask应用的连接"""
        self.app = app
        # 注册关闭时的处理函数
        @app.teardown_appcontext
        def close_connection(exception):
            # 如果需要，可以在这里关闭连接
            pass
        return self
    
    def get_connection(self):
        return get_db_connection()
    
    def execute(self, query, params=None):
        conn = self.get_connection()
        try:
            if params:
                result = conn.execute(query, params)
            else:
                result = conn.execute(query)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def fetch_all(self, query, params=None):
        conn = self.get_connection()
        try:
            if params:
                result = conn.execute(query, params).fetchall()
            else:
                result = conn.execute(query).fetchall()
            return [dict(row) for row in result]
        finally:
            conn.close()
    
    def fetch_one(self, query, params=None):
        conn = self.get_connection()
        try:
            if params:
                result = conn.execute(query, params).fetchone()
            else:
                result = conn.execute(query).fetchone()
            return dict(result) if result else None
        finally:
            conn.close()

# 创建数据库实例
db = Database()

# 定义简单的模型类
class User:
    @staticmethod
    def get_all():
        return db.fetch_all("SELECT * FROM users")
    
    @staticmethod
    def get_by_id(user_id):
        return db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
    
    @staticmethod
    def create(username, email, password_hash=None):
        created_at = datetime.now().isoformat()
        db.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, created_at)
        )
        return db.fetch_one("SELECT * FROM users WHERE username = ?", (username,))

class Post:
    @staticmethod
    def get_all():
        return db.fetch_all("SELECT * FROM posts ORDER BY date DESC")
    
    @staticmethod
    def get_by_id(post_id):
        return db.fetch_one("SELECT * FROM posts WHERE id = ?", (post_id,))
    
    @staticmethod
    def create(title, content, author, user_id=None):
        date = datetime.now().isoformat()
        db.execute(
            "INSERT INTO posts (title, content, author, date, user_id) VALUES (?, ?, ?, ?, ?)",
            (title, content, author, date, user_id)
        )
        return db.fetch_one("SELECT * FROM posts WHERE title = ? AND author = ? ORDER BY date DESC LIMIT 1", 
                           (title, author))
    
    @staticmethod
    def update_views(post_id):
        db.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (post_id,))
    
    @staticmethod
    def update_likes(post_id):
        db.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))

class Comment:
    @staticmethod
    def get_by_post_id(post_id):
        return db.fetch_all("SELECT * FROM comments WHERE postId = ? ORDER BY date DESC", (post_id,))
    
    @staticmethod
    def create(post_id, content, author, user_id=None):
        date = datetime.now().isoformat()
        db.execute(
            "INSERT INTO comments (postId, content, author, date, user_id) VALUES (?, ?, ?, ?, ?)",
            (post_id, content, author, date, user_id)
        )
        return db.fetch_one("SELECT * FROM comments WHERE postId = ? AND author = ? ORDER BY date DESC LIMIT 1", 
                           (post_id, author))
    
    @staticmethod
    def update_likes(comment_id):
        db.execute("UPDATE comments SET likes = likes + 1 WHERE id = ?", (comment_id,))

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
            views INTEGER DEFAULT 0,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
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
            user_id INTEGER,
            FOREIGN KEY (postId) REFERENCES posts(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# 初始化数据库
def init_db(app):
    create_tables()
        
# 确保表在应用启动时被创建
create_tables()
