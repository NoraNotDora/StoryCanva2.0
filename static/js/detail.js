const API_BASE_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const postId = urlParams.get('id');

    if (postId) {
        loadPostDetail(postId);
        loadComments(postId);
    } else {
        document.getElementById('post-detail').innerHTML = '<p>帖子ID无效</p>';
    }

    // 返回列表按钮事件
    document.getElementById('back-to-index').addEventListener('click', function() {
        console.log('返回列表按钮被点击了！'); // 添加调试信息
        window.location.href = 'index.html'; // 返回到 index.html
    });

    // 评论表单提交事件 (需要手动添加到 post detail 加载完成后)
});

// 加载帖子详情
function loadPostDetail(postId) {
    const postDetail = document.getElementById('post-detail');
    postDetail.innerHTML = '加载中...';

    fetch(`${API_BASE_URL}/posts/${postId}`)
        .then(response => response.json())
        .then(post => {
            if (!post) {
                postDetail.innerHTML = '<p>帖子不存在或已被删除</p>';
                return;
            }

            postDetail.innerHTML = `
                <div class="post-header">
                    <h2>${post.title}</h2>
                    <p class="post-meta">作者: ${post.author} | 发布时间: ${formatDate(post.date)} | 浏览: ${post.views} | 点赞: ${post.likes}</p>
                </div>
                <div class="post-content">
                    ${post.content}
                </div>
                <button id="like-post" data-id="${post.id}">点赞</button>

                <div class="comments-section">
                    <h3>评论区</h3>
                    <div id="comments-list"></div>
                    <div class="comment-form">
                        <h4>发表评论</h4>
                        <form id="comment-form">
                            <input type="hidden" id="comment-post-id" value="${post.id}">
                            <div class="form-group">
                                <label for="comment-author">昵称:</label>
                                <input type="text" id="comment-author" placeholder="匿名用户">
                            </div>
                            <div class="form-group">
                                <label for="comment-content">评论内容:</label>
                                <textarea id="comment-content" required></textarea>
                            </div>
                            <button type="submit">提交评论</button>
                        </form>
                    </div>
                </div>
            `;

            // 添加评论表单提交事件
            const commentForm = postDetail.querySelector('#comment-form');
            commentForm.addEventListener('submit', handleCommentSubmit);

            // 点赞按钮事件
            document.getElementById('like-post').addEventListener('click', function() {
                const postId = this.getAttribute('data-id');
                likePost(postId);
            });

        })
        .catch(error => {
            console.error('获取帖子详情失败:', error);
            postDetail.innerHTML = '<p>获取帖子详情失败，请稍后重试。</p>';
        });
}

// 加载评论
function loadComments(postId) {
    const commentsList = document.getElementById('comments-list');
    commentsList.innerHTML = '加载评论中...';

    fetch(`${API_BASE_URL}/posts/${postId}/comments`)
        .then(response => response.json())
        .then(comments => {
            commentsList.innerHTML = ''; // 清空加载提示
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

function handleCommentSubmit(e) {
    e.preventDefault();
    const postId = document.getElementById('comment-post-id').value;
    const content = document.getElementById('comment-content').value;
    const author = document.getElementById('comment-author').value;

    if (content) {
        saveComment(postId, content, author).then(() => {
            // 清空表单
            document.getElementById('comment-content').value = '';
            // 重新加载评论
            loadComments(postId);
        });
    }
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
            let currentLikes = parseInt(postMeta.textContent.match(/点赞: (\\d+)/)[1]);
            postMeta.innerHTML = postMeta.innerHTML.replace(/点赞: \\d+/, `点赞: ${currentLikes + 1}`);
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
            let currentLikes = parseInt(commentMeta.textContent.match(/点赞: (\\d+)/)[1]);
            commentMeta.innerHTML = commentMeta.innerHTML.replace(/点赞: \\d+/, `点赞: ${currentLikes + 1}`);
        }
    })
    .catch(error => {
        console.error('点赞评论失败:', error);
    });
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