# 🇳🇬 尼日利亚客户开发自动化搜索脚本

## 📋 功能说明

本脚本用于**家装五金出口贸易**开发尼日利亚客户，支持：
- 🔍 关键词自动组合搜索
- 🌐 多平台搜索链接生成（Google、Facebook、LinkedIn、Instagram）
- 📊 客户信息整理（公司名、联系人、邮箱、电话、网址、社交媒体）
- 📁 结果自动保存为 CSV/Excel

---

## ⚠️ 重要说明

**为什么不用爬虫自动抓取？**

| 平台 | 爬虫风险 |
|------|----------|
| LinkedIn | ⛔ 严格禁止，会封号 + 法律风险 |
| Facebook | ⛔ 严格禁止，会封号 |
| Instagram | ⛔ 严格禁止，会封号 |
| Google | ⛔ 频繁请求会封 IP |

**本脚本采用合规方案：**
- ✅ 生成精准搜索链接，人工查看
- ✅ 提供信息提取工具，辅助录入
- ✅ 统一整理到 Excel，方便跟进

---

## 🚀 快速开始

### 1. 环境要求

- macOS（已测试）
- Python 3.8+
- 可选：`openpyxl`（用于 Excel 输出）

### 2. 安装依赖

```bash
# 检查 Python 版本
python3 --version

# 安装 Excel 支持（可选）
pip3 install openpyxl
```

### 3. 运行脚本

```bash
# 进入脚本目录
cd /Users/zhuxiaolei/.openclaw/workspace/scripts

# 运行脚本
python3 nigeria-client-finder.py
```

---

## 📖 使用流程

### 模式 1：手动搜索辅助模式 🔍

**用途：** 生成搜索链接和指南，帮你快速找到目标客户

**操作步骤：**

1. 运行脚本，选择 `1`
2. 脚本会生成：
   - `nigeria_search_links.json` - 各平台搜索链接
   - `client_template.csv` - 客户记录模板
   - 终端输出搜索指南

3. 按指南依次搜索：
   ```
   Google → LinkedIn → Facebook → Instagram → Google Maps
   ```

4. 找到目标客户后，记录关键信息

### 模式 2：交互式录入模式 📝

**用途：** 搜索后录入客户信息，自动保存为 CSV/Excel

**操作步骤：**

1. 运行脚本，选择 `2`
2. 按提示逐个录入客户信息：
   ```
   公司名 → 联系人 → 邮箱 → 电话 → 网站 → 地址 → 城市 → 来源 → 备注
   ```
3. 录入完成后，自动生成：
   - `nigeria_clients.csv`
   - `nigeria_clients.xlsx`

### 模式 3：API 自动搜索模式 🤖

**用途：** 使用 Google Custom Search API 自动搜索（需配置）

**配置步骤：**

1. 获取 Google API Key：
   - 访问：https://console.cloud.google.com/
   - 创建项目 → 启用 Custom Search API → 创建 API Key

2. 创建 Search Engine：
   - 访问：https://programmablesearchengine.google.com/
   - 创建新搜索引擎 → 获取 Search Engine ID (CX)

3. 编辑脚本，填入配置：
   ```python
   CONFIG = {
       'google_api_key': '你的 API Key',
       'google_cx': '你的 Search Engine ID',
       # ... 其他配置
   }
   ```

4. 运行脚本，选择 `3`

---

## 🎯 搜索关键词策略

### 产品关键词（已配置）

```
door lock, door handle, cabinet hinge, drawer slide, furniture hardware
edge banding, furniture glue, cabinet pull, hinge, furniture accessories
门锁，门把手，铰链，导轨，家具五金，封边条，家具配件
```

### 买家类型关键词（已配置）

```
importer, wholesaler, distributor, dealer, trading company
building materials, hardware store, construction supplier
进口商，批发商，经销商
```

### 目标城市（已配置）

```
Lagos（拉各斯）- 最大城市，商业中心
Abuja（阿布贾）- 首都
Kano（卡诺）- 北部商业中心
Port Harcourt（哈科特港）- 石油城市
Ibadan（伊巴丹）- 西南部大城市
```

---

## 📂 输出文件说明

### nigeria_clients.csv
CSV 格式，可用 Excel 打开，字段：
| 字段 | 说明 |
|------|------|
| 公司名 | 公司全称 |
| 联系人 | 采购负责人姓名 |
| 邮箱 | 联系邮箱 |
| 电话 | 联系电话（尼日利亚 +234） |
| 网站 | 公司官网 |
| 地址 | 详细地址 |
| 城市 | 所在城市 |
| Facebook | Facebook 主页链接 |
| LinkedIn | LinkedIn 公司/个人链接 |
| Instagram | Instagram 主页链接 |
| 来源 | 发现渠道 |
| 搜索关键词 | 使用的搜索词 |
| 备注 | 其他信息 |
| 发现日期 | 记录时间 |

### nigeria_search_links.json
各平台搜索链接集合，可直接点击打开

### client_template.csv
空白客户记录模板，可手动填写

---

## 💡 高效搜索技巧

### Google 搜索指令

```bash
# 精确匹配
"door lock" importer Nigeria

# 排除某些词
"hardware" Nigeria -china -supplier

# 限定网站类型
"building materials" Nigeria site:.ng

# 找邮箱
"hardware" Nigeria "@gmail.com" OR "@yahoo.com"

# 找联系人
"purchasing manager" "hardware" Nigeria
```

### LinkedIn 搜索技巧

1. 搜索公司后，点进公司页面
2. 查看 "People" 标签，找：
   - Purchasing Manager
   - Procurement Officer
   - Import Manager
   - CEO/Owner（小公司直接找老板）
3. 发送连接请求时附带消息：
   ```
   Hi [Name], I noticed your company specializes in building materials.
   We manufacture door locks and furniture hardware in China.
   Would love to connect and explore potential cooperation.
   ```

### Facebook 搜索技巧

1. 搜索后筛选 "Pages"
2. 查看 "Page Transparency" 了解公司背景
3. 查看 "About" 里的联系方式
4. 直接发消息询问采购需求

### Google Maps 搜索技巧

1. 搜索 "hardware store Lagos"
2. 查看商家信息里的：
   - 网站
   - 电话
   - 营业时间
   - 用户评价（判断规模）
3. 街景查看实体店规模

---

## 🌐 推荐行业目录网站

| 网站 | 用途 |
|------|------|
| https://www.vconnect.com/ | 尼日利亚本地商家目录 |
| https://www.finelib.com/ | 尼日利亚公司信息 |
| https://www.tradekey.com/nigeria/ | B2B 采购商 |
| https://www.go4worldbusiness.com/ | 国际采购需求 |
| https://www.nigeriainfo.fm/ | 拉各斯商家信息 |

---

## ⚡ 批量搜索优化建议

如果要搜索大量关键词，建议：

1. **分批次执行**：每次 10-20 个关键词，避免疲劳
2. **使用浏览器书签**：把生成的搜索链接保存为书签文件夹
3. **使用多标签页**：一次性打开 5-10 个搜索结果页
4. **使用笔记工具**：边搜索边记录，如 Notion、Excel
5. **设置目标**：每天开发 10-20 个有效客户

---

## 🔧 自定义配置

编辑脚本顶部的 `CONFIG` 字典：

```python
CONFIG = {
    # 添加你的产品关键词
    'product_keywords': [
        'your product 1',
        'your product 2',
        # ...
    ],
    
    # 添加目标城市
    'target_cities': ['Lagos', 'Your City'],
    
    # 修改输出文件名
    'output_csv': 'my_clients.csv',
    'output_excel': 'my_clients.xlsx',
}
```

---

## 📞 尼日利亚区号参考

| 类型 | 格式 | 示例 |
|------|------|------|
| 手机 | +234 7XX XXX XXXX | +234 701 234 5678 |
| 座机 | +234 1 XXX XXXX | +234 1 234 5678 |
| 本地手机 | 07XX XXX XXXX | 0701 234 5678 |
| 本地座机 | 01 XXX XXXX | 01 234 5678 |

---

## 📝 跟进建议

找到客户后，建议：

1. **第一封邮件**：公司介绍 + 产品目录
2. **3 天后**：WhatsApp 跟进（尼日利亚人常用 WhatsApp）
3. **1 周后**：电话跟进
4. **持续跟进**：每周分享新产品/价格更新

**WhatsApp 开发话术：**
```
Hello [Name], this is [Your Name] from [Company].
We manufacture door locks and furniture hardware.
I found your company on [source] and believe we can offer competitive prices.
May I send you our product catalog?
```

---

## ❓ 常见问题

**Q: 为什么没有自动爬虫功能？**
A: 社交媒体严禁爬虫，会封号且有法律风险。人工搜索虽然慢，但更安全、更精准。

**Q: Google API 免费额度够用吗？**
A: 每天 100 次免费搜索，对于小规模开发足够。如需更多，需付费。

**Q: 如何验证邮箱是否有效？**
A: 可使用免费工具如 https://www.email-verifier.net/ 批量验证。

**Q: 如何找采购负责人邮箱？**
A: 尝试常见格式：
- info@company.com
- sales@company.com
- purchasing@company.com
- 名字@公司域名（如 john@company.com）

---

## 📄 许可证

本脚本仅供个人/公司内部使用，不得用于商业销售。

---

**祝晓雷哥哥开发顺利，订单满满！💰🌸**

_黛玉 敬上_
