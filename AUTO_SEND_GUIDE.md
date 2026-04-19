# WhatsApp 自动发送操作指南

## 📋 准备工作

### 1. 确认客户文件
确保以下文件存在且包含有效客户数据：
- **客户文件路径**: `/Users/zhuxiaolei/.openclaw/workspace/logs/nigeria-clients/nigeria_verified_clients.csv`
- **必需字段**: `company_name`, `whatsapp` 或 `phone`

### 2. 检查WhatsApp连接状态
```bash
# 检查WhatsApp Bridge状态
openclaw-whatsapp status

# 如果未连接，需要重新配对
openclaw-whatsapp pair
```

### 3. 验证发送限制
- **每日上限**: 50条消息
- **当前已发送**: 查看日志文件确认
- **静默时间**: 23:00-08:00 不发送

## ▶️ 手动执行发送

### 方法1: 直接运行脚本
```bash
cd /Users/zhuxiaolei/.openclaw/workspace/scripts
python3 nigeria-send-afternoon.py
```

### 方法2: 使用OpenClaw命令
```bash
# 在OpenClaw中执行
exec cd /Users/zhuxiaolei/.openclaw/workspace/scripts && python3 nigeria-send-afternoon.py
```

## 🔍 监控发送过程

### 实时日志查看
```bash
# 查看发送日志
tail -f /tmp/openclaw/openclaw-*.log | grep "nigeria-send"

# 查看WhatsApp特定日志  
tail -f /tmp/openclaw/openclaw-*.log | grep "whatsapp"
```

### 发送状态指标
- ✅ **成功发送**: 显示绿色勾号和"发送成功"
- ❌ **发送失败**: 显示红色叉号和错误信息
- ⏳ **等待间隔**: 显示随机等待时间（25-35秒）

## 🛠️ 故障排除

### 常见问题及解决方案

#### 1. WhatsApp连接失败
**症状**: "发送失败: WhatsApp not connected"
**解决**: 
```bash
# 重新配对WhatsApp
openclaw-whatsapp pair

# 等待配对完成后再试
```

#### 2. 号码格式错误
**症状**: "无效号码" 或 "号码不存在"
**解决**:
- 检查CSV文件中的号码格式
- 确保号码为+234开头的国际格式
- 或者0开头的本地格式（脚本会自动转换）

#### 3. 发送频率限制
**症状**: "发送失败: Rate limited"
**解决**:
- 等待1小时后再试
- 检查是否超过每日50条限制
- 调整发送间隔时间

#### 4. 脚本执行权限
**症状**: "Permission denied"
**解决**:
```bash
# 添加执行权限
chmod +x /Users/zhuxiaolei/.openclaw/workspace/scripts/nigeria-send-afternoon.py
```

## 📊 发送后处理

### 1. 查看发送报告
脚本执行完成后会显示总结：
```
📊 发送总结
✅ 成功发送: X 条
📈 总计处理: Y 个客户
```

### 2. 检查客户文件更新
- 成功发送的客户会在数据库中标记为已联系
- 避免重复发送给同一客户

### 3. 监控回复情况
- 通过WhatsApp应用查看客户回复
- 记录高意向客户进行重点跟进

## ⚙️ 高级配置

### 修改发送模板
编辑消息模板在脚本中：
```python
# 文件: nigeria-send-afternoon.py
MESSAGE_TEMPLATE = """你的自定义消息模板"""
```

### 调整发送参数
```python
# 发送间隔 (秒)
interval = random.randint(25, 35)

# 每日上限
if sent_count >= 50:
    break
```

### 添加新的客户来源
修改客户文件路径：
```python
# 文件顶部配置
CLIENTS_FILE = "/新的/客户/文件/路径.csv"
```

## 📱 最佳实践

### 发送时机建议
- **最佳时间**: 工作日下午 14:00-16:00 (拉各斯时间)
- **避免时间**: 周五、周末、节假日
- **季节性**: 避开斋月等宗教节日期间

### 消息内容优化
- **简洁明了**: 控制在200字以内
- **突出优势**: 价格、质量、交货期
- **行动号召**: 明确的下一步行动（查看目录、询价等）
- **联系方式**: 提供多种联系方式

### 客户分层策略
- **A类客户** (高评分): 个性化定制消息
- **B类客户** (中评分): 标准模板消息  
- **C类客户** (低评分): 批量群发消息

---
**注意**: 自动发送功能仅用于商业开发，请遵守当地法律法规和WhatsApp使用条款。