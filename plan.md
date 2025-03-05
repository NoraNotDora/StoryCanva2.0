# 前后端分离

## 前端
bootstrap+js+html

## 后端
flask

## 数据库
sqlite

## 项目结构
MVC架构参考：https://blog.csdn.net/m0_54701273/article/details/142551525

## 功能实现
- 用户登录和注册

Q:怎样完善登录和注册？
users
  |
  |-- posts (一对多: 一个用户可以发布多个帖子)
  |     |
  |     |-- comments (一对多: 一个帖子可以有多个评论)
  |     |
  |     |-- post_tags (多对多: 一个帖子可以有多个标签，一个标签可以应用于多个帖子)
  |           |
  |           |-- tags
  |
  |-- comments (一对多: 一个用户可以发表多个评论)
  |
  |-- roles (多对一: 多个用户可以有相同的角色)


- 成就解锁
- 整合collage diffusion
- 补充对话界面（可能可以用react做？）

对话参考：https://www.51cto.com/article/802283.html

https://github.com/codecaine-zz/llm_bootstrap5_template/tree/main