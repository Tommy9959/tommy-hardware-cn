# Hugo 多语言静态网站

使用 Hugo 构建的快速、美观、支持多语言的静态网站模板。

## 🌍 支持的语言

- 🇨🇳 中文 (Chinese) - 默认语言
- 🇬🇧 English (英语)
- 🇸🇦 العربية (阿拉伯语) - RTL 支持

## 📁 项目结构

```
hugo-multilingual-site/
├── hugo.toml              # Hugo 配置文件
├── content/               # 网站内容
│   ├── zh/               # 中文内容
│   │   ├── _index.md     # 首页
│   │   ├── about.md      # 关于页面
│   │   └── contact.md    # 联系页面
│   ├── en/               # 英文内容
│   │   └── ...
│   └── ar/               # 阿拉伯语内容
│       └── ...
├── layouts/              # 模板文件
│   ├── _default/         # 默认模板
│   │   ├── baseof.html   # 基础布局
│   │   └── single.html   # 单页模板
│   ├── index.html        # 首页模板
│   └── partials/         # 局部模板
│       └── language-switcher.html  # 语言切换器
├── static/               # 静态资源
│   ├── css/
│   │   └── style.css     # 样式文件
│   ├── js/
│   │   └── main.js       # JavaScript
│   └── images/           # 图片
└── README.md             # 说明文档
```

## 🚀 快速开始

### 1. 安装 Hugo

**macOS:**
```bash
brew install hugo
```

**Windows:**
```bash
choco install hugo -confirm
```

**Linux:**
```bash
sudo apt-get install hugo
```

### 2. 本地预览

```bash
cd hugo-multilingual-site
hugo server --buildDrafts
```

访问：http://localhost:1313

### 3. 构建生产版本

```bash
hugo --gc --minify
```

生成的文件在 `public/` 目录

## 🌐 多语言配置

### 添加新语言

在 `hugo.toml` 中添加：

```toml
[languages.fr]
  title = 'Site Français'
  weight = 4
  languageName = 'Français'
  languageCode = 'fr'
  contentDir = 'content/fr'
```

然后创建 `content/fr/` 目录并添加内容。

### 语言切换器

语言切换器位于页面右上角，支持：
- 悬停下拉菜单
- 当前语言高亮
- RTL 自动适配（阿拉伯语）

## 🎨 自定义样式

编辑 `static/css/style.css` 中的 CSS 变量：

```css
:root {
    --primary-color: #3498db;    /* 主色调 */
    --secondary-color: #2c3e50;  /* 次要颜色 */
    --accent-color: #e74c3c;     /* 强调色 */
}
```

## 📱 响应式设计

网站完全响应式，适配：
- 📱 手机 (< 768px)
- 📱 平板 (768px - 1024px)
- 💻 桌面 (> 1024px)

## 🚢 部署

### GitHub Pages

```bash
# 构建
hugo --gc --minify

# 推送到 gh-pages 分支
cd public
git init
git add .
git commit -m "Deploy"
git remote add origin https://github.com/USERNAME/REPO.git
git push -f origin HEAD:gh-pages
```

### Netlify

1. 连接 GitHub 仓库
2. 构建命令：`hugo --gc --minify`
3. 发布目录：`public`

### Vercel

1. 导入项目
2. 自动检测 Hugo
3. 自动部署

## 📝 添加新页面

1. 在对应语言目录创建 `.md` 文件：
   ```bash
   content/zh/new-page.md
   ```

2. 添加 Front Matter：
   ```markdown
   ---
   title: "新页面"
   description: "页面描述"
   ---
   
   页面内容...
   ```

3. Hugo 自动生成页面

## 🎯 特性

- ✅ **多语言支持** - 中文、English、العربية
- ✅ **RTL 支持** - 阿拉伯语从右到左布局
- ✅ **响应式设计** - 适配所有设备
- ✅ **快速加载** - 静态网站，秒级打开
- ✅ **SEO 友好** - 语义化 HTML
- ✅ **易于部署** - 可部署在任何静态托管

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

---

**使用 Hugo 构建，为多语言世界而生** 🌍
