// 修改全局变量，指向后端API地址
const API_BASE_URL = 'http://localhost:5000/api';

// 弹出 帖子输入的框---【去掉默认隐藏为显示，设置display = "block";】
function post(){
    var inp = document.getElementsByClassName("post");
    inp[0].style.display = "block";
}	 
    
// 点击发布
function postSuccess(){
    //隐藏发布框
    var inp = document.getElementsByClassName("post");
    inp[0].style.display = "none";   
    
    const title = document.getElementById('title').value;
    const content = document.getElementById('content').value;
    const author = document.getElementById('author').value;

    if (title && content) {
        fetch(`${API_BASE_URL}/posts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, content, author })
        })
        .then(response => response.json())
        .then(data => {
            console.log('帖子发布成功:', data);
            // 清空表单
            document.getElementById('title').value = '';
            document.getElementById('content').value = '';
            document.getElementById('author').value = '';
            // 重新加载帖子列表
            console.log('发布成功后，准备加载帖子列表...'); // 添加调试日志
            loadPosts();
            console.log('帖子列表加载函数调用完毕。'); // 添加调试日志
        })
        .catch(error => {
            console.error('发布帖子失败:', error);
        });
    }
}

function getTime(){
     // 1、获取当前的日期
     var date = new Date();
    var m = (date.getMonth()+1)>9?(date.getMonth()+1):"0"+(date.getMonth()+1);
    var min = (date.getMinutes())>9?(date.getMinutes()):"0"+(date.getMinutes());
    var se = (date.getSeconds())>9?(date.getSeconds()):"0"+(date.getSeconds);
    var cl = date.getFullYear()+"年"+m+"月"+date.getDate()+"日\t"+date.getHours()+"时"+min+"分"+date.getSeconds()+"秒";
    return cl;
}

document.addEventListener('DOMContentLoaded', function() {
    loadPosts(); // 加载帖子列表

    // 添加帖子表单提交事件
    document.getElementById('post-form').addEventListener('submit', function(e) {
        e.preventDefault();
        postSuccess(); // 调用 postSuccess 函数处理帖子提交
    });
});

// 加载帖子列表
function loadPosts() {
    console.log('开始加载帖子列表...'); // 添加调试日志
    const postsList = document.getElementById('postul');
    postsList.innerHTML = '';
    
    fetch(`${API_BASE_URL}/posts`)
        .then(response => response.json())
        .then(posts => {
            console.log('成功获取帖子列表:', posts); // 添加调试日志
            if (posts.length === 0) {
                postsList.innerHTML = '<p>暂无帖子，快来发表第一篇吧！</p>';
                return;
            }
            
            posts.forEach(post => {
                const postElement = document.createElement('div');
                postElement.className = 'post-item';
                postElement.innerHTML = `
                    <h3><a href="#" class="post-link" data-id="${post.id}">${post.title}</a></h3>
                    <p class="post-meta">作者: ${post.author} | 发布时间: ${formatDate(post.date)} | 浏览: ${post.views} | 点赞: ${post.likes}</p>
                `;
                postsList.appendChild(postElement);
                
                // 添加点击事件
                postElement.querySelector('.post-link').addEventListener('click', function(e) {
                    e.preventDefault();
                    const postId = this.getAttribute('data-id');
                    showPostDetail(postId);
                });
            });
            console.log('帖子列表加载完成并显示。'); // 添加调试日志
        })
        .catch(error => {
            console.error('加载帖子列表失败:', error);
            postsList.innerHTML = '<p>加载帖子列表失败，请稍后重试。</p>';
        });
}

// 显示帖子详情
function showPostDetail(postId) {
    // 跳转到 detail.html，并传递 postId 参数
    window.location.href = `detail.html?id=${postId}`;
}

// 加载评论
function loadComments(postId) {
    const commentsList = document.getElementById('comments-list');
    commentsList.innerHTML = '';
    
    fetch(`${API_BASE_URL}/posts/${postId}/comments`)
        .then(response => response.json())
        .then(comments => {
            if (comments.length === 0) {
                commentsList.innerHTML = '<p>暂无评论，快来发表第一条评论吧！</p>';
                return;
            }
            
            comments.forEach(comment => {
                const commentElement = document.createElement('div');
                commentElement.className = 'comment-item';
                commentElement.innerHTML = `
                    <p class="comment-meta">作者: ${comment.author} | 发布时间: ${formatDate(comment.date)} | 点赞: ${comment.likes}</p>
                    <div class="comment-content">${comment.content}</div>
                    <button class="like-comment" data-id="${comment.id}">点赞</button>
                `;
                commentsList.appendChild(commentElement);
                
                // 添加评论点赞事件
                commentElement.querySelector('.like-comment').addEventListener('click', function() {
                    const commentId = this.getAttribute('data-id');
                    likeComment(commentId);
                });
            });
        })
        .catch(error => {
            console.error('加载评论失败:', error);
            commentsList.innerHTML = '<p>加载评论失败，请稍后重试。</p>';
        });
}

// 保存评论
function saveComment(postId, content, author) {
    return fetch(`${API_BASE_URL}/comments`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ postId: Number(postId), content, author })
    })
    .then(response => response.json())
    .then(data => {
        console.log('评论保存成功:', data);
        return data;
    })
    .catch(error => {
        console.error('保存评论失败:', error);
        throw error;
    });
}

// 点赞帖子
function likePost(postId) {
    fetch(`${API_BASE_URL}/posts/${postId}/like`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新UI
            const likeButton = document.getElementById('like-post');
            const postMeta = likeButton.parentElement.querySelector('.post-meta');
            let currentLikes = parseInt(postMeta.textContent.match(/点赞: (\d+)/)[1]);
            postMeta.innerHTML = postMeta.innerHTML.replace(/点赞: \d+/, `点赞: ${currentLikes + 1}`);
        }
    })
    .catch(error => {
        console.error('点赞帖子失败:', error);
    });
}

// 点赞评论
function likeComment(commentId) {
    fetch(`${API_BASE_URL}/comments/${commentId}/like`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新UI
            const likeButton = document.querySelector(`.like-comment[data-id="${commentId}"]`);
            const commentMeta = likeButton.parentElement.querySelector('.comment-meta');
            let currentLikes = parseInt(commentMeta.textContent.match(/点赞: (\d+)/)[1]);
            commentMeta.innerHTML = commentMeta.innerHTML.replace(/点赞: \d+/, `点赞: ${currentLikes + 1}`);
        }
    })
    .catch(error => {
        console.error('点赞评论失败:', error);
    });
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return `${date.getFullYear()}-${padZero(date.getMonth() + 1)}-${padZero(date.getDate())} ${padZero(date.getHours())}:${padZero(date.getMinutes())}`;
}

// 补零
function padZero(num) {
    return num < 10 ? '0' + num : num;
}
