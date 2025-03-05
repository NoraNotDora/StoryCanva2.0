const API_BASE_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const postId = urlParams.get('id');

    if (!postId) {
        document.getElementById('post-detail').innerHTML = '<div class="error">未找到帖子ID</div>';
        return;
    }

    // 获取帖子详情
    fetch(`${API_BASE_URL}/posts/${postId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('帖子获取失败');
            }
            return response.json();
        })
        .then(post => {
            // 构建帖子详情HTML
            let postHTML = `
                <div class="post-header">
                    <h1>${post.title}</h1>
                    <div class="post-meta">
                        <span>作者: ${post.author}</span>
                        <span>发布时间: ${post.date}</span>
                        <span><i class="fas fa-eye"></i> ${post.views}</span>
                        <span><i class="fas fa-heart"></i> ${post.likes}</span>
                    </div>
                </div>
                <div class="post-content">
                    ${post.content}
                    ${post.image_path ? `
                    <div class="post-image">
                        <img src="${post.image_path.startsWith('/') ? post.image_path : '/' + post.image_path}" 
                             class="img-fluid rounded" alt="故事插图">
                    </div>` : ''}
                </div>
                <div class="post-actions">
                    <button id="like-post" onclick="likePost(${post.id})">
                        <i class="fas fa-heart"></i> 点赞 (${post.likes})
                    </button>
                </div>
            `;
            
            // 添加评论部分
            postHTML += `
                <div class="comments-section">
                    <h3>评论 (${post.comments ? post.comments.length : 0})</h3>
                    <div class="comment-form">
                        <textarea id="comment-content" placeholder="写下你的评论..."></textarea>
                        <button onclick="submitComment(${post.id})">发表评论</button>
                    </div>
                    <div class="comments-list" id="comments-list">
                    </div>
                </div>
            `;
            
            document.getElementById('post-detail').innerHTML = postHTML;
            
            // 加载评论
            loadComments(postId);
        })
        .catch(error => {
            console.error('获取帖子详情失败:', error);
            document.getElementById('post-detail').innerHTML = `
                <div class="error">
                    <p>获取帖子详情失败</p>
                    <p>${error.message}</p>
                </div>
            `;
        });

    // 返回列表按钮事件
    document.getElementById('back-to-index').addEventListener('click', function() {
        console.log('返回列表按钮被点击了！'); // 添加调试信息
        window.location.href = 'index.html'; // 返回到 index.html
    });
});

// 加载评论
function loadComments(postId) {
    fetch(`${API_BASE_URL}/posts/${postId}/comments`)
        .then(response => response.json())
        .then(comments => {
            const commentsListElement = document.getElementById('comments-list');
            
            if (!comments || comments.length === 0) {
                commentsListElement.innerHTML = '<div class="no-comments">暂无评论，快来发表第一条评论吧！</div>';
                return;
            }
            
            let commentsHTML = '';
            comments.forEach(comment => {
                commentsHTML += `
                    <div class="comment">
                        <div class="comment-header">
                            <span class="comment-author">${comment.author}</span>
                            <span class="comment-date">${comment.date}</span>
                        </div>
                        <div class="comment-content">${comment.content}</div>
                        <div class="comment-actions">
                            <button onclick="likeComment(${comment.id})">
                                <i class="fas fa-heart"></i> 点赞 (${comment.likes})
                            </button>
                        </div>
                    </div>
                `;
            });
            
            commentsListElement.innerHTML = commentsHTML;
        })
        .catch(error => {
            console.error('获取评论失败:', error);
            document.getElementById('comments-list').innerHTML = '<div class="error">获取评论失败</div>';
        });
}

// 提交评论
function submitComment(postId) {
    const content = document.getElementById('comment-content').value.trim();
    
    if (!content) {
        alert('评论内容不能为空');
        return;
    }
    
    fetch(`${API_BASE_URL}/comments`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            postId: postId,
            content: content
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('评论提交失败');
        }
        return response.json();
    })
    .then(data => {
        alert('评论发表成功！');
        document.getElementById('comment-content').value = '';
        loadComments(postId);
    })
    .catch(error => {
        console.error('评论提交失败:', error);
        alert('评论提交失败，请重试');
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
            const likeButton = document.getElementById('like-post');
            const currentLikes = parseInt(likeButton.textContent.match(/\d+/)[0]) + 1;
            likeButton.innerHTML = `<i class="fas fa-heart"></i> 点赞 (${currentLikes})`;
        }
    })
    .catch(error => console.error('点赞失败:', error));
}

// 点赞评论
function likeComment(commentId) {
    fetch(`${API_BASE_URL}/comments/${commentId}/like`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadComments(new URLSearchParams(window.location.search).get('id'));
        }
    })
    .catch(error => console.error('点赞评论失败:', error));
}

// 格式化日期 (保持不变)
function formatDate(dateString) {
    const date = new Date(dateString);
    return `${date.getFullYear()}-${padZero(date.getMonth() + 1)}-${padZero(date.getDate())} ${padZero(date.getHours())}:${padZero(date.getMinutes())}`;
}

// 补零 (保持不变)
function padZero(num) {
    return num < 10 ? '0' + num : num;
} 