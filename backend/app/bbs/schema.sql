-- 启用外键约束
PRAGMA foreign_keys = ON;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- 创建帖子表
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author TEXT,
    date TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    user_id INTEGER,
    image_path TEXT,
    is_public INTEGER DEFAULT 0,  -- 0表示私有，1表示公开
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建评论表
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
);