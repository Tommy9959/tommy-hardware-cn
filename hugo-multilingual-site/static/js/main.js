// Hugo 多语言网站主脚本

document.addEventListener('DOMContentLoaded', function() {
    console.log('Hugo Multilingual Site Loaded');
    
    // 平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // 头部滚动效果
    const header = document.querySelector('.site-header');
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 100) {
            header.style.background = 'rgba(255, 255, 255, 0.98)';
            header.style.backdropFilter = 'blur(10px)';
        } else {
            header.style.background = 'var(--bg-color)';
        }
    });
});
