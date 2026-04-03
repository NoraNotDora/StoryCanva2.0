# StoryCanva 设计规范

## 1. 系统主色
### 主题色（Primary Color）
- **标准橙色** `#FF6B4A`
  - 使用场景：
    - 主要按钮背景
    - 卡片标题栏背景
    - 重要标签背景
    - 强调性图标

### 主题色变体
- **浅色橙** `#FF8B6E`
  - 使用场景：
    - 滚动条
    - 悬停状态
    - 次要强调
- **深色橙** `#E65B3E`
  - 使用场景：
    - 按钮悬停状态
    - 重要操作的激活状态

## 2. 辅助色
### 交互状态色
- **悬停背景色** `rgba(255, 107, 74, 0.05)`
  - 使用场景：
    - 列表项悬停效果
    - 卡片悬停效果
    - 轻量级强调

### 功能色
- **次要灰色** `#6c757d`
  - 使用场景：
    - 次要按钮
    - 私密标签
    - 辅助文本

## 3. 文本色
- **主要文本** `#212529`（Bootstrap 默认）
- **次要文本** `#6c757d`（Bootstrap 文本静音色）
- **白色文本** `#FFFFFF`（用于深色背景）

## 4. 边框与阴影
### 阴影效果
- **卡片阴影** `0 .125rem .25rem rgba(0,0,0,.075)`
- **头像阴影** `0 0 15px rgba(0,0,0,0.1)`

## 5. 使用规范

### 按钮样式
```css
/* 主要按钮 */
.btn-primary {
    background-color: #FF6B4A;
    border-color: #FF6B4A;
}
.btn-primary:hover {
    background-color: #E65B3E;
    border-color: #E65B3E;
}

/* 轮廓按钮 */
.btn-outline-primary {
    color: #FF6B4A;
    border-color: #FF6B4A;
}
.btn-outline-primary:hover {
    color: white;
    background-color: #FF6B4A;
}
```

### 标签样式
```css
.badge.theme-bg {
    background-color: #FF6B4A;
    padding: 0.4em 0.6em;
    font-weight: 500;
}
```

### 卡片样式
```css
.card {
    border: none;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 .125rem .25rem rgba(0,0,0,.075);
}

.card-header.theme-bg {
    background-color: #FF6B4A;
    border-color: #FF6B4A;
    color: white;
}
```

## 6. 可访问性建议
- 确保文本在主题色背景上有足够的对比度
- 使用适当的文本大小和字重来增强可读性
- 为交互元素提供清晰的视觉反馈
- 考虑色盲用户的需求，搭配适当的图标

## 7. CSS 变量定义
```css
:root {
    --theme-color: #FF6B4A;
    --theme-color-light: #FF8B6E;
    --theme-color-dark: #E65B3E;
    --theme-hover: rgba(255, 107, 74, 0.05);
}
```

## 8. 注意事项
1. 保持色彩使用的一致性
2. 遵循品牌主色在重要元素上的应用
3. 合理使用辅助色，避免喧宾夺主
4. 确保界面配色符合 WCAG 2.0 可访问性标准
5. 在开发新功能时优先使用已定义的色彩变量
