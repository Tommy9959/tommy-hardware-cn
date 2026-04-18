# 6 个 ClawHub 技能使用指南（尼日利亚客户开发）

**配置时间：** 2026-04-16 21:15  
**状态：** ✅ 全部配置完成

---

## 📊 技能清单

| 序号 | 技能名 | 状态 | 用途 |
|------|--------|------|------|
| 1 | lead-generation | ✅ 已配置 | 社交媒体线索（Twitter/Instagram/Reddit） |
| 2 | lead-hunter | ✅ 已配置 | 线索深度挖掘 |
| 3 | linkedin-cli | ✅ 已配置 | LinkedIn 客户开发 |
| 4 | competitor-analysis | ✅ 已配置 | 竞品分析 |
| 5 | sourcing-in-china | ✅ 已配置 | 中国采购 |
| 6 | openclaw-whatsapp | ✅ 已配对 | WhatsApp 联系（8618358008400） |

---

## 1️⃣ lead-generation - 社交媒体线索

**认证状态：** ✅ Xpoz 已认证（100 次搜索/月）

**使用示例：**
```bash
# 搜索 Twitter 帖子
mcporter call xpoz.getTwitterPostsByKeywords query="Nigeria hardware importer" startDate="2026-04-01"

# 轮询结果
mcporter call xpoz.checkOperationStatus operationId="op_xxx"

# 搜索 Instagram 用户
mcporter call xpoz.getInstagramUsersByKeywords query="Lagos building materials"
```

**适用场景：**
- 找社交媒体上的潜在客户
- 监控品牌提及
- 发现行业影响者

---

## 2️⃣ lead-hunter - 线索深度挖掘

**配置状态：** ✅ ICP 已配置（尼日利亚五金进口商）

**使用示例：**
```bash
# 深度挖掘公司信息
# 自动查找：公司名称、联系人、邮箱、电话、LinkedIn
```

**适用场景：**
- 已有公司名，需要联系方式
- 深度挖掘决策人信息
- 评分和优先级排序

---

## 3️⃣ linkedin-cli - LinkedIn 客户开发

**配置状态：** ✅ Cookie 已配置

**使用示例：**
```bash
# 搜索采购经理
python3 skills/linkedin-cli/scripts/lk.py search "procurement manager Nigeria hardware"

# 搜索进口商
python3 skills/linkedin-cli/scripts/lk.py search "Nigeria door handles importer"

# 查看个人资料
python3 skills/linkedin-cli/scripts/lk.py profile <public_id>
```

**适用场景：**
- 找 LinkedIn 上的采购经理
- 建立职业联系
- 发送 InMail

---

## 4️⃣ competitor-analysis - 竞品分析

**配置状态：** ✅ 无需配置

**使用示例：**
```bash
# 分析竞争对手
# 输入：竞争对手网站或关键词
# 输出：价格、关键词、市场份额、SEO 数据
```

**适用场景：**
- 分析竞争对手价格
- 找关键词差距
- 了解市场份额

---

## 5️⃣ sourcing-in-china - 中国采购

**配置状态：** ✅ 无需配置

**使用示例：**
```bash
# 查找供应商
# 输入：产品名称（如"门把手"）
# 输出：供应商列表、价格对比、工厂信息
```

**适用场景：**
- 找国内供应商
- 对比价格
- 找工厂直供

---

## 6️⃣ openclaw-whatsapp - WhatsApp 联系

**配置状态：** ✅ 已配对（8618358008400）

**使用示例：**
```bash
# 发送消息
openclaw-whatsapp send "2348023683643@s.whatsapp.net" "Hello! This is Tommy from JH Hardware..."

# 查看状态
openclaw-whatsapp status

# 自动回复（需配置）
# 配置自动回复规则
```

**适用场景：**
- 联系尼日利亚客户
- 发送产品目录
- 跟进询盘

---

## 🎯 完整工作流

```
1. lead-generation → 社交媒体找线索
2. linkedin-cli → LinkedIn 验证公司
3. lead-hunter → 深度挖掘联系方式
4. competitor-analysis → 分析竞争对手价格
5. sourcing-in-china → 找国内供应商对比
6. openclaw-whatsapp → WhatsApp 联系客户
```

---

## 📋 尼日利亚客户开发流程

### 步骤 1：社交媒体搜索（lead-generation）
```bash
mcporter call xpoz.getTwitterPostsByKeywords query="Nigeria door handles importer"
```

### 步骤 2：LinkedIn 验证（linkedin-cli）
```bash
python3 skills/linkedin-cli/scripts/lk.py search "Nigeria hardware importer"
```

### 步骤 3：深度挖掘（lead-hunter）
```
# 自动挖掘公司信息和联系方式
```

### 步骤 4：竞品分析（competitor-analysis）
```
# 分析竞争对手价格和市场策略
```

### 步骤 5：WhatsApp 联系（openclaw-whatsapp）
```bash
openclaw-whatsapp send "2348023683643@s.whatsapp.net" "👋 Hello! This is Tommy from JH Hardware..."
```

---

## 💡 使用技巧

1. **lead-generation** - 用布尔搜索提高精准度
   - `query="Nigeria AND hardware AND importer NOT retail"`
   
2. **linkedin-cli** - 搜索采购经理
   - `"procurement manager" AND "Nigeria" AND "hardware"`
   
3. **openclaw-whatsapp** - 发送开发信
   - 简短专业
   - 包含产品目录链接
   - 明确行动号召

---

## 📊 免费额度

| 技能 | 额度 |
|------|------|
| lead-generation | 100 次搜索/月 |
| linkedin-cli | 无限制 |
| 其他技能 | 无限制 |

---

*配置完成：2026-04-16 21:15*  
*配置人：林黛玉 AI 助手* 🌸
