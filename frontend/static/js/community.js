document.addEventListener('DOMContentLoaded', function() {
    // 处理图片加载错误
    const images = document.querySelectorAll('.card-img-top');
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.src = '/static/picture/placeholder.jpg';
            this.onerror = null; // 防止循环触发错误
        });
    });
    
    // 其他社区页面的 JavaScript...
}); 