import sqlite3
import os
from datetime import datetime
import hashlib
import uuid

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
    def get_by_username(username):
        return db.fetch_one("SELECT * FROM users WHERE username = ?", (username,))
    
    @staticmethod
    def get_by_email(email):
        return db.fetch_one("SELECT * FROM users WHERE email = ?", (email,))
    
    @staticmethod
    def create(username, email, password):
        # 生成盐值
        salt = uuid.uuid4().hex
        # 哈希密码
        hashed_password = User.hash_password(password, salt)
        created_at = datetime.now().isoformat()
        
        db.execute(
            "INSERT INTO users (username, email, password_hash, salt, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, email, hashed_password, salt, created_at)
        )
        return db.fetch_one("SELECT * FROM users WHERE username = ?", (username,))
    
    @staticmethod
    def hash_password(password, salt):
        """使用SHA-256哈希密码"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    @staticmethod
    def verify_password(user, password):
        """验证密码是否正确"""
        if not user or 'password_hash' not in user or 'salt' not in user:
            return False
        hashed_password = User.hash_password(password, user['salt'])
        return hashed_password == user['password_hash']
    
    @staticmethod
    def get_user_posts(user_id, limit=None):
        """获取用户的所有帖子"""
        query = "SELECT * FROM posts WHERE user_id = ? ORDER BY date DESC"
        params = (user_id,)
        
        if limit:
            query += f" LIMIT {limit}"
        
        return db.fetch_all(query, params)
    
    @staticmethod
    def get_user_comments(user_id, limit=None):
        """获取用户的所有评论"""
        query = """
            SELECT c.*, p.title as post_title 
            FROM comments c 
            JOIN posts p ON c.postId = p.id 
            WHERE c.user_id = ? 
            ORDER BY c.date DESC
        """
        params = (user_id,)
        
        if limit:
            query += f" LIMIT {limit}"
        
        return db.fetch_all(query, params)
    
    @staticmethod
    def get_user_stats(user_id):
        """获取用户统计信息"""
        # 获取帖子数量
        post_count = db.fetch_one(
            "SELECT COUNT(*) as count FROM posts WHERE user_id = ?", 
            (user_id,)
        )
        
        # 获取评论数量
        comment_count = db.fetch_one(
            "SELECT COUNT(*) as count FROM comments WHERE user_id = ?", 
            (user_id,)
        )
        
        # 获取帖子获得的总点赞数
        post_likes = db.fetch_one(
            "SELECT SUM(likes) as total FROM posts WHERE user_id = ?", 
            (user_id,)
        )
        
        # 获取评论获得的总点赞数
        comment_likes = db.fetch_one(
            "SELECT SUM(likes) as total FROM comments WHERE user_id = ?", 
            (user_id,)
        )
        
        # 计算总点赞数
        total_likes = (post_likes['total'] or 0) + (comment_likes['total'] or 0)
        
        return {
            'post_count': post_count['count'],
            'comment_count': comment_count['count'],
            'total_likes': total_likes
        }
    
    @staticmethod
    def update_email(user_id, email):
        """更新用户邮箱"""
        db.execute(
            "UPDATE users SET email = ? WHERE id = ?",
            (email, user_id)
        )
        return User.get_by_id(user_id)

    @staticmethod
    def count_user_posts(user_id):
        """统计用户的帖子数量"""
        result = db.fetch_one(
            "SELECT COUNT(*) as count FROM posts WHERE user_id = ?",
            (user_id,)
        )
        return result['count'] if result else 0

    @staticmethod
    def count_user_comments(user_id):
        """统计用户的评论数量"""
        result = db.fetch_one(
            "SELECT COUNT(*) as count FROM comments WHERE user_id = ?",
            (user_id,)
        )
        return result['count'] if result else 0

    @staticmethod
    def count_user_total_likes(user_id):
        """统计用户获得的总点赞数"""
        post_likes = db.fetch_one(
            "SELECT SUM(likes) as total FROM posts WHERE user_id = ?",
            (user_id,)
        )
        comment_likes = db.fetch_one(
            "SELECT SUM(likes) as total FROM comments WHERE user_id = ?",
            (user_id,)
        )
        
        post_total = post_likes['total'] if post_likes and post_likes['total'] else 0
        comment_total = comment_likes['total'] if comment_likes and comment_likes['total'] else 0
        
        return post_total + comment_total

class Post:
    @staticmethod
    def get_all():
        """获取所有帖子"""
        return db.fetch_all("SELECT * FROM posts ORDER BY date DESC")
    
    @staticmethod
    def get_by_id(post_id):
        """获取单个帖子"""
        post = db.fetch_one("SELECT * FROM posts WHERE id = ?", (post_id,))
        if post:
            # 获取帖子的评论
            comments = Comment.get_by_post_id(post_id)
            post['comments'] = comments
        return post
    
    @staticmethod
    def create(title, content, author, user_id=None, image_path=None, is_public=0):
        try:
            date = datetime.now().isoformat()
            print(f"创建帖子: title={title}, author={author}, user_id={user_id}, image_path={image_path}, is_public={is_public}")
            
            db.execute(
                "INSERT INTO posts (title, content, author, date, user_id, image_path, is_public) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (title, content, author, date, user_id, image_path, is_public)
            )
            
            # 获取刚刚创建的帖子
            new_post = db.fetch_one(
                "SELECT * FROM posts WHERE title = ? AND author = ? ORDER BY date DESC LIMIT 1", 
                (title, author)
            )
            
            print(f"创建的帖子: {new_post}")
            return new_post
        except Exception as e:
            print(f"创建帖子时出错: {str(e)}")
            raise
    
    @staticmethod
    def update_views(post_id):
        db.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (post_id,))
    
    @staticmethod
    def update_likes(post_id):
        db.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
    
    @staticmethod
    def get_with_author(post_id):
        """获取帖子及其作者信息"""
        query = """
            SELECT p.*, u.username, u.email 
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
        """
        return db.fetch_one(query, (post_id,))
    
    @staticmethod
    def get_all_with_authors():
        """获取所有帖子及其作者信息"""
        query = """
            SELECT p.*, u.username, u.email 
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            ORDER BY p.date DESC
        """
        return db.fetch_all(query)

    @staticmethod
    def increment_views(post_id):
        """增加帖子浏览量"""
        try:
            db.execute(
                "UPDATE posts SET views = views + 1 WHERE id = ?",
                (post_id,)
            )
            return True
        except Exception as e:
            print(f"增加浏览量时出错: {str(e)}")
            return False

    @staticmethod
    def increment_likes(post_id):
        """增加帖子点赞数"""
        db.execute(
            "UPDATE posts SET likes = likes + 1 WHERE id = ?",
            (post_id,)
        )
        return True

    @staticmethod
    def get_all_public():
        """获取所有公开帖子"""
        posts = db.fetch_all("SELECT p.*, u.username as author FROM posts p JOIN users u ON p.user_id = u.id WHERE p.is_public = 1 ORDER BY p.date DESC")
        
        # 处理图片路径
        for post in posts:
            if post['image_path'] and not post['image_path'].startswith('uploads/'):
                post['image_path'] = f"uploads/{post['image_path']}"
        
        return posts

    @staticmethod
    def get_by_user_id(user_id):
        """获取用户的所有帖子"""
        return db.fetch_all(
            "SELECT * FROM posts WHERE user_id = ? ORDER BY date DESC",
            (user_id,)
        )

    @staticmethod
    def update_public_status(post_id, is_public):
        """更新帖子的公开状态"""
        db.execute(
            "UPDATE posts SET is_public = ? WHERE id = ?",
            (is_public, post_id)
        )
        return True

    @staticmethod
    def delete(post_id):
        """删除帖子"""
        # 先删除帖子的所有评论
        db.execute("DELETE FROM comments WHERE postId = ?", (post_id,))
        # 再删除帖子
        db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        return True

    @staticmethod
    def update(story_id, title, content, is_public, image_path=None):
        """更新帖子"""
        try:
            # 构建更新语句
            update_fields = []
            params = []
            
            if title:
                update_fields.append("title = ?")
                params.append(title)
            
            if content:
                update_fields.append("content = ?")
                params.append(content)
            
            update_fields.append("is_public = ?")
            params.append(is_public)
            
            if image_path:
                update_fields.append("image_path = ?")
                params.append(image_path)
            
            # 添加帖子ID
            params.append(story_id)
            
            # 执行更新
            db.execute(
                f"UPDATE posts SET {', '.join(update_fields)} WHERE id = ?",
                tuple(params)
            )
            
            return True
        except Exception as e:
            print(f"更新帖子时出错: {str(e)}")
            return False

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

    @staticmethod
    def get_by_post_id(post_id):
        """获取帖子的所有评论"""
        return db.fetch_all(
            "SELECT * FROM comments WHERE postId = ? ORDER BY date DESC",
            (post_id,)
        )

    @staticmethod
    def get_by_id(comment_id):
        """获取单个评论"""
        return db.fetch_one(
            "SELECT * FROM comments WHERE id = ?",
            (comment_id,)
        )

    @staticmethod
    def increment_likes(comment_id):
        """增加评论点赞数"""
        db.execute(
            "UPDATE comments SET likes = likes + 1 WHERE id = ?",
            (comment_id,)
        )
        return True

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
        # 启用外键约束
        conn.execute("PRAGMA foreign_keys = ON")
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
        # 启用外键约束
        conn.execute("PRAGMA foreign_keys = ON")
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
    
    try:
        # 临时禁用外键约束
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # 读取schema.sql文件并执行
        current_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(current_dir, 'bbs', 'schema.sql')
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            cursor.executescript(f.read())
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"创建表时出错: {e}")
        raise
    finally:
        conn.close()

# 初始化数据库
def init_db(app):
    create_tables()
        
# 确保表在应用启动时被创建
create_tables()
