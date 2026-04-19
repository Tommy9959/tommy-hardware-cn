# 尼日利亚五金客户开发完整工作流程

## 📋 项目概述
- **目标市场**: 尼日利亚 (Nigeria)
- **主营产品**: 五金产品（门控五金、家具五金、建材配件）
- **排除产品**: 灯具、电器、卫浴、板材
- **核心优势**: 工厂直销价格、灵活起订量、快速交货、认证齐全

## 🔧 自动化脚本架构

### 1. 客户发现阶段 (`nigeria-client-finder.py`)
**功能**: 智能客户收集 + 去重 + 评分 + 分类
- ✅ 智能去重机制（WhatsApp/邮箱唯一标识）
- ✅ 客户评分系统（5维度评分，最高100分）
- ✅ 产品线精准分类（门控/家具/建材三大类）
- ✅ WhatsApp消息模板自动生成
- ✅ 客户分析报告生成

### 2. 消息发送阶段 (`nigeria-send-afternoon.py`)  
**功能**: WhatsApp自动化发送
- ✅ 从CSV文件读取验证客户
- ✅ 号码格式标准化（+234格式）
- ✅ 开发信模板发送
- ✅ 随机间隔控制（25-35秒）
- ✅ 每日发送上限（50条）

## 🎯 产品线详细分类

### 门控五金 (Door Hardware) - 核心产品
- 🚪 门把手 (DH-001~DH-006)
- 🔒 门锁 (DL-001~DL-007)  
- 🔧 门铰链 (HH-001~HH-006)
- 🚀 导轨 (ST-001~ST-006)

### 家具五金 (Furniture Hardware)
- 🪑 沙发脚 (SL-001~SL-006)
- 🗄️ 橱柜五金 (CH-001~CH-006)
- 🔩 家具配件
- 🛋️ 家具支撑

### 建材配件 (Building Materials)
- 🏗️ 钢管、法兰
- 🏠 建材 (胶粘剂、墙纸)
- 🚪 门配件

## ⏰ 跟进时机优化策略

### 最佳联系时间（拉各斯时区）
- **最佳日期**: 周一至周四
- **最佳时段**: 10:00-16:00 (Lagos time)
- **避免时间**: 
  - 周五（宗教日）
  - 周末
  - 当地节假日

### 重要节假日（避免联系）
- Easter: 2026-04-10, 2026-04-11
- Labour Day: 2026-05-01  
- Eid al-Fitr: 2026-06-03, 2026-06-04
- Christmas: 2026-12-25, 2026-12-26

## 📊 客户评分系统

### 评分维度（总分100分）
1. **WhatsApp有效性** (30分): 有有效WhatsApp号码
2. **公司规模** (20分): 大客户(20分) vs 小客户(10分)
3. **产品匹配度** (25分): 与主营产品线匹配
4. **地理位置** (15分): Lagos/Abuja优先
5. **网站质量** (10分): 有专业网站

### 客户分级
- **高潜力客户**: ≥85分（优先联系）
- **中等潜力客户**: 60-84分（常规跟进）
- **低潜力客户**: <60分（批量发送）

## 💬 WhatsApp消息模板

### 大客户话术（强调质量、认证、大批量）
```
Hi {name}!

I'm Tommy from Yiwu Shuihui Import & Export Co., Ltd. We specialize in premium {product} with ISO 9001 certification.

✅ Factory direct pricing (30-50% lower than market)
✅ MOQ flexible for trial orders  
✅ Fast delivery: 15-25 days to Lagos
✅ Complete export documentation (SONCAP, Form M)

Would you like our detailed quotation for {product}?

Best regards,
Tommy 📞 +86-183-5800-8400
🌐 https://jh-hardware.com
```

### 小客户话术（强调价格、小批量、灵活性）
```
Hello {name}!

I'm Tommy from China, supplier of quality {product}. Perfect for your {company} business!

💰 Competitive prices for small orders
📦 MOQ from 100-500 pcs (flexible)
🚚 Delivery to Lagos: 20-30 days  
📱 WhatsApp support 24/7

Free samples available! Interested in our price list?

Best,
Tommy 📞 +86-183-5800-8400
🌐 https://jh-hardware.com
```

## 📁 文件目录结构

```
workspace/
├── scripts/
│   ├── nigeria-client-finder.py      # 客户发现脚本
│   └── nigeria-send-afternoon.py     # 消息发送脚本
├── logs/
│   └── nigeria-clients/
│       ├── client_database.json      # 客户数据库（去重用）
│       ├── nigeria_client_report_*.txt  # 客户分析报告
│       └── nigeria_*_clients_*.csv   # 分类产品客户文件
└── NIGERIA_HARDWARE_WORKFLOW.md      # 本流程文档
```

## 🔄 自动化执行计划

### 定时任务配置
- **客户发现**: 每天 17:00 自动运行
- **消息发送**: 每天 17:30 自动运行  
- **汇率监控**: 每天 9:00, 14:00, 20:00
- **系统健康检查**: 每30分钟

### 执行限制
- **每日发送上限**: 50条消息
- **发送间隔**: 25-35秒随机
- **静默时间**: 23:00-08:00 (避免打扰)

## 📈 优化方向

### 跟进时机优化
- [ ] 集成尼日利亚当地节假日API
- [ ] 添加客户响应时间分析
- [ ] 实现智能重试机制

### 客户分析报告增强  
- [ ] 添加竞争对手价格对比
- [ ] 客户采购周期预测
- [ ] 地理热力图可视化

### WhatsApp自动化增强
- [ ] A/B测试不同话术效果
- [ ] 自动回复处理功能
- [ ] 发送效果追踪统计