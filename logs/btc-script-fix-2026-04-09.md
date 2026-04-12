# BTC 脚本修复记录 - 2026-04-09 23:02

## 问题描述
主人反馈晚上 10 点钟没有收到 BTC 推送，脚本没有生效。

## 问题排查

### 1. 检查 crontab 配置
```bash
crontab -l
```
发现 BTC 任务配置了两次（重复）：
```
0 8-22 * * * /opt/homebrew/bin/node /Users/zhuxiaolei/.openclaw/workspace/scripts/btc-analyzer.js --notify >> /Users/zhuxiaolei/.openclaw/workspace/logs/btc-analysis.log 2>&1
```

### 2. 检查脚本执行日志
```bash
cat ~/.openclaw/workspace/logs/btc-analysis.log | tail -30
```
发现错误：
```
⚠️ 警告：K 线数据不可用，使用简化分析模式
❌ 错误：Cannot read properties of null (reading 'trend')
```

### 3. 根本原因分析
脚本在获取 K 线数据失败后，`klines` 对象为空或某些时间周期为 `undefined`，但在生成卡片时直接访问了 `a15m.trend`、`a1h.trend` 等属性，导致报错。

**具体错误点：**
- Gate.io API 返回错误：`Invalid currency pair BTCUSDT`（应该是 `BTC_USDT`）
- 虽然 symbolMap 配置了映射，但 `fetchFromSource` 函数中没有使用映射后的符号
- K 线数据获取失败后，生成卡片时没有正确处理 `null` 值

## 修复内容

### 修复 1: 使用 symbolMap 转换交易对符号
在 `fetchFromSource` 函数中添加：
```javascript
const mappedSymbol = source.symbolMap && source.symbolMap[symbol] ? source.symbolMap[symbol] : symbol;
```

并在 ticker、orderBook、klines 请求中都使用 `mappedSymbol`。

### 修复 2: 处理 K 线数据不可用的情况
在 `generateCard` 函数中，添加条件判断：
```javascript
const hasKlines = klines && klines['1h'] && klines['1h'].length > 0;

if (!hasKlines) {
  console.log('⚠️ 警告：K 线数据不可用，使用简化分析模式');
}

const a15m = hasKlines && klines['15m'] ? analyze(klines['15m'], '15M') : null;
// ... 其他周期同理
```

### 修复 3: 卡片模板条件渲染
将技术分析、关键价位、策略建议等部分改为条件渲染：
```javascript
${hasKlines ? `详细分析内容` : '⚠️ K 线数据暂时不可用，无法提供详细技术分析'}
```

### 修复 4: Gate.io 数据解析优化
修复 Gate.io ticker 数据解析逻辑，支持多种数据格式。

## 测试结果

```bash
/opt/homebrew/bin/node /Users/zhuxiaolei/.openclaw/workspace/scripts/btc-analyzer.js
```

✅ 成功输出：
```
💰 价格数据
├─ 当前价：$71,144.90
├─ 24h 涨跌：+0.39% 🟢
├─ 24h 高：$71,959.70
├─ 24h 低：$70,461.30
└─ 波动区间：$1,498.40 (2.13%)
```

## 待办事项

1. ⚠️ 清理 crontab 中的重复配置（crontab 命令会卡住，需要手动处理）
2. 测试 --notify 参数是否正常工作（需在 8:00-22:00 时段内）

## 下一步

明天（2026-04-10）早上 8 点起，BTC 推送应该可以正常工作了。
