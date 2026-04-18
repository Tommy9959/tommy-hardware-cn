// Hugo 多语言网站主脚本 - v20260418

// 移动端菜单初始化函数
function initMobileMenu() {
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const siteNav = document.querySelector('.site-nav');
    
    console.log('Init mobile menu:', { menuToggle: !!menuToggle, siteNav: !!siteNav });
    
    if (menuToggle && siteNav) {
        // 点击汉堡菜单按钮
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
                console.log('Nav link clicked, closing menu');
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
    const langDropdown = langSwitcher?.querySelector('.lang-dropdown');
    
    console.log('Init lang switcher:', { langSwitcher: !!langSwitcher, langDropdown: !!langDropdown });
    
    if (langSwitcher) {
        // 点击语言切换器按钮
        const langLabel = langSwitcher.querySelector('.lang-label');
        if (langLabel) {
            langLabel.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                langSwitcher.classList.toggle('active');
                if (langDropdown) {
                    langDropdown.classList.toggle('active');
                }
                console.log('Lang switcher toggled:', langSwitcher.classList.contains('active'));
            });
        }
        
        // 点击选项时关闭
        if (langDropdown) {
            langDropdown.querySelectorAll('.lang-option').forEach(option => {
                option.addEventListener('click', function() {
                    langSwitcher.classList.remove('active');
                    langDropdown.classList.remove('active');
                });
            });
        }
        
        // 点击外部关闭
        document.addEventListener('click', function() {
            langSwitcher.classList.remove('active');
            if (langDropdown) {
                langDropdown.classList.remove('active');
            }
        });
    }
}

// 页面加载完成后初始化
function initAll() {
    console.log('=== Initializing all scripts ===');
    initMobileMenu();
    initLangSwitcher();
    console.log('=== Initialization complete ===');
}

// 多种初始化方式确保执行
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
} else {
    // DOM 已经就绪，立即执行
    initAll();
}

// 额外保险：延迟执行一次
setTimeout(initAll, 50);
setTimeout(initAll, 200);

// 平滑滚动
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href && href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
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
