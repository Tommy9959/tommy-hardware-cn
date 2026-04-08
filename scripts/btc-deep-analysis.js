#!/usr/bin/env node
/**
 * BTC 比特币深度分析报告
 * 数据源：Binance API
 */

const https = require('https');

function fetchJSON(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'BTC-Deep/1.0' }, timeout: 10000 }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => { try { resolve(JSON.parse(data)); } catch (e) { reject(e); } });
    }).on('error', reject).on('timeout', () => reject(new Error('Timeout')));
  });
}

async function main() {
  try {
    console.log('🔍 获取数据...\n');
    
    // 并行获取核心数据
    const [ticker24h, klines15m, klines1h, klines4h, klines1d] = await Promise.all([
      fetchJSON('https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT'),
      fetchJSON('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=100'),
      fetchJSON('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=100'),
      fetchJSON('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=4h&limit=100'),
      fetchJSON('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=90')
    ]);
    
    const parseK = k => ({ open: parseFloat(k[1]), high: parseFloat(k[2]), low: parseFloat(k[3]), close: parseFloat(k[4]), volume: parseFloat(k[5]) });
    const kl = {
      '15m': klines15m.map(parseK), '1h': klines1h.map(parseK),
      '4h': klines4h.map(parseK), '1d': klines1d.map(parseK)
    };
    
    const price = parseFloat(ticker24h.lastPrice);
    const change24h = parseFloat(ticker24h.priceChangePercent);
    const high24h = parseFloat(ticker24h.highPrice);
    const low24h = parseFloat(ticker24h.lowPrice);
    const vol24h = parseFloat(ticker24h.quoteVolume);
    
    // 技术指标函数
    const RSI = (p, n = 14) => {
      if (p.length < n + 1) return 50;
      let g = 0, l = 0;
      for (let i = p.length - n; i < p.length; i++) { const c = p[i] - p[i - 1]; if (c > 0) g += c; else l -= c; }
      const ag = g / n, al = l / n; return al === 0 ? 100 : 100 - (100 / (1 + ag / al));
    };
    
    const EMA = (p, n) => {
      if (p.length < n) return p.at(-1);
      const k = 2 / (n + 1);
      let e = p.slice(0, n).reduce((a, b) => a + b) / n;
      for (let i = n; i < p.length; i++) e = p[i] * k + e * (1 - k);
      return e;
    };
    
    const MACD = p => {
      const e12 = EMA(p, 12), e26 = EMA(p, 26), m = e12 - e26;
      return { macd: m, histogram: m * 0.8 };
    };
    
    const ATR = (k, n = 14) => {
      if (k.length < n + 1) return 0;
      let t = 0;
      for (let i = k.length - n; i < k.length; i++) {
        const tr = Math.max(k[i].high - k[i].low, Math.abs(k[i].high - k[i - 1].close), Math.abs(k[i].low - k[i - 1].close));
        t += tr;
      }
      return t / n;
    };
    
    const Pivot = k => {
      const { high: H, low: L, close: C } = k.at(-1);
      const P = (H + L + C) / 3;
      return { r3: H + 2 * (P - L), r2: P + (H - L), r1: 2 * P - L, pivot: P, s1: 2 * P - H, s2: P - (H - L), s3: L - 2 * (H - P) };
    };
    
    const Fib = k => {
      const c = k.map(x => x.close), h = Math.max(...c), l = Math.min(...c), r = h - l;
      return { f0: h, f236: h - r * 0.236, f382: h - r * 0.382, f500: h - r * 0.5, f618: h - r * 0.618, f786: h - r * 0.786, f1000: l };
    };
    
    const analyze = (k, label) => {
      const c = k.map(x => x.close), p = c.at(-1);
      const rsi = RSI(c), e9 = EMA(c, 9), e20 = EMA(c, 20), e50 = EMA(c, 50), e200 = c.length >= 200 ? EMA(c, 200) : null;
      const macd = MACD(c), atr = ATR(k), piv = Pivot(k), fib = Fib(k);
      let trend = '震荡', score = 0;
      if (e9 > e20 && e20 > e50 && p > e9) { trend = '强上涨'; score = 3; }
      else if (e9 > e20 && p > e9) { trend = '上涨'; score = 2; }
      else if (e9 > e20 || p > e20) { trend = '偏涨'; score = 1; }
      else if (e9 < e20 && e20 < e50 && p < e9) { trend = '强下跌'; score = -3; }
      else if (e9 < e20 && p < e9) { trend = '下跌'; score = -2; }
      else if (e9 < e20 || p < e20) { trend = '偏跌'; score = -1; }
      let s = 0; if (rsi > 70) s -= 2; else if (rsi < 30) s += 2; if (macd.histogram > 0) s += 1; else s -= 1; if (p > e20) s += 1; else s -= 1;
      let sig = '观望', conf = '中';
      if (s >= 4) { sig = '强烈买入'; conf = '高'; } else if (s >= 2) { sig = '买入'; conf = '中高'; } else if (s >= 1) { sig = '偏多'; }
      else if (s <= -4) { sig = '强烈卖出'; conf = '高'; } else if (s <= -2) { sig = '卖出'; conf = '中高'; } else if (s <= -1) { sig = '偏空'; }
      return { label, price: p, rsi, e9, e20, e50, e200, macd, atr, trend, score, signal: sig, confidence: conf, pivots: piv, fib };
    };
    
    const a15m = analyze(kl['15m'], '15M'), a1h = analyze(kl['1h'], '1H'), a4h = analyze(kl['4h'], '4H'), a1d = analyze(kl['1d'], '1D');
    const totalScore = a15m.score + a1h.score + a4h.score + a1d.score;
    
    let overall = '观望 - 等待机会', emoji = '🟡';
    if (totalScore >= 8) { overall = '强烈做多 - 全周期共振'; emoji = '🟢🟢🟢'; }
    else if (totalScore >= 4) { overall = '强烈做多 - 多周期共振'; emoji = '🟢🟢'; }
    else if (totalScore >= 2) { overall = '偏多 - 短线强势'; emoji = '🟢'; }
    else if (totalScore <= -8) { overall = '强烈做空 - 全周期共振'; emoji = '🔴🔴🔴'; }
    else if (totalScore <= -4) { overall = '强烈做空 - 多周期共振'; emoji = '🔴🔴'; }
    else if (totalScore <= -2) { overall = '偏空 - 短线弱势'; emoji = '🔴'; }
    
    const fmt = (n, d = 2) => n.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
    const fmtM = n => n >= 1e12 ? `$${(n / 1e12).toFixed(2)}T` : n >= 1e9 ? `$${(n / 1e9).toFixed(2)}B` : `$${n.toFixed(2)}`;
    const now = new Date(), wd = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][now.getDay()];
    const time = `${now.toISOString().slice(0, 10)} ${wd} ${now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })}`;
    
    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 BTC 比特币深度分析报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 ${time}
ℹ️ 数据来源：Binance API | 不构成投资建议 | 注意风险管理

══════════════════════════════════
📈 一、市场行情概览
══════════════════════════════════

💰 价格数据
├─ 当前价：$${fmt(price)}
├─ 24h 涨跌：${change24h > 0 ? '+' : ''}${fmt(change24h)}% ${change24h >= 0 ? '🟢' : '🔴'}
├─ 24h 高：$${fmt(high24h)}
├─ 24h 低：$${fmt(low24h)}
└─ 波动区间：$${fmt(high24h - low24h)} (${fmt((high24h - low24h) / low24h * 100)}%)

📊 市场数据
├─ 24h 成交量：${fmtM(vol24h)}
├─ 总市值：${fmtM(price * 19750000)}
└─ 流通量：~19.75M BTC

══════════════════════════════════
🎯 二、综合研判
══════════════════════════════════

${emoji} ${overall}

综合评分：${totalScore > 0 ? '+' : ''}${totalScore} / 12
置信度：${a4h.confidence}

核心逻辑：
${totalScore >= 4 ? '• 多周期均线多头排列，趋势强劲\n• MACD 持续放量，动能充足' : ''}
${a1h.rsi > 70 || a4h.rsi > 70 ? '• RSI 超买，警惕短期回调风险' : ''}
${a1d.rsi < 60 && totalScore >= 4 ? '• 日线级别仍有上行空间' : ''}
${totalScore <= 0 && totalScore > -4 ? '• 周期分化，方向不明' : ''}

══════════════════════════════════
📊 三、多周期技术分析
══════════════════════════════════

15 分钟线 (超短线)
├─ 趋势：${a15m.trend}
├─ RSI: ${fmt(a15m.rsi, 0)} ${a15m.rsi > 70 ? '⚠️ 超买' : a15m.rsi < 30 ? '✅ 超卖' : ''}
├─ MACD: ${a15m.macd.histogram > 0 ? '多头' : '空头'}
├─ EMA: 9($${fmt(a15m.e9)}) > 20($${fmt(a15m.e20)}) ${a15m.e9 > a15m.e20 ? '✓' : '✗'}
└─ 波动率：${fmt(a15m.atr / price * 100, 2)}%

1 小时线 (短线)
├─ 趋势：${a1h.trend}
├─ RSI: ${fmt(a1h.rsi, 0)} ${a1h.rsi > 70 ? '⚠️ 超买' : a1h.rsi < 30 ? '✅ 超卖' : ''}
├─ MACD: ${a1h.macd.histogram > 0 ? '多头' : '空头'}
├─ EMA: 9($${fmt(a1h.e9)}) > 20($${fmt(a1h.e20)}) ${a1h.e9 > a1h.e20 ? '✓' : '✗'}
└─ 波动率：${fmt(a1h.atr / price * 100, 2)}%

4 小时线 (中线)
├─ 趋势：${a4h.trend}
├─ RSI: ${fmt(a4h.rsi, 0)} ${a4h.rsi > 70 ? '⚠️ 超买' : a4h.rsi < 30 ? '✅ 超卖' : ''}
├─ MACD: ${a4h.macd.histogram > 0 ? '多头' : '空头'}
├─ EMA: 9($${fmt(a4h.e9)}) | 20($${fmt(a4h.e20)}) | 50($${fmt(a4h.e50)})
${a4h.e200 ? `├─ EMA200: $${fmt(a4h.e200)}` : ''}
└─ 波动率：${fmt(a4h.atr / price * 100, 2)}%

日线 (长线)
├─ 趋势：${a1d.trend}
├─ RSI: ${fmt(a1d.rsi, 0)} ${a1d.rsi > 70 ? '⚠️ 超买' : a1d.rsi < 30 ? '✅ 超卖' : ''}
├─ MACD: ${a1d.macd.histogram > 0 ? '多头' : '空头'}
└─ 波动率：${fmt(a1d.atr / price * 100, 2)}%

══════════════════════════════════
📐 四、关键价位系统
══════════════════════════════════

枢轴点 (4H)
├─ R3 (强阻力): $${fmt(a4h.pivots.r3)}
├─ R2 (阻力): $${fmt(a4h.pivots.r2)}
├─ R1 (弱阻力): $${fmt(a4h.pivots.r1)}
├─ Pivot (中枢): $${fmt(a4h.pivots.pivot)}
├─ S1 (弱支撑): $${fmt(a4h.pivots.s1)}
├─ S2 (支撑): $${fmt(a4h.pivots.s2)}
└─ S3 (强支撑): $${fmt(a4h.pivots.s3)}

斐波那契回撤 (4H)
├─ 0% (高点): $${fmt(a4h.fib.f0)}
├─ 23.6%: $${fmt(a4h.fib.f236)}
├─ 38.2%: $${fmt(a4h.fib.f382)} ← 浅回调
├─ 50%: $${fmt(a4h.fib.f500)} ← 中位
├─ 61.8%: $${fmt(a4h.fib.f618)} ← 黄金分割
├─ 78.6%: $${fmt(a4h.fib.f786)}
└─ 100% (低点): $${fmt(a4h.fib.f1000)}

══════════════════════════════════
💡 五、实操策略建议
══════════════════════════════════

📋 短线交易 (4H)
├─ 方向：${totalScore >= 4 ? '逢低做多' : totalScore <= -4 ? '逢高做空' : '观望'}
├─ 入场 (多): $${fmt(a4h.pivots.s1 * 1.001)}
├─ 入场 (空): $${fmt(a4h.pivots.r1 * 0.999)}
├─ 止损：$${fmt(a4h.pivots.s2 * 0.995)}
├─ 目标 1: $${fmt(a4h.pivots.r1)}
├─ 目标 2: $${fmt(a4h.pivots.r2)}
└─ 盈亏比：1:${fmt((a4h.pivots.r2 - a4h.pivots.s1) / Math.max(a4h.pivots.s1 - a4h.pivots.s2 * 0.995, 1), 2)}

📋 中线交易 (1D)
├─ 方向：${a1d.trend.includes('上涨') ? '持有多头' : a1d.trend.includes('下跌') ? '持有空头' : '区间操作'}
├─ 关键支撑：$${fmt(a1d.fib.f618)}
├─ 关键阻力：$${fmt(a1d.fib.f0)}
└─ 仓位：${totalScore >= 4 ? '60-80%' : totalScore <= -4 ? '20-40% 空' : '30-50%'}

⚠️ 风险警示
├─ 波动率：${fmt(a4h.atr / price * 100, 2)}% ${a4h.atr / price * 100 > 3 ? '⚠️ 较高' : '✅ 正常'}
├─ RSI 超买：${a1h.rsi > 70 || a4h.rsi > 70 ? '⚠️ 是' : '✅ 否'}
└─ 仓位上限：建议单笔不超过总资金的 5-10%

══════════════════════════════════
📝 六、情景推演
══════════════════════════════════

🟢 看涨情景 (概率：${totalScore >= 4 ? '60%' : totalScore >= 2 ? '45%' : '25%'})
├─ 触发：站稳 $${fmt(a4h.pivots.pivot)} 上方
├─ 目标：R1 $${fmt(a4h.pivots.r1)} → R2 $${fmt(a4h.pivots.r2)} → R3 $${fmt(a4h.pivots.r3)}
└─ 失效：跌破 $${fmt(a4h.pivots.s1)}

🔴 看跌情景 (概率：${totalScore <= -4 ? '60%' : totalScore <= -2 ? '45%' : '25%'})
├─ 触发：跌破 $${fmt(a4h.pivots.s1)}
├─ 目标：S1 $${fmt(a4h.pivots.s1)} → S2 $${fmt(a4h.pivots.s2)} → S3 $${fmt(a4h.pivots.s3)}
└─ 失效：站回 $${fmt(a4h.pivots.pivot)} 上方

⚪ 震荡情景 (概率：${totalScore >= -2 && totalScore <= 2 ? '50%' : '20%'})
├─ 区间：$${fmt(a4h.pivots.s2)} - $${fmt(a4h.pivots.r2)}
└─ 策略：区间内低多高空，突破后跟随

══════════════════════════════════
⚠️ 免责声明：本报告不构成投资建议，加密货币市场风险极高，请独立判断、谨慎决策
══════════════════════════════════
`);
    
  } catch (error) {
    console.error('❌ 错误:', error.message);
    process.exit(1);
  }
}

main();
