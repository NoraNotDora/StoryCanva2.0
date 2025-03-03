const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const port = 3000;

app.use(cors());
app.use(bodyParser.json());

// 初始化数据库
const db = new sqlite3.Database('./story.db', (err) => {
    if (err) {
        console.error("Database connection error:", err.message);
    } else {
        console.log('Connected to the story.db database.');
        createTables();
    }
});

// 创建表
function createTables() {
    db.run(`
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            author TEXT,
            date TEXT,
            likes INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0
        )
    `, (err) => {
        if (err) {
            console.error("Error creating posts table:", err.message);
        } else {
            console.log('Posts table created or already exists.');
        }
    });

    db.run(`
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            postId INTEGER,
            content TEXT,
            author TEXT,
            date TEXT,
            likes INTEGER DEFAULT 0,
            FOREIGN KEY (postId) REFERENCES posts(id)
        )
    `, (err) => {
        if (err) {
            console.error("Error creating comments table:", err.message);
        } else {
            console.log('Comments table created or already exists.');
        }
    });
}

// API 接口

// 获取所有帖子
app.get('/api/posts', (req, res) => {
    db.all("SELECT * FROM posts ORDER BY date DESC", [], (err, rows) => {
        if (err) {
            res.status(500).send(err.message);
            return;
        }
        res.json(rows);
    });
});

// 获取单个帖子
app.get('/api/posts/:id', (req, res) => {
    const id = req.params.id;
    db.get("SELECT * FROM posts WHERE id = ?", [id], (err, row) => {
        if (err) {
            res.status(500).send(err.message);
            return;
        }
        if (row) {
            // 增加浏览量 (这里为了简化直接在读取时增加，实际应用中可能需要更严谨的处理)
            db.run("UPDATE posts SET views = views + 1 WHERE id = ?", [id], (updateErr) => {
                if (updateErr) {
                    console.error("Error updating views:", updateErr.message);
                }
                res.json(row);
            });
        } else {
            res.status(404).send('Post not found');
        }
    });
});

// 创建新帖子
app.post('/api/posts', (req, res) => {
    const { title, content, author } = req.body;
    const date = new Date().toISOString();
    db.run("INSERT INTO posts (title, content, author, date) VALUES (?, ?, ?, ?)", [title, content, author, date], function(err) {
        if (err) {
            res.status(500).send(err.message);
            return;
        }
        res.json({ id: this.lastID });
    });
});

// 获取帖子的所有评论
app.get('/api/posts/:postId/comments', (req, res) => {
    const postId = req.params.postId;
    db.all("SELECT * FROM comments WHERE postId = ? ORDER BY date DESC", [postId], (err, rows) => {
        if (err) {
            res.status(500).send(err.message);
            return;
        }
        res.json(rows);
    });
});

// 创建新评论
app.post('/api/comments', (req, res) => {
    const { postId, content, author } = req.body;
    const date = new Date().toISOString();
    db.run("INSERT INTO comments (postId, content, author, date) VALUES (?, ?, ?, ?)", [postId, content, author, date], function(err) {
        if (err) {
            res.status(500).send(err.message);
            return;
        }
        res.json({ id: this.lastID });
    });
});

// 点赞帖子
app.post('/api/posts/:postId/like', (req, res) => {
    const postId = req.params.postId;
    db.run("UPDATE posts SET likes = likes + 1 WHERE id = ?", [postId], function(err) {
        if (err) {
            res.status(500).send(err.message);
            return;
        }
        res.json({ success: true, changes: this.changes });
    });
});

// 点赞评论
app.post('/api/comments/:commentId/like', (req, res) => {
    const commentId = req.params.commentId;
    db.run("UPDATE comments SET likes = likes + 1 WHERE id = ?", [commentId], function(err) {
        if (err) {
            res.status(500).send(err.message);
            return;
        }
        res.json({ success: true, changes: this.changes });
    });
});


app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
}); 