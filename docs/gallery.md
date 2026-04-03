# 用户图库功能实现文档

## 1. 功能概述

用户图库功能允许用户：
- 上传和管理个人图片
- 查看存储空间使用情况
- 为图片添加描述
- 删除已上传的图片
- 管理个人头像

## 2. 数据库设计

### 2.1 表结构

```sql
CREATE TABLE user_gallery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    image_name TEXT NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    image_size INTEGER NOT NULL,
    image_type TEXT NOT NULL,
    is_avatar INTEGER DEFAULT 0,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_gallery_user_id ON user_gallery(user_id);
CREATE INDEX idx_user_gallery_upload_date ON user_gallery(upload_date);
CREATE INDEX idx_user_gallery_is_avatar ON user_gallery(is_avatar);
```

### 2.2 字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID，外键关联users表 |
| image_path | TEXT | 图片存储路径 |
| image_name | TEXT | 原始图片名称 |
| upload_date | DATETIME | 上传时间 |
| image_size | INTEGER | 图片大小（字节） |
| image_type | TEXT | 图片类型（如jpg, png等） |
| is_avatar | INTEGER | 是否为头像（0否1是） |
| description | TEXT | 图片描述 |

## 3. 系统架构

### 3.1 文件结构

```
project/
├── backend/
│   ├── app/
│   │   ├── models.py      # 数据模型
│   │   ├── views.py       # 视图函数
│   │   └── __init__.py
├── frontend/
│   ├── static/
│   │   └── uploads/       # 图片存储目录
│   └── templates/
│       └── gallery.html   # 图库页面模板
```

### 3.2 存储规则

- 图片存储路径格式：`uploads/<user_id>/<uuid>.<ext>`
- 支持的图片格式：jpg, jpeg, png, gif
- 单个文件大小限制：2MB
- 用户总存储空间：50MB

## 4. 核心功能实现

### 4.1 图片上传

```python
@app.route('/gallery/upload', methods=['POST'])
@login_required
def upload_image():
    # 文件验证
    # 空间检查
    # 文件保存
    # 数据库记录
```

关键步骤：
1. 验证文件类型和大小
2. 检查用户存储空间
3. 生成唯一文件名
4. 创建用户专属目录
5. 保存文件并记录信息

### 4.2 图片管理

```python
class UserGallery:
    @staticmethod
    def get_user_images(user_id):
        # 获取用户图片列表
    
    @staticmethod
    def delete_image(image_id, user_id):
        # 删除指定图片
```

### 4.3 存储空间管理

```python
def get_user_storage_usage(user_id):
    # 计算用户已使用空间
```

## 5. 安全措施

### 5.1 文件安全
- 使用 `secure_filename` 处理文件名
- 使用 UUID 生成唯一文件名
- 验证文件类型和大小
- 用户目录隔离

### 5.2 访问控制
- 登录验证
- 用户权限检查
- 防止未授权访问

## 6. 前端实现

### 6.1 页面组件
- 存储空间使用显示
- 图片上传表单
- 图片预览
- 图片网格展示
- 删除确认对话框

### 6.2 交互功能
- 实时图片预览
- 上传进度反馈
- 删除确认
- 错误提示

## 7. 性能优化

### 7.1 数据库优化
- 索引优化
- 分页加载
- 定期清理

### 7.2 存储优化
- 图片压缩
- 缓存策略
- 异步处理

## 8. 注意事项

### 8.1 限制条件
- 文件大小限制：2MB/个
- 总空间限制：50MB/用户
- 支持的文件类型：jpg, jpeg, png, gif

### 8.2 维护建议
- 定期清理无效文件
- 监控存储空间使用
- 备份重要数据
- 日志记录和分析

## 9. 未来扩展

### 9.1 功能扩展
- 图片编辑功能
- 相册分类
- 图片分享
- 批量上传
- 图片压缩选项

### 9.2 性能扩展
- CDN支持
- 分布式存储
- 图片处理服务
