// 导入 SQL.js
import initSqlJs from './sql-wasm.js';

// 创建数据库类
class Database {
    constructor() {
        this.db = null;
        this.SQL = null;
        this.ready = this.init();
        this.posts = new PostsTable(this);
        this.comments = new CommentsTable(this);
    }

    // 初始化 SQL.js
    async init() {
        console.log('初始化 SQL.js 数据库...');
        try {
            // 初始化 SQL.js
            this.SQL = await initSqlJs({
                locateFile: file => `./static/js/${file}`
            });
            
            // 创建新的数据库
            this.db = new this.SQL.Database();
            
            // 创建表
            this.db.run(`
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    section TEXT NOT NULL,
                    author TEXT NOT NULL,
                    time TEXT NOT NULL,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    image TEXT
                )
            `);
            
            this.db.run(`
                CREATE TABLE IF NOT EXISTS comments (
                    id TEXT PRIMARY KEY,
                    postId TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author TEXT NOT NULL,
                    time TEXT NOT NULL,
                    likes INTEGER DEFAULT 0,
                    FOREIGN KEY (postId) REFERENCES posts(id)
                )
            `);
            
            // 检查是否需要添加示例数据
            const result = this.db.exec("SELECT COUNT(*) as count FROM posts");
            const count = result[0].values[0][0];
            
            if (count === 0) {
                await this.addSampleData();
            } else {
                console.log('数据库已有数据，跳过初始化');
            }
            
            console.log('SQL.js 数据库初始化完成');
            return true;
        } catch (error) {
            console.error('SQL.js 数据库初始化失败:', error);
            throw error;
        }
    }
    
    // 添加示例数据
    async addSampleData() {
        console.log('添加示例数据...');
        
        // 添加示例帖子
        const samplePosts = [
            {
                id: '1678901234567',
                title: '欢迎来到社区论坛',
                content: '这是我们社区的第一个帖子，希望大家能在这里分享有趣的故事和经验！',
                section: '公告',
                author: '管理员',
                time: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
                likes: 5,
                comments: 2,
                image: null
            },
            {
                id: '1678901234568',
                title: '分享一个有趣的经历',
                content: '今天在路上遇到了一只非常友好的小猫，它一直跟着我走了很长一段路...',
                section: '日常',
                author: '猫咪爱好者',
                time: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
                likes: 10,
                comments: 3,
                image: null
            }
        ];
        
        // 添加示例评论
        const sampleComments = [
            {
                id: '1678901234569',
                postId: '1678901234567',
                content: '欢迎欢迎！期待这个社区的发展！',
                author: '新用户',
                time: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
                likes: 2
            },
            {
                id: '1678901234570',
                postId: '1678901234567',
                content: '希望能在这里认识更多朋友！',
                author: '社区成员',
                time: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
                likes: 1
            },
            {
                id: '1678901234571',
                postId: '1678901234568',
                content: '好可爱的猫咪，有照片吗？',
                author: '爱猫人士',
                time: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
                likes: 3
            },
            {
                id: '1678901234572',
                postId: '1678901234568',
                content: '我也有类似的经历，猫咪真的很有灵性！',
                author: '动物爱好者',
                time: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
                likes: 2
            },
            {
                id: '1678901234573',
                postId: '1678901234568',
                content: '希望下次能看到这只猫咪的照片！',
                author: '摄影师',
                time: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
                likes: 1
            }
        ];
        
        // 批量添加示例数据
        for (const post of samplePosts) {
            await this.posts.add(post);
        }
        
        for (const comment of sampleComments) {
            await this.comments.add(comment);
        }
        
        console.log('示例数据添加完成');
    }
    
    // 保存数据库到本地存储
    saveToLocalStorage() {
        if (!this.db) return;
        
        try {
            const data = this.db.export();
            const buffer = new Uint8Array(data);
            const blob = new Blob([buffer], { type: 'application/octet-stream' });
            const base64 = arrayBufferToBase64(blob);
            localStorage.setItem('sqliteDB', base64);
            console.log('数据库已保存到本地存储');
        } catch (error) {
            console.error('保存数据库失败:', error);
        }
    }
    
    // 从本地存储加载数据库
    loadFromLocalStorage() {
        if (!this.SQL) return false;
        
        try {
            const base64 = localStorage.getItem('sqliteDB');
            if (!base64) return false;
            
            const binaryString = window.atob(base64);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            
            this.db = new this.SQL.Database(bytes);
            console.log('从本地存储加载数据库成功');
            return true;
        } catch (error) {
            console.error('加载数据库失败:', error);
            return false;
        }
    }
}

// 帖子表操作类
class PostsTable {
    constructor(database) {
        this.database = database;
    }
    
    // 添加帖子
    async add(post) {
        await this.database.ready;
        
        const stmt = this.database.db.prepare(`
            INSERT INTO posts (id, title, content, section, author, time, likes, comments, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);
        
        stmt.run([
            post.id,
            post.title,
            post.content,
            post.section,
            post.author,
            post.time,
            post.likes || 0,
            post.comments || 0,
            post.image || null
        ]);
        
        stmt.free();
        this.database.saveToLocalStorage();
        return post.id;
    }
    
    // 获取帖子
    async get(id) {
        await this.database.ready;
        
        const stmt = this.database.db.prepare(`
            SELECT * FROM posts WHERE id = ?
        `);
        
        stmt.bind([id]);
        const result = stmt.step();
        
        if (!result) {
            stmt.free();
            return null;
        }
        
        const post = this.rowToObject(stmt.getAsObject());
        stmt.free();
        return post;
    }
    
    // 更新帖子
    async put(post) {
        await this.database.ready;
        
        const stmt = this.database.db.prepare(`
            UPDATE posts
            SET title = ?, content = ?, section = ?, author = ?, time = ?, likes = ?, comments = ?, image = ?
            WHERE id = ?
        `);
        
        stmt.run([
            post.title,
            post.content,
            post.section,
            post.author,
            post.time,
            post.likes || 0,
            post.comments || 0,
            post.image || null,
            post.id
        ]);
        
        stmt.free();
        this.database.saveToLocalStorage();
        return post.id;
    }
    
    // 删除帖子
    async delete(id) {
        await this.database.ready;
        
        const stmt = this.database.db.prepare(`
            DELETE FROM posts WHERE id = ?
        `);
        
        stmt.run([id]);
        stmt.free();
        
        // 同时删除相关评论
        const commentsStmt = this.database.db.prepare(`
            DELETE FROM comments WHERE postId = ?
        `);
        
        commentsStmt.run([id]);
        commentsStmt.free();
        
        this.database.saveToLocalStorage();
        return true;
    }
    
    // 获取所有帖子
    async toArray() {
        await this.database.ready;
        
        const result = this.database.db.exec(`
            SELECT * FROM posts
        `);
        
        if (!result || result.length === 0) {
            return [];
        }
        
        const columns = result[0].columns;
        const posts = result[0].values.map(row => {
            const post = {};
            columns.forEach((col, index) => {
                post[col] = row[index];
            });
            return this.rowToObject(post);
        });
        
        return posts;
    }
    
    // 按时间排序
    orderBy(field) {
        return {
            reverse: async () => {
                await this.database.ready;
                
                const result = this.database.db.exec(`
                    SELECT * FROM posts ORDER BY ${field} DESC
                `);
                
                if (!result || result.length === 0) {
                    return [];
                }
                
                const columns = result[0].columns;
                const posts = result[0].values.map(row => {
                    const post = {};
                    columns.forEach((col, index) => {
                        post[col] = row[index];
                    });
                    return this.rowToObject(post);
                });
                
                return posts;
            },
            toArray: async () => {
                await this.database.ready;
                
                const result = this.database.db.exec(`
                    SELECT * FROM posts ORDER BY ${field} ASC
                `);
                
                if (!result || result.length === 0) {
                    return [];
                }
                
                const columns = result[0].columns;
                const posts = result[0].values.map(row => {
                    const post = {};
                    columns.forEach((col, index) => {
                        post[col] = row[index];
                    });
                    return this.rowToObject(post);
                });
                
                return posts;
            }
        };
    }
    
    // 获取帖子数量
    async count() {
        await this.database.ready;
        
        const result = this.database.db.exec(`
            SELECT COUNT(*) as count FROM posts
        `);
        
        return result[0].values[0][0];
    }
    
    // 将数据库行转换为对象
    rowToObject(row) {
        return {
            id: row.id,
            title: row.title,
            content: row.content,
            section: row.section,
            author: row.author,
            time: row.time,
            likes: row.likes,
            comments: row.comments,
            image: row.image
        };
    }
}

// 评论表操作类
class CommentsTable {
    constructor(database) {
        this.database = database;
    }
    
    // 添加评论
    async add(comment) {
        await this.database.ready;
        
        const stmt = this.database.db.prepare(`
            INSERT INTO comments (id, postId, content, author, time, likes)
            VALUES (?, ?, ?, ?, ?, ?)
        `);
        
        stmt.run([
            comment.id,
            comment.postId,
            comment.content,
            comment.author,
            comment.time,
            comment.likes || 0
        ]);
        
        stmt.free();
        this.database.saveToLocalStorage();
        return comment.id;
    }
    
    // 获取评论
    async get(id) {
        await this.database.ready;
        
        const stmt = this.database.db.prepare(`
            SELECT * FROM comments WHERE id = ?
        `);
        
        stmt.bind([id]);
        const result = stmt.step();
        
        if (!result) {
            stmt.free();
            return null;
        }
        
        const comment = this.rowToObject(stmt.getAsObject());
        stmt.free();
        return comment;
    }
    
    // 更新评论
    async put(comment) {
        await this.database.ready;
        
        const stmt = this.database.db.prepare(`
            UPDATE comments
            SET postId = ?, content = ?, author = ?, time = ?, likes = ?
            WHERE id = ?
        `);
        
        stmt.run([
            comment.postId,
            comment.content,
            comment.author,
            comment.time,
            comment.likes || 0,
            comment.id
        ]);
        
        stmt.free();
        this.database.saveToLocalStorage();
        return comment.id;
    }
    
    // 删除评论
    async delete(id) {
        await this.database.ready;
        
        const stmt = this.database.db.prepare(`
            DELETE FROM comments WHERE id = ?
        `);
        
        stmt.run([id]);
        stmt.free();
        this.database.saveToLocalStorage();
        return true;
    }
    
    // 查询评论
    where(field) {
        return {
            equals: (value) => {
                return {
                    sortBy: async (sortField) => {
                        await this.database.ready;
                        
                        const result = this.database.db.exec(`
                            SELECT * FROM comments 
                            WHERE ${field} = ? 
                            ORDER BY ${sortField} ASC
                        `, [value]);
                        
                        if (!result || result.length === 0) {
                            return [];
                        }
                        
                        const columns = result[0].columns;
                        const comments = result[0].values.map(row => {
                            const comment = {};
                            columns.forEach((col, index) => {
                                comment[col] = row[index];
                            });
                            return this.rowToObject(comment);
                        });
                        
                        return comments;
                    }
                };
            }
        };
    }
    
    // 获取所有评论
    async toArray() {
        await this.database.ready;
        
        const result = this.database.db.exec(`
            SELECT * FROM comments
        `);
        
        if (!result || result.length === 0) {
            return [];
        }
        
        const columns = result[0].columns;
        const comments = result[0].values.map(row => {
            const comment = {};
            columns.forEach((col, index) => {
                comment[col] = row[index];
            });
            return this.rowToObject(comment);
        });
        
        return comments;
    }
    
    // 将数据库行转换为对象
    rowToObject(row) {
        return {
            id: row.id,
            postId: row.postId,
            content: row.content,
            author: row.author,
            time: row.time,
            likes: row.likes
        };
    }
}

// 辅助函数：ArrayBuffer 转 Base64
function arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
}

// 创建数据库实例
const db = new Database();

// 导出数据库实例
export { db };
