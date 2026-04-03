-- 启用外键约束
PRAGMA foreign_keys = ON;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TEXT NOT NULL,
    avatar_path TEXT DEFAULT 'picture/default_avatar.png',
    nickname TEXT,
    age INTEGER CHECK (age BETWEEN 5 AND 9),
    gender TEXT CHECK (gender IN ('boy', 'girl', 'neutral')),
    favorite_colors TEXT,  -- JSON数组存储
    story_preferences TEXT,  -- JSON数组存储
    favorite_characters TEXT,  -- JSON数组存储
    fear_list TEXT,  -- JSON数组存储
    language_level TEXT DEFAULT 'basic'  -- basic(5-6岁) 或 advanced(7-9岁)
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