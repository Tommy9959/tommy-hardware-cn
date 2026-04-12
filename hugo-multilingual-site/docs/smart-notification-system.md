# 📱 智能通知系统配置

## ✅ 通知通道分配策略

### 日常通知 → 微信 (WeChat)
**频率：** 每天/每周
**内容：** 例行报告、一般更新

### 重要通知 → iMessage
**频率：** 实时/紧急
**内容：** 严重错误、网站故障、安全提醒

### 正式报告 → 邮件
**频率：** 每月/每季度
**内容：** 月度总结、季度分析、趋势报告

---

## 📊 通知级别定义

### 🔵 蓝色 - 信息级 (微信)
- 日常检查完成
- 周报发送
- 一般更新通知

**示例：**
```
📊 jh-hardware.com SEO 日报
日期：2026-04-12
✅ 所有检查通过
索引页面：150 个
详情：https://search.google.com/search-console
```

---

### 🟢 绿色 - 正常级 (微信)
- 网站运行正常
- 索引状态良好
- 无错误提醒

**示例：**
```
✅ 网站状态正常
HTTP 200 - 响应快速
sitemap.xml - 可访问
robots.txt - 正常
```

---

### 🟡 黄色 - 警告级 (微信 + iMessage)
- 小问题需要关注
- 非紧急错误
- 性能下降

**示例：**
```
⚠️ 注意：发现小问题
- 索引错误：5 个（略高于正常）
- 点击率：0.8%（低于 1%）
建议：周末优化
```

---

### 🟠 橙色 - 严重级 (iMessage)
- 网站访问异常
- 索引错误 > 10 个
- 排名大幅下降

**示例：**
```
🚨 严重问题 - 需要立即处理
网站：jh-hardware.com
问题：HTTP 500 错误
时间：2026-04-12 15:30
请立即检查！
```

---

### 🔴 红色 - 紧急级 (iMessage + 电话)
- 网站完全无法访问
- Google 惩罚通知
- 安全漏洞

**示例：**
```
🆘 紧急告警！
网站：jh-hardware.com
状态：无法访问 (HTTP 404)
时间：2026-04-12 15:30
请立即处理！
```

---

## 📋 具体通知规则

### 1. 每日检查报告 (9:00 AM)

**通道：** 微信
**级别：** 蓝色 - 信息级

**内容模板：**
```
📊 jh-hardware.com SEO 日报
日期：{{date}}

【检查结果】
✅ 网站状态：{{website_status}}
✅ 索引状态：{{index_status}}
✅ sitemap：{{sitemap_status}}

【关键指标】
- 已发现页面：{{discovered_pages}} 个
- 索引错误：{{index_errors}} 个
- 展示次数：{{impressions}} ({{change}}%)

【行动建议】
{{action_items}}

详情：https://search.google.com/search-console
```

---

### 2. 每周报告 (周一 9:00 AM)

**通道：** 微信
**级别：** 绿色 - 正常级

**内容模板：**
```
📈 jh-hardware.com SEO 周报
周期：{{week_range}}

【本周表现】
展示次数：{{impressions}} ({{change}}%)
点击次数：{{clicks}} ({{change}}%)
平均排名：{{position}} ({{change}})
点击率：{{ctr}}% ({{change}}%)

【索引状态】
已索引页面：{{indexed_pages}} ({{change}})
错误页面：{{error_pages}} 个

【关键词表现】
排名前 10: {{top_10_keywords}} 个
新进入前 10: {{new_top_10}} 个

【本周行动项】
1. {{action_1}}
2. {{action_2}}
3. {{action_3}}

详细报告：{{report_link}}
```

---

### 3. 网站故障告警 (实时)

**通道：** iMessage
**级别：** 橙色 - 严重级

**内容模板：**
```
🚨 网站故障告警

网站：jh-hardware.com
状态：{{status_code}}
错误：{{error_message}}
时间：{{timestamp}}
影响：{{impact}}

请立即检查！
检查链接：https://jh-hardware.com
```

---

### 4. 索引错误告警 (实时)

**通道：** iMessage
**级别：** 橙色 - 严重级

**触发条件：** 索引错误 > 10 个

**内容模板：**
```
⚠️ 索引错误告警

网站：jh-hardware.com
错误数量：{{error_count}} 个
错误类型：{{error_type}}
时间：{{timestamp}}

常见错误：
1. {{error_1}}
2. {{error_2}}
3. {{error_3}}

请查看 Search Console：
https://search.google.com/search-console/index
```

---

### 5. 排名大幅下降告警 (实时)

**通道：** iMessage
**级别：** 橙色 - 严重级

**触发条件：** 平均排名下降 > 5 位

**内容模板：**
```
📉 排名下降告警

网站：jh-hardware.com
当前排名：{{current_position}}
之前排名：{{previous_position}}
下降幅度：{{drop}} 位
时间：{{timestamp}}

可能原因：
- Google 算法更新
- 竞争对手优化
- 网站技术问题

建议立即检查！
```

---

### 6. 月度报告 (每月 1 号)

**通道：** 邮件
**级别：** 蓝色 - 信息级

**内容模板：**
```
主题：📊 jh-hardware.com SEO 月度报告 - {{month}}

正文：

【整月概览】
总展示次数：{{total_impressions}}
总点击次数：{{total_clicks}}
平均点击率：{{avg_ctr}}%
平均排名：{{avg_position}}

【趋势分析】
展示次数：{{trend_impressions}} (📈/📉)
点击次数：{{trend_clicks}} (📈/📉)
索引页面：{{trend_indexed}} (📈/📉)

【关键词表现】
排名前 10 的关键词：{{top_10_count}} 个
排名前 3 的关键词：{{top_3_count}} 个
新进入前 10：{{new_top_10}} 个

【内容表现】
表现最好的页面：{{best_page}}
需要优化的页面：{{needs_optimization}}

【外部链接】
新增外部链接：{{new_backlinks}} 个
总外部链接：{{total_backlinks}} 个

【下月计划】
1. {{plan_1}}
2. {{plan_2}}
3. {{plan_3}}

详细报告见附件。
```

---

## ⚙️ 自动化配置

### 每日检查脚本

**文件：** `/Users/zhuxiaolei/.openclaw/workspace/hugo-multilingual-site/scripts/gsc-daily-check.sh`

**执行时间：** 每天 9:00 AM

**通知逻辑：**
```bash
if [ 所有检查通过 ]; then
    发送微信日报
elif [ 发现小问题 ]; then
    发送微信日报 + 黄色警告
elif [ 发现严重问题 ]; then
    发送微信日报 + iMessage 告警
fi
```

---

### 实时监控脚本

**文件：** `/Users/zhuxiaolei/.openclaw/workspace/hugo-multilingual-site/scripts/gsc-realtime-monitor.sh`

**执行时间：** 每 5 分钟

**监控项：**
- 网站可访问性 (HTTP 状态码)
- sitemap 可访问性
- robots.txt 可访问性

**通知逻辑：**
```bash
if [ HTTP 状态码 != 200 ]; then
    发送 iMessage 严重告警
elif [ sitemap 不可访问 ]; then
    发送 iMessage 严重告警
fi
```

---

### 周报生成脚本

**文件：** `/Users/zhuxiaolei/.openclaw/workspace/hugo-multilingual-site/scripts/gsc-weekly-report.sh`

**执行时间：** 每周一 9:00 AM

**通知逻辑：**
```bash
生成周报 → 发送微信
```

---

### 月报生成脚本

**文件：** `/Users/zhuxiaolei/.openclaw/workspace/hugo-multilingual-site/scripts/gsc-monthly-report.sh`

**执行时间：** 每月 1 号 9:00 AM

**通知逻辑：**
```bash
生成月报 → 发送邮件
```

---

## 🔔 通知接收配置

### 微信通知
- **接收者：** 主人（当前对话）
- **发送方式：** OpenClaw 微信通道
- **格式：** 文本 + 链接

### iMessage 通知
- **接收者：** +8618358008400
- **发送方式：** `imsg send --to "+8618358008400" --text "消息内容"`
- **格式：** 文本

### 邮件通知
- **接收者：** z946487044@icloud.com
- **发送方式：** 邮件客户端或 API
- **格式：** HTML 邮件 + 附件

---

## 📊 通知统计

### 预期通知频率

| 通知类型 | 频率 | 通道 | 预计数量/月 |
|---------|------|------|-----------|
| 日报 | 每天 | 微信 | 30 条 |
| 周报 | 每周 | 微信 | 4 条 |
| 月报 | 每月 | 邮件 | 1 条 |
| 故障告警 | 按需 | iMessage | 0-5 条 |
| 错误告警 | 按需 | iMessage | 0-3 条 |

**总计：** 约 35-43 条通知/月

---

## 🎯 通知优化建议

### 避免打扰
- 日报时间：9:00 AM（主人开始工作后）
- 周报时间：周一 9:00 AM（周一例会前）
- 紧急告警：立即发送（不分时间）

### 免打扰时段
- **晚上 23:00 - 早上 8:00**
  - 暂停非紧急通知
  - 紧急告警仍然发送

### 周末策略
- **周六、周日**
  - 日报暂停
  - 紧急告警仍然发送
  - 周报改为周一发送

---

## 📝 通知示例库

### 示例 1：日报（正常）
```
📊 jh-hardware.com SEO 日报
日期：2026-04-12

【检查结果】
✅ 网站状态：正常 (HTTP 200)
✅ 索引状态：正常
✅ sitemap：正常 (150 个 URL)

【关键指标】
- 已发现页面：150 个
- 索引错误：0 个
- 展示次数：待更新

【行动建议】
- 继续等待 Google 索引
- 监控 Search Console 数据

详情：https://search.google.com/search-console
```

### 示例 2：故障告警
```
🚨 网站故障告警

网站：jh-hardware.com
状态：HTTP 500
错误：Internal Server Error
时间：2026-04-12 15:30
影响：用户无法访问网站

请立即检查！
检查链接：https://jh-hardware.com
```

### 示例 3：周报
```
📈 jh-hardware.com SEO 周报
周期：4/8 - 4/14

【本周表现】
展示次数：待更新
点击次数：待更新
平均排名：待更新

【索引状态】
已索引页面：待更新
错误页面：0 个

【本周行动项】
1. 等待 Google 开始索引
2. 监控 Search Console 数据
3. 准备产品图片

详细报告：查看附件
```

---

## ✅ 配置检查清单

- [ ] 微信通道配置完成 ✅
- [ ] iMessage 通道配置完成 ✅
- [ ] 邮件通道待配置
- [ ] 每日检查脚本已创建 ✅
- [ ] 实时监控脚本待创建
- [ ] 周报模板已创建 ✅
- [ ] 月报模板待创建
- [ ] 通知规则文档已创建 ✅

---

*配置完成时间：2026-04-12*
*网站：https://jh-hardware.com*
*通知系统：智能分配模式*
