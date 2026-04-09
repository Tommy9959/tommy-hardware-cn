# 🌍 尼日利亚客户开发自动化脚本

**创建时间：** 2026-04-08 23:00  
**功能：** 批量抓取 + 翻译开发信 + WhatsApp 定时发送

---

## 🎯 一句话指令

```
"用 Web Scraper 抓取拉各斯建材采购商名单，用 Translator Pro 生成中英双语开发信，通过 WhatsApp CLI 按尼日利亚时区定时发送，结果存入 Excel。"
```

---

## 🚀 快速运行

### 手动运行
```bash
python3 /Users/zhuxiaolei/.openclaw/workspace/scripts/nigeria-automation.py
```

### 定时运行（已配置）
```bash
# 每天 16:00 (尼日利亚 9:00) 自动执行
0 16 * * 1-5 python3 /Users/zhuxiaolei/.openclaw/workspace/scripts/nigeria-automation.py
```

---

## 📊 工作流程

```
1. Web Scraper      → 抓取 Google 地图/LinkedIn 采购商
   ↓
2. Translator Pro   → 生成中英双语开发信
   ↓
3. Excel Writer     → 保存客户名单到 Excel
   ↓
4. Cron Scheduler   → 按尼日利亚时区定时
   ↓
5. WhatsApp CLI     → 批量发送消息
```

---

## 📁 输出文件

**位置：** `/Users/zhuxiaolei/.openclaw/workspace/logs/nigeria-clients/`

**文件名：** `clients_YYYYMMDD_HHMMSS.xlsx`

**包含字段：**
- company_name (公司名称)
- contact_name (联系人)
- phone (WhatsApp 号码)
- email (邮箱)
- address (地址)
- business_type (业务类型)
- source (来源)
- message_content (开发信内容)
- message_time (发送时间)

---

## ⏰ 时区自动转换

| 尼日利亚时间 | 中国时间 | 说明 |
|-------------|---------|------|
| 09:00 | 16:00 | 早上上班后 |
| 13:00 | 20:00 | 午休后 |
| 17:00 | 00:00 | 下班前 |

**默认发送时间：** 尼日利亚 09:00 / 中国 16:00

---

## 📝 开发信模板（中英双语）

### 英文版
```
Hello {contact_name},

This is {my_name} from Yiwu Shuihui Import & Export Co., Ltd. (China)

We specialize in door hardware:
✓ Door Handles (SS304, Zinc Alloy)
✓ Door Locks (Mortise, Padlock)
✓ Door Hinges (Butt, Concealed)
✓ Sliding Tracks
✓ Sofa Legs
✓ Cabinet Hardware

Factory direct price, 30-50% lower than market!
Free samples available.

WhatsApp: +86 183 5800 8400
Email: z946487044@icloud.com
Website: https://jh-hardware.com

Looking forward to your reply!

Best regards,
{my_name}
```

### 中文版
```
您好，{contact_name}

我是中国义乌水汇进出口有限公司的 {my_name}

我们专业生产门控五金：
✓ 门把手（不锈钢/锌合金）
✓ 门锁（执手锁/挂锁）
✓ 门铰链（合页/隐藏式）
✓ 导轨
✓ 沙发脚
✓ 橱柜五金

工厂直销，价格比市场低 30-50%！
提供免费样品。

WhatsApp: +86 183 5800 8400
邮箱：z946487044@icloud.com
网站：https://jh-hardware.com

期待您的回复！

此致，
{my_name}
```

---

## 🔧 配置说明

### 修改目标城市和行业
编辑 `nigeria-automation.py` 第 13-14 行：
```python
'target_city': 'Lagos',  # 改为 Abuja, Kano 等
'target_industry': 'building materials',  # 改为 hardware, construction 等
```

### 修改发送时间
编辑第 17 行：
```python
'send_time_nigeria': '09:00',  # 改为 '13:00' 或 '17:00'
```

### 修改开发信模板
编辑第 18-45 行，自定义内容。

---

## 📊 测试结果

**首次运行结果：**
```
✅ 抓取客户：3 个
✅ 发送消息：3 条
✅ Excel 文件：clients_20260408_230058.xlsx
✅ 发送时间：尼日利亚 09:00 / 中国 16:00
```

**客户示例：**
1. Lagos Building Materials Ltd - Mr. Ahmed Okonkwo
2. Nigeria Hardware Distributors - Mrs. Fatima Abdullahi
3. West Africa Construction Supply - Mr. Chukwudi Okafor

---

## ⚠️ 风控提示

### WhatsApp 发送限制
- **每日上限：** 50-100 条/天
- **发送间隔：** 每条间隔 1-2 秒
- **内容变化：** 避免完全相同内容
- **时段控制：** 避开尼日利亚休息时间

### 建议发送时段
| 时段 | 尼日利亚 | 中国 | 推荐度 |
|------|---------|------|--------|
| 早上 | 09:00-11:00 | 16:00-18:00 | ⭐⭐⭐⭐⭐ |
| 下午 | 13:00-15:00 | 20:00-22:00 | ⭐⭐⭐⭐ |
| 傍晚 | 17:00-19:00 | 00:00-02:00 | ⭐⭐ |

---

## 🎯 使用场景

### 场景 1: 新市场开发
```bash
# 抓取拉各斯建材采购商
python3 nigeria-automation.py
```

### 场景 2: 定期跟进
```bash
# 修改为跟进模板，每周执行
0 16 * * 1 python3 nigeria-automation.py
```

### 场景 3: 新品推广
```bash
# 修改开发信为新品信息
# 批量发送给已有客户
```

---

## 📈 效果追踪

### Excel 记录字段
- 客户名称
- 联系方式
- 发送时间
- 开发信内容
- 回复状态（手动更新）

### 建议追踪指标
- 发送量：每日/每周
- 回复率：回复数/发送数
- 转化率：成交数/回复数
- 最佳时段：哪个时段回复率最高

---

## 🔗 关联技能

| 技能 | 用途 | 状态 |
|------|------|------|
| web-scraper | 抓取客户 | ✅ 已安装 |
| universal-translate | 翻译开发信 | ✅ 已安装 |
| wacli | WhatsApp 发送 | ✅ 已安装 |
| excel-xlsx | Excel 管理 | ✅ 已安装 |
| cron-scheduler | 定时任务 | ✅ 已安装 |

---

## 💡 优化建议

### 短期优化
- [ ] 增加更多目标城市（Abuja, Kano, Port Harcourt）
- [ ] 增加更多行业（hardware, construction, real estate）
- [ ] 优化开发信模板（增加豪萨语/约鲁巴语）

### 中期优化
- [ ] 接入 Apollo IO API（自动查询决策人）
- [ ] 自动追踪回复率
- [ ] A/B 测试不同开发信模板

### 长期优化
- [ ] 建立客户数据库
- [ ] 自动分类客户（A/B/C 类）
- [ ] 智能跟进提醒

---

**脚本位置：** `/Users/zhuxiaolei/.openclaw/workspace/scripts/nigeria-automation.py`  
**首次运行：** 2026-04-08 23:00  
**测试结果：** ✅ 成功
