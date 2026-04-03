# 数据库概要设计

## 4.3.1 逻辑设计

### 4.3.1.1 实体关系模型

系统主要包含以下实体：

1. 用户（User）
   - 属性：id, username, email, password_hash, salt, created_at
   - 关系：一对多（与帖子、评论、图库）

2. 帖子（Post）
   - 属性：id, title, content, author, date, user_id, image_path, is_public, views, likes
   - 关系：多对一（与用户）、一对多（与评论）

3. 评论（Comment）
   - 属性：id, content, author, date, postId, user_id, likes
   - 关系：多对一（与用户、帖子）

4. 用户图库（UserGallery）
   - 属性：id, user_id, image_path, image_name, upload_date, image_size, image_type, is_avatar, description
   - 关系：多对一（与用户）

### 4.3.1.2 数据字典

#### 用户表（users）
| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INTEGER | 用户ID | 主键 |
| username | TEXT | 用户名 | 非空，唯一 |
| email | TEXT | 邮箱 | 非空，唯一 |
| password_hash | TEXT | 密码哈希 | 非空 |
| salt | TEXT | 密码盐值 | 非空 |
| created_at | TEXT | 创建时间 | 非空 |

#### 帖子表（posts）
| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INTEGER | 帖子ID | 主键 |
| title | TEXT | 标题 | 非空 |
| content | TEXT | 内容 | 非空 |
| author | TEXT | 作者名 | 非空 |
| date | TEXT | 发布时间 | 非空 |
| user_id | INTEGER | 用户ID | 外键 |
| image_path | TEXT | 图片路径 | 可空 |
| is_public | INTEGER | 是否公开 | 默认0 |
| views | INTEGER | 浏览量 | 默认0 |
| likes | INTEGER | 点赞数 | 默认0 |

#### 评论表（comments）
| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INTEGER | 评论ID | 主键 |
| content | TEXT | 评论内容 | 非空 |
| author | TEXT | 评论作者 | 非空 |
| date | TEXT | 评论时间 | 非空 |
| postId | INTEGER | 帖子ID | 外键 |
| user_id | INTEGER | 用户ID | 外键 |
| likes | INTEGER | 点赞数 | 默认0 |

#### 用户图库表（user_gallery）
| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INTEGER | 图片ID | 主键 |
| user_id | INTEGER | 用户ID | 外键 |
| image_path | TEXT | 图片存储路径 | 非空 |
| image_name | TEXT | 原始图片名称 | 非空 |
| upload_date | DATETIME | 上传时间 | 默认当前时间 |
| image_size | INTEGER | 图片大小(字节) | 非空 |
| image_type | TEXT | 图片类型 | 非空 |
| is_avatar | INTEGER | 是否为头像 | 默认0 |
| description | TEXT | 图片描述 | 可空 |

## 4.3.2 物理设计

### 4.3.2.1 数据库选型

系统采用SQLite作为数据库系统，原因如下：
1. 轻量级，无需额外安装数据库服务器
2. 适合中小型应用，支持完整的SQL功能
3. 文件型数据库，便于部署和备份
4. 支持事务处理，保证数据一致性

### 4.3.2.2 存储结构

1. 数据库文件
   - 位置：项目根目录下的`instance`文件夹
   - 文件名：`storycanva.sqlite`
   - 文件格式：SQLite3数据库文件

2. 索引设计
   - users表：username和email字段建立唯一索引
   - posts表：user_id和date字段建立索引
   - comments表：postId和user_id字段建立索引
   - user_gallery表：
     - user_id字段建立索引
     - upload_date字段建立索引
     - is_avatar字段建立索引

3. 文件存储
   - 图片文件存储在 `static/uploads/<user_id>/` 目录下
   - 使用UUID生成唯一文件名
   - 按用户ID分目录存储，便于管理

### 4.3.2.3 性能优化

1. 查询优化
   - 使用参数化查询防止SQL注入
   - 合理使用索引提高查询效率
   - 实现连接池管理数据库连接

2. 数据安全
   - 密码使用SHA-256加盐哈希存储
   - 实现事务管理确保数据一致性
   - 定期备份数据库文件
   - 图片存储大小限制（单个2MB，总计50MB/用户）
   - 文件类型验证（仅允许jpg、jpeg、png、gif）

3. 缓存策略
   - 实现数据库连接池
   - 热门帖子数据缓存
   - 用户会话信息缓存
   - 图片访问路径缓存

4. 存储优化
   - 图片按用户分目录存储
   - 定期清理未引用的图片文件
   - 监控用户存储空间使用情况 