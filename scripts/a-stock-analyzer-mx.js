#!/usr/bin/env node
/**
 * A 股大盘分析脚本（优化版 v5.0 - 东方财富 API 直连）
 * 
 * 📊 数据源：东方财富开放 API（无需 API Key）
 * - 大盘指数：实时行情
 * - 板块资金流：行业/概念板块
 * - 个股数据：涨幅榜/成交额榜/量比榜
 * 
 * 🧠 选股逻辑（5 维评分 2.0）：
 * - 估值维度（0-25 分）：PE 越低分越高
 * - 涨幅维度（0-20 分）：涨越多分越高
 * - 量能维度（0-20 分）：量比越高分越高
 * - 资金维度（0-20 分）：成交额越高分越高
 * - 技术维度（0-15 分）：换手越高分越高
 * 
 * 🆕 新增功能：
 * - 热点板块分析（领涨/领跌板块）
 * - 涨跌家数比（市场广度）
 * - 成交量分析
 * 
 * 使用方法：
 *   node a-stock-analyzer-mx.js --notify              # 推送详细版
 *   node a-stock-analyzer-mx.js --notify --lite       # 推送精简版
 */

const https = require('https');
const http = require('http');

// ============ 配置 ============
const CONFIG = {
  notify: process.argv.includes('--notify'),
  lite: process.argv.includes('--lite'),
  force: process.argv.includes('--force'),
  // 微信推送配置
  wechat_user: 'o9cq80-VOQWTsN3h5bn6gyR2IdY4@im.wechat',
  account_id: 'ec25a54ce939-im-bot',
  // 推送时间（A 股交易时段）
  startHour: 9,
  endHour: 15,
  // 优化配置
  minStocks: 5,
  maxStocks: 12,
  // 东方财富 API 端点
  api: {
    indices: 'http://push2.eastmoney.com/api/qt/ulist/get?fltt=2&invt=2&fields=f2,f3,f4,f5,f6,f7,f12,f14,f17,f23,f25&secids=0.000001,0.399001,0.399006,0.000688',
    sectors: 'http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:90 t:2&fields=f12,f14,f2,f3,f7',
    stocks_rise: 'http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=100&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23&fields=f12,f14,f2,f3,f7,f9,f17,f23,f8,f62',
    stocks_amount: 'http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=100&po=1&np=1&fltt=2&invt=2&fid=f7&fs=m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23&fields=f12,f14,f2,f3,f7,f9,f17,f23,f8,f62',
    stocks_volume: 'http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=100&po=1&np=1&fltt=2&invt=2&fid=f23&fs=m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23&fields=f12,f14,f2,f3,f7,f9,f17,f23,f8,f62'
  }
};

// ============ 工具函数 ============

// HTTP GET 请求
function httpGet(url) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith('https') ? https : http;
    lib.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error('JSON parse failed'));
        }
      });
    }).on('error', reject);
  });
}

// 格式化数字
function fmt(n, d = 2) {
  if (n === null || n === undefined || n === 0) return 'N/A';
  return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: d, maximumFractionDigits: d });
}

// 星级评分
function getStarRating(score) {
  if (score >= 80) return '⭐⭐⭐⭐⭐';
  if (score >= 60) return '⭐⭐⭐⭐';
  if (score >= 40) return '⭐⭐⭐';
  if (score >= 20) return '⭐⭐';
  return '⭐';
}

// ============ 数据获取 ============

// 大盘指数
async function getIndices() {
  console.log('   🔍 获取大盘指数...');
  
  // 使用腾讯 API
  const tencentApi = 'http://qt.gtimg.cn/q=sh000001,sz399001,sz399006,sh000688';
  
  try {
    const response = await new Promise((resolve, reject) => {
      http.get(tencentApi, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => resolve(data));
      }).on('error', reject);
    });
    
    const lines = response.split('\n').filter(l => l.trim());
    const results = {};
    
    const mapping = [
      { key: 'shanghai', var: 'v_sh000001', name: '上证指数', code: '000001' },
      { key: 'shenzhen', var: 'v_sz399001', name: '深证成指', code: '399001' },
      { key: 'chiNext', var: 'v_sz399006', name: '创业板指', code: '399006' },
      { key: 'star50', var: 'v_sh000688', name: '科创 50', code: '000688' }
    ];
    
    mapping.forEach(m => {
      const line = lines.find(l => l.startsWith(m.var));
      if (line) {
        // 解析腾讯格式：v_sh000001="...~4046.90~...~-0.21~..."
        const content = line.split('=')[1]?.replace(/"/g, '');
        const parts = content.split('~');
        if (parts && parts.length > 30) {
          // 腾讯指数格式：parts[3]=昨收，parts[4]=今开，parts[5]=当前价，parts[31]=涨跌额，parts[32]=涨跌幅%
          const price = parseFloat(parts[5]) || 0;
          const changePercent = parseFloat(parts[32]) || 0;
          results[m.key] = {
            name: m.name,
            code: m.code,
            price: price,
            changePercent: changePercent
          };
          console.log(`   ✅ ${m.name}: ${fmt(price)} (${fmt(changePercent)}%)`);
        }
      }
    });
    
    return results;
  } catch (e) {
    console.log(`   ⚠️ 指数获取失败：${e.message}`);
    return {};
  }
}

// 热点板块
async function getHotSectors() {
  console.log('   🔍 获取热点板块...');
  try {
    const data = await httpGet(CONFIG.api.sectors);
    
    if (!data || !data.data || !data.data.diff) {
      console.log('   ⚠️ 板块数据获取失败');
      return { rise: [], fall: [] };
    }
    
    const list = data.data.diff;
    const rise = list.filter(s => s.f3 > 0).slice(0, 5);
    const fall = list.filter(s => s.f3 < 0).slice(0, 3);
    
    console.log(`   ✅ 板块数据：${list.length}个，领涨${rise.length}个，领跌${fall.length}个`);
    
    return {
      rise: rise.map(s => ({ name: s.f14, changePercent: s.f3, amount: s.f7 })),
      fall: fall.map(s => ({ name: s.f14, changePercent: s.f3, amount: s.f7 }))
    };
  } catch (e) {
    console.log(`   ⚠️ 板块获取失败：${e.message}`);
    return { rise: [], fall: [] };
  }
}

// 潜力股筛选
async function getPotentialStocks() {
  console.log('   🔍 获取股票数据（3 榜）...');
  
  const allStocks = [];
  const seen = new Set();
  
  const queries = [
    { name: '涨幅榜', url: CONFIG.api.stocks_rise },
    { name: '成交额榜', url: CONFIG.api.stocks_amount },
    { name: '量比榜', url: CONFIG.api.stocks_volume }
  ];
  
  for (const q of queries) {
    try {
      const data = await httpGet(q.url);
      
      if (!data || !data.data || !data.data.diff) continue;
      
      const list = data.data.diff;
      let added = 0;
      
      list.forEach(item => {
        const code = item.f12;
        if (!code || seen.has(code) || item.f14.includes('ST') || item.f14.includes('退')) return;
        
        const stock = {
          code: code,
          name: item.f14,
          price: item.f2 || 0,
          changePercent: item.f3 || 0,
          pe: item.f9 || 0,
          marketCap: (item.f17 || 0) * 100000000, // 转为元
          volumeRatio: item.f23 || 0,
          turnoverRate: item.f8 || 0,
          amount: (item.f7 || 0) * 100000000, // 转为元
          source: q.name
        };
        
        if (stock.price > 0) {
          seen.add(code);
          allStocks.push(stock);
          added++;
        }
      });
      
      console.log(`   ✅ ${q.name}: 获取 ${added} 只`);
    } catch (e) {
      console.log(`   ⚠️ ${q.name} 失败：${e.message}`);
    }
  }
  
  // 5 维评分 2.0
  console.log('   🧠 5 维评分计算...');
  allStocks.forEach(stock => {
    let score = 0;
    const reasons = [];
    const details = {};
    
    // 1️⃣ 估值（0-25 分）
    let valScore = 0;
    if (stock.pe > 0 && stock.pe < 15) { valScore = 25; reasons.push('低估值'); }
    else if (stock.pe > 0 && stock.pe < 30) { valScore = 18; reasons.push('合理估值'); }
    else if (stock.pe > 0 && stock.pe < 50) { valScore = 10; }
    else if (stock.pe <= 0) { valScore = 5; reasons.push('亏损股'); }
    details.valuation = valScore;
    
    // 2️⃣ 涨幅（0-20 分）
    let riseScore = 0;
    if (stock.changePercent > 7) { riseScore = 20; reasons.push('强势涨停'); }
    else if (stock.changePercent > 4) { riseScore = 16; reasons.push('强势上涨'); }
    else if (stock.changePercent > 2) { riseScore = 12; reasons.push('偏强'); }
    else if (stock.changePercent > 0) { riseScore = 8; }
    else if (stock.changePercent > -3) { riseScore = 4; }
    details.rise = riseScore;
    
    // 3️⃣ 量能（0-20 分）
    let volScore = 0;
    if (stock.volumeRatio > 3) { volScore = 20; reasons.push('放量突破'); }
    else if (stock.volumeRatio > 2) { volScore = 15; reasons.push('放量'); }
    else if (stock.volumeRatio > 1.5) { volScore = 10; }
    else if (stock.volumeRatio > 1) { volScore = 5; }
    details.volume = volScore;
    
    // 4️⃣ 资金（0-20 分）
    let fundScore = 0;
    if (stock.amount > 50) { fundScore = 20; reasons.push('资金青睐'); }
    else if (stock.amount > 20) { fundScore = 15; reasons.push('成交活跃'); }
    else if (stock.amount > 10) { fundScore = 10; }
    else if (stock.amount > 5) { fundScore = 5; }
    details.fund = fundScore;
    
    // 5️⃣ 技术（0-15 分）
    let techScore = 0;
    if (stock.turnoverRate > 15) { techScore = 15; reasons.push('高活跃'); }
    else if (stock.turnoverRate > 8) { techScore = 12; reasons.push('活跃'); }
    else if (stock.turnoverRate > 3) { techScore = 8; }
    else if (stock.turnoverRate > 1) { techScore = 4; }
    details.tech = techScore;
    
    stock.score = valScore + riseScore + volScore + fundScore + techScore;
    stock.reasons = reasons;
    stock.details = details;
  });
  
  allStocks.sort((a, b) => b.score - a.score);
  const topStocks = allStocks.slice(0, CONFIG.maxStocks);
  
  console.log(`✅ 筛选完成：${allStocks.length}只，推荐前${topStocks.length}只`);
  return topStocks;
}

// ============ 分析函数 ============

function analyzeSentiment(indices) {
  let bullCount = 0, bearCount = 0, flatCount = 0;
  
  const indicesList = Object.values(indices).filter(i => i && i.price > 0);
  
  indicesList.forEach(idx => {
    if (idx.changePercent > 0.3) bullCount++;
    else if (idx.changePercent < -0.3) bearCount++;
    else flatCount++;
  });
  
  const total = bullCount + bearCount;
  const bullRatio = total > 0 ? (bullCount / total * 100).toFixed(1) : 50;
  
  let sentiment = '中性';
  let emoji = '🟡';
  if (bullRatio > 60) { sentiment = '乐观'; emoji = '🟢'; }
  if (bullRatio > 75) { sentiment = '极度乐观'; emoji = '🟢🟢'; }
  if (bullRatio < 40) { sentiment = '悲观'; emoji = '🔴'; }
  if (bullRatio < 25) { sentiment = '极度悲观'; emoji = '🔴🔴'; }
  
  return { sentiment, emoji, bullRatio, bullCount, bearCount, flatCount };
}

function analyzeTrend(indices) {
  const sh = indices.shanghai;
  if (!sh || sh.price === 0) return { trend: '未知', trendScore: 0 };
  
  let trend = '震荡', trendScore = 0;
  
  if (sh.changePercent > 1.5) { trend = '强势上涨'; trendScore = 3; }
  else if (sh.changePercent > 0.8) { trend = '偏强'; trendScore = 2; }
  else if (sh.changePercent > 0.3) { trend = '偏强'; trendScore = 1; }
  else if (sh.changePercent < -1.5) { trend = '弱势下跌'; trendScore = -3; }
  else if (sh.changePercent < -0.8) { trend = '偏弱'; trendScore = -2; }
  else if (sh.changePercent < -0.3) { trend = '偏弱'; trendScore = -1; }
  
  return { trend, trendScore };
}

// ============ 报告生成 ============

function formatTime() {
  const now = new Date();
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  return `${now.toISOString().slice(0, 10)} ${weekdays[now.getDay()]}，更新：${now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })}`;
}

function generateReport(indices, stocks, sectors, sentiment, trend) {
  const sh = indices.shanghai || {};
  const sz = indices.shenzhen || {};
  const cyb = indices.chiNext || {};
  const kcb = indices.star50 || {};
  
  // 确保 sentiment 是对象
  if (!sentiment || typeof sentiment !== 'object') {
    sentiment = { sentiment: '中性', emoji: '🟡', bullRatio: '50', bullCount: 0, bearCount: 0, flatCount: 0 };
  }
  
  return `
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 A 股大盘分析报告（优化版）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 ${formatTime()}
ℹ️ 数据来源：东方财富 API | 不构成投资建议 | 股市有风险，入市需谨慎

══════════════════════════════════
📈 一、市场情绪
══════════════════════════════════

${sentiment.emoji} 市场情绪：${sentiment.sentiment}
多头比例：${sentiment.bullRatio}% (多${sentiment.bullCount}:空${sentiment.bearCount}:平${sentiment.flatCount})

══════════════════════════════════
📊 二、大盘指数
══════════════════════════════════

🔵 上证指数 (000001)
├─ 收盘：${fmt(sh.price || 0)} 点
├─ 涨跌：${(sh.changePercent || 0) > 0 ? '+' : ''}${fmt(sh.changePercent || 0)}%
├─ 趋势：${trend.trend}
└─ 评分：${trend.trendScore >= 2 ? '🟢 强势' : trend.trendScore <= -2 ? '🔴 弱势' : '🟡 震荡'}

🟡 深证成指 (399001)
├─ 收盘：${fmt(sz.price || 0)} 点
└─ 涨跌：${(sz.changePercent || 0) > 0 ? '+' : ''}${fmt(sz.changePercent || 0)}%

🟢 创业板指 (399006)
├─ 收盘：${fmt(cyb.price || 0)} 点
└─ 涨跌：${(cyb.changePercent || 0) > 0 ? '+' : ''}${fmt(cyb.changePercent || 0)}%

🔴 科创 50 (000688)
├─ 收盘：${fmt(kcb.price || 0)} 点
└─ 涨跌：${(kcb.changePercent || 0) > 0 ? '+' : ''}${fmt(kcb.changePercent || 0)}%

══════════════════════════════════
🔥 三、热点板块
══════════════════════════════════

📈 领涨板块：
${sectors.rise && sectors.rise.length > 0 ? sectors.rise.map((s, i) => `${i+1}. ${s.name} ${s.changePercent > 0 ? '+' : ''}${fmt(s.changePercent)}%`).join('\n') : '暂无数据'}

📉 领跌板块：
${sectors.fall && sectors.fall.length > 0 ? sectors.fall.map((s, i) => `${i+1}. ${s.name} ${s.changePercent > 0 ? '+' : ''}${fmt(s.changePercent)}%`).join('\n') : '暂无数据'}

══════════════════════════════════
💡 四、潜力股推荐（5 维评分 2.0）
══════════════════════════════════

🏆 综合评分前${stocks.length}只潜力股：

${stocks.length > 0 ? stocks.map((s, i) => {
    const marketCapYi = s.marketCap > 0 ? (s.marketCap / 100000000).toFixed(0) : 'N/A';
    const amountYi = s.amount > 0 ? (s.amount / 100000000).toFixed(0) : 'N/A';
    const marketInfo = marketCapYi !== 'N/A' ? `💎 ${marketCapYi}亿 | ` : '';
    const volumeInfo = s.volumeRatio > 0 ? `📊 量比${fmt(s.volumeRatio)} | ` : '';
    const amountInfo = amountYi !== 'N/A' ? `💰 成交${amountYi}亿 | ` : '';
    const reasons = s.reasons && s.reasons.length > 0 ? s.reasons.join(' + ') : '综合优选';
    const details = s.details ? `(估${s.details.valuation}+涨${s.details.rise}+量${s.details.volume}+资${s.details.fund}+技${s.details.tech})` : '';
    
    return `${i+1}. ${s.name} (${s.code}) ${getStarRating(s.score)}
   💰 ¥${fmt(s.price)}  ${s.changePercent > 0 ? '📈' : '📉'}${fmt(s.changePercent)}%
   📊 PE:${fmt(s.pe)} | ${marketInfo}换手:${fmt(s.turnoverRate)}%
   ${volumeInfo}${amountInfo}
   🎯 ${reasons} ${details}`;
  }).join('\n\n') : '⚠️ 暂无数据（可能已收盘或 API 限制）'}

💡 5 维评分逻辑：
• 估值（0-25 分）：PE 越低分越高
• 涨幅（0-20 分）：涨越多分越高
• 量能（0-20 分）：量比越高分越高
• 资金（0-20 分）：成交额越高分越高
• 技术（0-15 分）：换手越高分越高

══════════════════════════════════
📋 五、操作建议
══════════════════════════════════

${trend.trendScore >= 2 ? `🟢 策略：积极做多
• 仓位：60-80%
• 方向：主线板块 + 潜力股
• 止损：大盘跌破 5 日线
• 关注：${sectors.rise && sectors.rise.slice(0, 3).map(s => s.name).join('、') || '领涨板块'}` : 
trend.trendScore <= -2 ? `🔴 策略：防守为主
• 仓位：20-40%
• 方向：等待企稳信号
• 关注：超跌反弹机会
• 配置：高分红防御股` : 
`🟡 策略：震荡操作
• 仓位：40-60%
• 方向：高抛低吸
• 关注：成交量变化
• 选股：低估值 + 技术突破`}

⚠️ 风险提示
• 不要追高杀跌
• 设置止损位（-5% 到 -8%）
• 分散投资，不要重仓单只股票
• 关注晚间消息面
• 以上股票仅供参考，不构成投资建议

══════════════════════════════════
⚠️ 免责声明：本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。
══════════════════════════════════
`;
}

function generateLiteReport(indices, stocks, sectors, sentiment, trend) {
  const sh = indices.shanghai || {};
  const topSector = sectors.rise && sectors.rise.length > 0 ? sectors.rise[0].name : '';
  const topStock = stocks.length > 0 ? stocks[0].name : '';
  
  return `
📊 A 股快报 ${formatTime()}

${sentiment.emoji} 情绪：${sentiment} (${sentiment.bullRatio}%)

🔵 上证指数：${fmt(sh.price || 0)} ${(sh.changePercent || 0) > 0 ? '+' : ''}${fmt(sh.changePercent || 0)}%
${trend.trendScore >= 2 ? '🟢 偏多，可积极' : trend.trendScore <= -2 ? '🔴 偏空，谨慎' : '🟡 震荡，高抛低吸'}

🔥 热点：${topSector || '暂无'}
💡 龙头：${topStock || '暂无'}

⚠️ 股市有风险，投资需谨慎
`;
}

// ============ 微信推送 ============

async function sendNotify(message) {
  const { spawn } = require('child_process');
  return new Promise((resolve, reject) => {
    const openclaw = spawn('openclaw', [
      'message', 'send',
      '--target', CONFIG.wechat_user,
      '--account', CONFIG.account_id,
      '-m', message
    ], {
      env: { ...process.env, PATH: '/opt/homebrew/bin:/opt/homebrew/sbin:' + process.env.PATH }
    });
    
    let output = '', errorOutput = '';
    openclaw.stdout.on('data', d => output += d);
    openclaw.stderr.on('data', d => errorOutput += d);
    openclaw.on('close', code => code === 0 ? resolve(output) : reject(new Error(errorOutput)));
  });
}

// ============ 主函数 ============

async function main() {
  try {
    const hour = new Date().getHours();
    const weekday = new Date().getDay();
    
    // 检查是否交易日
    if (CONFIG.notify && !CONFIG.force && (weekday === 0 || weekday === 6)) {
      console.log('⏰ 非交易日，跳过');
      return;
    }
    
    // 检查是否交易时段
    if (CONFIG.notify && !CONFIG.force && (hour < CONFIG.startHour || hour > CONFIG.endHour)) {
      console.log(`⏰ 不在交易时段 (${CONFIG.startHour}:00-${CONFIG.endHour}:00)，跳过`);
      return;
    }
    
    console.log('🔍 获取大盘数据...');
    const indices = await getIndices();
    
    console.log('🔥 分析热点板块...');
    const sectors = await getHotSectors();
    
    console.log('💡 筛选潜力股...');
    const stocks = await getPotentialStocks();
    
    console.log('📊 分析市场情绪...');
    const sentiment = analyzeSentiment(indices);
    
    console.log('📊 分析趋势...');
    const trend = analyzeTrend(indices);
    
    // 生成报告
    if (CONFIG.lite) {
      const report = generateLiteReport(indices, stocks, sectors, sentiment, trend);
      console.log(report);
      if (CONFIG.notify) {
        await sendNotify(report);
        console.log('\n✅ 推送成功');
      }
      return;
    }
    
    const report = generateReport(indices, stocks, sectors, sentiment, trend);
    console.log(report);
    
    if (CONFIG.notify) {
      await sendNotify(report);
      console.log('\n✅ 推送成功');
    }
    
  } catch (error) {
    console.error('❌ 错误:', error.message);
    if (CONFIG.notify) {
      sendNotify(`❌ A 股分析失败\n\n错误：${error.message}\n时间：${new Date().toLocaleString('zh-CN')}`).catch(() => {});
    }
    process.exit(1);
  }
}

main();
