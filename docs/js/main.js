// Hugo 多语言网站主脚本

// 移动端菜单初始化函数
function initMobileMenu() {
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const siteNav = document.querySelector('.site-nav');
    
    if (menuToggle && siteNav) {
        menuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.toggle('active');
            siteNav.classList.toggle('active');
            console.log('Menu toggled:', siteNav.classList.contains('active'));
        });
        
        // 点击导航链接时关闭菜单
        siteNav.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', function() {
                menuToggle.classList.remove('active');
                siteNav.classList.remove('active');
            });
        });
        
        // 点击外部关闭菜单
        document.addEventListener('click', function(e) {
            if (!siteNav.contains(e.target) && !menuToggle.contains(e.target)) {
                menuToggle.classList.remove('active');
                siteNav.classList.remove('active');
            }
        });
    }
}

// 移动端语言切换器
function initLangSwitcher() {
    const langSwitcher = document.querySelector('.lang-switcher');
    if (langSwitcher) {
        langSwitcher.addEventListener('click', function(e) {
            e.stopPropagation();
            this.classList.toggle('active');
        });
        document.addEventListener('click', function() {
            langSwitcher.classList.remove('active');
        });
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('Hugo Multilingual Site Loaded');
    initMobileMenu();
    initLangSwitcher();
});

// 防止 defer 加载问题，再次检查
if (document.readyState === 'interactive' || document.readyState === 'complete') {
    setTimeout(() => {
        initMobileMenu();
        initLangSwitcher();
    }, 100);
}

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
if (header) {
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 100) {
            header.style.background = 'rgba(255, 255, 255, 0.98)';
            header.style.backdropFilter = 'blur(10px)';
        } else {
            header.style.background = 'var(--bg-color)';
        }
    });
}
