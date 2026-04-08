# 📊 比特币技术分析推送

## 功能

- ⏰ **推送时间**: 每天 8:00-22:00，每小时一次（共 15 次）
- 📈 **分析内容**:
  - 4 小时技术指标（RSI、EMA20/50、支撑/阻力）
  - 24 小时技术指标
  - 入场时机建议
  - 操作策略

## 文件

- `btc-analyzer.js` - 核心分析脚本
- `btc-analyzer-notify.sh` - 推送脚本（供 cron 调用）

## 手动测试

```bash
# 运行分析
node btc-analyzer.js

# 发送推送
./btc-analyzer-notify.sh
```

## Cron 配置

```
0 8-22 * * * /bin/bash /Users/zhuxiaolei/.openclaw/workspace/scripts/btc-analyzer-notify.sh
```

## 日志

查看推送日志：
```bash
tail -f ~/.openclaw/workspace/logs/btc-analysis.log
```

## 指标说明

- **RSI**: >70 超买，<30 超卖
- **EMA**: 20/50 金叉看涨，死叉看跌
- **信号**: 🟢买入 / 🔴卖出 / 观望
