document.addEventListener('DOMContentLoaded', function() {
    const publishForm = document.getElementById('publish-form');
    const imageInput = document.getElementById('story-image');
    const imagePreview = document.getElementById('image-preview');
    
    // 图片预览功能
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                }
                
                reader.readAsDataURL(this.files[0]);
            } else {
                imagePreview.style.display = 'none';
            }
        });
    }
    
    if (publishForm) {
        publishForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const title = document.getElementById('title').value;
            const content = document.getElementById('content').value;
            const imageFile = document.getElementById('story-image').files[0];
            const isPublic = document.getElementById('is-public').checked ? 1 : 0;
            
            if (!title || !content) {
                alert('标题和内容不能为空！');
                return;
            }
            
            // 获取提交按钮
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            
            // 禁用按钮，显示加载状态
            submitButton.disabled = true;
            submitButton.textContent = '发布中...';
            
            // 创建FormData对象，用于发送文件
            const formData = new FormData();
            formData.append('title', title);
            formData.append('content', content);
            formData.append('is_public', isPublic);
            if (imageFile) {
                formData.append('image', imageFile);
            }
            
            // 发送 API 请求
            fetch('/api/posts', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('网络响应不正常');
                }
                return response.json();
            })
            .then(data => {
                console.log('发布成功:', data);
                alert('故事发布成功！');
                // 重定向到个人主页
                window.location.href = '/profile';
            })
            .catch(error => {
                console.error('发布失败:', error);
                alert('发布失败，请重试！');
            })
            .finally(() => {
                // 恢复按钮状态
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            });
        });
    }
}); 