# CHANGELOG: 铁管套管产品页全面优化

**日期：** 2026-05-27

## 改动汇总

### 1. 目录重命名（三语言）
- `content/en/products/steel-pipes-flanges/` → `content/en/products/iron-casing-pipes/`
- `content/zh/products/steel-pipes-flanges/` → `content/zh/products/iron-casing-pipes/`
- `content/ar/products/steel-pipes-flanges/` → `content/ar/products/iron-casing-pipes/`

### 2. 添加别名（Aliases）确保旧URL不404
- 18个产品单页（EN/ZH/AR × 6产品）均添加了 `aliases` frontmatter，包含两种旧路径：
  - `/{lang}/products/steel-pipes-flanges/sp-00X`
  - `/products/steel-pipes-flanges/sp-00X`
- 3个 _index.md 文件（产品分类页）添加了别名：
  - `/{lang}/products/steel-pipes-flanges` 和 `/{lang}/products/steel-pipes-flanges/`

### 3. 图片路径更新
- EN产品页 image: 从 `/images/products/steel-pipes-flanges/` → `/images/products/iron-casing-pipes/`
- ZH/AR产品页原无image字段，无需修改

### 4. 静态图片迁移
- `static/images/products/steel-pipes-flanges/` → `static/images/products/iron-casing-pipes/`
- 12个占位图片文件（6个.svg + 6个.png，均为SVG内容）全部迁移并更新了文本内容
- 占位图片文字从 "Seamless Steel Pipe" 改为 "Iron Casing Pipe" 等正确名称

### 5. 中文产品页内容重写（zh）
- sp-001 到 sp-006 全部重写
- 旧内容：无缝钢管/焊接钢管/法兰/方钢管/盲板法兰/镀锌管（完全不相关）
- 新内容：铁管套管 16mm/25mm 四款不同壁厚 + 连接件，与英文版一致

### 6. 阿拉伯语产品页内容重写（ar）
- sp-001 到 sp-006 全部重写
- 旧内容：各种钢管/法兰（完全不相关）
- 新内容：أنابيب حديد كاسينغ（铁管套管）与英文版一致

### 7. 分类索引页模型编号修正
- ZH/AR _index.md 中 model 前缀从 SP-XXX 修正为 IP-XXX

### 8. 布局模板更新
- `layouts/products/list.html`：产品分类卡片中的"钢法兰"相关条目已改为"铁管套管"
  - 名称：Iron Casing Pipes / 铁管套管 / أنابيب حديد كاسينغ
  - 描述更新为铁管套管相关
  - 链接从 `/products/steel-pipes-flanges/` → `/products/iron-casing-pipes/`

### 9. 联系页面更新
- `content/en/contact.md`：产品列表中的 "Steel Pipes & Flanges" → "Iron Casing Pipes"
- `content/zh/contact.md`：产品列表中的 "钢管法兰" → "铁管套管"

### 10. Hugo配置文件
- `hugo.toml`：无需要修改（菜单中没有引用 /products/steel-pipes-flanges/）

### 11. 博客文章
- 三篇博客文章的标题和内容已正确使用"Iron Casing Pipes"（之前已正确，内容中"steel pipes"仅用于对比语境，无需修改）

### 构建测试
- `hugo --destination /tmp/test-build` 编译通过 ✅
- 别名重定向页面正确生成 ✅
