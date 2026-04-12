#!/usr/bin/env node
/**
 * 比特币专业行情分析卡片（增强版）
 * 数据源：Binance API
 * 输出：结构化详细分析卡片
 * 
 * 使用方法：
 *   node btc-analyzer.js --notify  # 推送分析结果
 *   node btc-analyzer.js           # 仅输出到控制台
 */

const https = require('https');
const { spawn } = require('child_process');
const { HttpsProxyAgent } = require('https-proxy-agent');

// 不使用代理，直接访问

// ============ 多数据源配置 ============
// 主数据源：Binance（全球最大交易所）
// 备用 1：OKX（亚洲主流交易所）
// 备用 2：CoinGecko（聚合数据，无需 API key）
// 备用 3：Gate.io（备用交易所）
// 备用 4：Kraken（欧美主流交易所）

const API_SOURCES = [
  {
    name: 'Binance',
    baseUrl: 'https://api.binance.com/api/v3',
    endpoints: {
      ticker: (symbol) => `/ticker/24hr?symbol=${symbol}`,
      depth: (symbol) => `/depth?symbol=${symbol}&limit=20`,
      klines: (symbol, interval, limit) => `/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`
    },
    symbolMap: { 'BTCUSDT': 'BTCUSDT' },
    priority: 1
  },
  {
    name: 'OKX',
    baseUrl: 'https://www.okx.com/api/v5',
    endpoints: {
      ticker: (symbol) => `/market/ticker?instId=${symbol.replace('USDT', '-USDT').replace('--', '-')}`,
      depth: (symbol) => `/market/books?instId=${symbol.replace('USDT', '-USDT').replace('--', '-')}&sz=20`,
      klines: (symbol, interval, limit) => {
        // OKX bar 参数映射：15m → 15m, 1h → 1H, 4h → 4H, 1d → 1D
        const barMap = { '15m': '15m', '1h': '1H', '4h': '4H', '1d': '1D' };
        const bar = barMap[interval] || interval;
        return `/market/candles?instId=${symbol.replace('USDT', '-USDT').replace('--', '-')}&bar=${bar}&limit=${limit}`;
      }
    },
    symbolMap: { 'BTCUSDT': 'BTC-USDT' },
    priority: 2
  },
  {
    name: 'Gate.io',
    baseUrl: 'https://api.gateio.ws/api/v4',
    endpoints: {
      ticker: (symbol) => `/spot/tickers?currency_pair=${symbol}`,
      depth: (symbol) => `/spot/order_books?currency_pair=${symbol}&limit=20`,
      klines: (symbol, interval, limit) => `/spot/candlesticks?currency_pair=${symbol}&interval=${interval}&limit=${limit}`
    },
    symbolMap: { 'BTCUSDT': 'BTC_USDT' },
    priority: 3
  },
  {
    name: 'CoinGecko',
    baseUrl: 'https://api.coingecko.com/api/v3',
    endpoints: {
      ticker: () => `/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true`,
      depth: () => null, // 不支持
      klines: () => null // 不支持 K 线
    },
    symbolMap: { 'BTCUSDT': 'bitcoin' },
    priority: 4,
    note: '仅基础价格，无 K 线'
  }
];

const CONFIG = {
  notify: process.argv.includes('--notify'),
  force: process.argv.includes('--force'), // 强制推送，跳过时间检查
  wechat_user: 'o9cq80-VOQWTsN3h5bn6gyR2IdY4@im.wechat',
  account_id: 'ec25a54ce939-im-bot',
  startHour: 8,
  endHour: 22,
  currentSource: null, // 当前使用的数据源
  maxRetries: 2
};

// ============ 数据获取 ============

// 带重试的 fetchJSON
function fetchJSON(url, sourceName = 'Unknown', retryCount = 0) {
  return new Promise((resolve, reject) => {
    // 使用代理访问（Clash Pro mixed-port: 7890）
    const proxyUrl = new URL('http://127.0.0.1:7890');
    const proxyAgent = new HttpsProxyAgent(proxyUrl);
    
    const options = {
      headers: { 
        'User-Agent': 'BTC-Analyzer/2.0',
        'Accept': 'application/json'
      },
      timeout: 30000, // 增加到 30 秒
      agent: proxyAgent
    };
    
    console.log(`🔍 [${sourceName}] 请求：${url} (重试 ${retryCount}/${CONFIG.maxRetries})`);
    
    https.get(url, options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { 
          const result = JSON.parse(data);
          console.log(`✅ [${sourceName}] 响应成功`);
          resolve(result); 
        }
        catch (e) { 
          console.log(`❌ [${sourceName}] JSON 解析失败：${e.message}`);
          reject(e); 
        }
      });
    }).on('error', (e) => {
      const errorMsg = `${e.message}`;
      console.log(`❌ [${sourceName}] 请求失败：${errorMsg}`);
      
      // 重试逻辑：如果是网络错误且未达到最大重试次数，则重试
      if ((errorMsg.includes('socket disconnected') || errorMsg.includes('Timeout') || errorMsg.includes('ENOTFOUND')) && retryCount < CONFIG.maxRetries) {
        console.log(`🔄 [${sourceName}] 等待 2 秒后重试...`);
        setTimeout(() => {
          fetchJSON(url, sourceName, retryCount + 1)
            .then(resolve)
            .catch(reject);
        }, 2000);
      } else {
        reject(e);
      }
    }).on('timeout', () => {
      console.log(`⏱️ [${sourceName}] 请求超时`);
      
      // 重试逻辑
      if (retryCount < CONFIG.maxRetries) {
        console.log(`🔄 [${sourceName}] 等待 2 秒后重试...`);
        setTimeout(() => {
          fetchJSON(url, sourceName, retryCount + 1)
            .then(resolve)
            .catch(reject);
        }, 2000);
      } else {
        reject(new Error('Timeout'));
      }
    });
  });
}

// 尝试从多个数据源获取数据
async function fetchFromSource(source, symbol = 'BTCUSDT') {
  try {
    // 使用 symbolMap 转换交易对符号（不同交易所格式不同）
    const mappedSymbol = source.symbolMap && source.symbolMap[symbol] ? source.symbolMap[symbol] : symbol;
    console.log(`🔍 [${source.name}] 原始符号：${symbol}, 映射后：${mappedSymbol}`);
    
    const tickerUrl = source.baseUrl + source.endpoints.ticker(mappedSymbol);
    const tickerData = await fetchJSON(tickerUrl, source.name);
    
    // 尝试获取订单簿（可选）
    let orderBook = null;
    if (source.endpoints.depth) {
      try {
        const depthUrl = source.baseUrl + source.endpoints.depth(mappedSymbol);
        orderBook = await fetchJSON(depthUrl, source.name);
      } catch (e) {
        console.log(`⚠️ [${source.name}] 订单簿获取失败，继续...`);
      }
    }
    
    // 尝试获取 K 线（可选）
    let klines = {};
    if (source.endpoints.klines) {
      const intervals = ['15m', '1h', '4h', '1d'];
      for (const interval of intervals) {
        try {
          const klineUrl = source.baseUrl + source.endpoints.klines(mappedSymbol, interval, 100);
          const klineData = await fetchJSON(klineUrl, source.name);
          
          // OKX K 线格式：[time, open, high, low, close, vol, volCcy]
          // Binance K 线格式：[time, open, high, low, close, volume, ...]
          if (Array.isArray(klineData)) {
            if (interval === '1d') console.log(`[DEBUG] ${source.name} 日线原始数据：`, JSON.stringify(klineData.slice(0, 2)));
klines[interval] = klineData.map(k => {
              // Gate.io 格式：[time, volume, open, close, high, low, ...]
              // 标准格式：[time, open, high, low, close, volume, ...]
              const isGateIO = source.name === 'Gate.io';
              let open, high, low, close, volume;
              if (isGateIO) {
                // Gate.io 格式：[time, volume, open, close, high, low, ...]
                // 但需要确保 high > low
                const h = parseFloat(k[4]);
                const l = parseFloat(k[5]);
                open = parseFloat(k[2]);
                close = parseFloat(k[3]);
                volume = parseFloat(k[1] || 0);
                high = Math.max(h, l);
                low = Math.min(h, l);
              } else {
                open = parseFloat(k[1]);
                high = parseFloat(k[2]);
                low = parseFloat(k[3]);
                close = parseFloat(k[4]);
                volume = parseFloat(k[5] || 0);
              }
              return { time: k[0], open, high, low, close, volume };
            });
          } else if (klineData.data && Array.isArray(klineData.data)) {
            // OKX 返回格式
            klines[interval] = klineData.data.map(k => ({
              time: k[0],
              open: parseFloat(k[1]),
              high: parseFloat(k[2]),
              low: parseFloat(k[3]),
              close: parseFloat(k[4]),
              volume: parseFloat(k[5] || 0)
            }));
          }
        } catch (e) {
          console.log(`⚠️ [${source.name}] ${interval} K 线获取失败：${e.message}`);
        }
      }
    }
    
    return { ticker: tickerData, orderBook, klines, source: source.name };
  } catch (e) {
    throw new Error(`[${source.name}] 数据获取失败：${e.message}`);
  }
}

// 智能故障转移：按优先级尝试多个数据源
async function getMarketData() {
  console.log('🔄 开始尝试获取市场数据...');
  
  for (const source of API_SOURCES) {
    try {
      console.log(`🎯 尝试数据源 #${source.priority}: ${source.name}`);
      const rawData = await fetchFromSource(source);
      
      // 标准化数据格式
      const normalizedData = normalizeData(rawData, source.name);
      
      CONFIG.currentSource = source.name;
      console.log(`✅ 成功使用数据源：${source.name}`);
      return normalizedData;
    } catch (e) {
      console.log(`❌ ${source.name} 失败：${e.message}`);
      console.log(`   尝试下一个数据源...\n`);
    }
  }
  
  throw new Error('所有数据源均不可用');
}

// ============ 数据格式标准化 ============
// 不同 API 返回的数据格式不同，需要统一标准化

function normalizeData(rawData, sourceName) {
  const { ticker, orderBook, klines } = rawData;
  
  // 标准化 ticker 数据
  let normalizedTicker = {};
  
  if (sourceName === 'Binance' || sourceName === 'OKX' || sourceName === 'Gate.io') {
    // 交易所 API 格式
    if (sourceName === 'Binance') {
      normalizedTicker = {
        lastPrice: parseFloat(ticker.lastPrice || ticker.last),
        priceChangePercent: parseFloat(ticker.priceChangePercent),
        high24h: parseFloat(ticker.highPrice),
        low24h: parseFloat(ticker.lowPrice),
        volume24h: parseFloat(ticker.quoteVolume || ticker.volume),
        bidPrice: ticker.bids && ticker.bids[0] ? parseFloat(ticker.bids[0][0]) : null,
        askPrice: ticker.asks && ticker.asks[0] ? parseFloat(ticker.asks[0][0]) : null
      };
    } else if (sourceName === 'OKX') {
      const okxData = ticker.data && ticker.data[0] ? ticker.data[0] : ticker;
      normalizedTicker = {
        lastPrice: parseFloat(okxData.last || okxData.lastPx),
        priceChangePercent: parseFloat(okxData.chg || 0),
        high24h: parseFloat(okxData.high24h || okxData.high24),
        low24h: parseFloat(okxData.low24h || okxData.low24),
        volume24h: parseFloat(okxData.volCcy24h || okxData.vol24h),
        bidPrice: parseFloat(okxData.bidPx || (okxData.bids && okxData.bids[0] ? okxData.bids[0][0] : null)),
        askPrice: parseFloat(okxData.askPx || (okxData.asks && okxData.asks[0] ? okxData.asks[0][0] : null))
      };
    } else if (sourceName === 'Gate.io') {
      // Gate.io tickers API 返回格式：{"BTC_USDT":{"last":"108528.56","change_percentage":"+1.54%",...}}
      let gateData = ticker;
      if (ticker && typeof ticker === 'object' && !Array.isArray(ticker)) {
        // 如果是对象，取 BTC_USDT 或 BTCUSDT 键
        gateData = ticker.BTC_USDT || ticker.BTCUSDT || ticker;
      } else if (Array.isArray(ticker)) {
        gateData = ticker[0];
      }
      
      // 解析涨跌幅（去除 % 符号）
      let changePct = 0;
      if (gateData.change_percentage) {
        changePct = parseFloat(gateData.change_percentage.replace('%', '')) || 0;
      } else if (gateData.changePercentage) {
        changePct = parseFloat(gateData.changePercentage) || 0;
      }
      
      normalizedTicker = {
        lastPrice: parseFloat(gateData.last || gateData.close || 0),
        priceChangePercent: changePct,
        high24h: parseFloat(gateData.high24h || gateData.high_24h || gateData.high),
        low24h: parseFloat(gateData.low24h || gateData.low_24h || gateData.low),
        volume24h: parseFloat(gateData.quoteVolume || gateData.quote_volume_24h || gateData.volume),
        bidPrice: gateData.highestBid ? parseFloat(gateData.highestBid) : (gateData.bid ? parseFloat(gateData.bid) : null),
        askPrice: gateData.lowestAsk ? parseFloat(gateData.lowestAsk) : (gateData.ask ? parseFloat(gateData.ask) : null)
      };
    }
  } else if (sourceName === 'CoinGecko') {
    // CoinGecko 格式（仅基础价格）
    const btcData = ticker.bitcoin || {};
    normalizedTicker = {
      lastPrice: btcData.usd || 0,
      priceChangePercent: btcData.usd_24h_change || 0,
      high24h: null,
      low24h: null,
      volume24h: btcData.usd_24h_vol || 0,
      bidPrice: null,
      askPrice: null
    };
  }
  
  // 标准化订单簿
  let normalizedOrderBook = null;
  if (orderBook) {
    if (sourceName === 'Binance') {
      normalizedOrderBook = {
        bids: orderBook.bids || [],
        asks: orderBook.asks || []
      };
    } else if (sourceName === 'OKX') {
      normalizedOrderBook = {
        bids: orderBook.data && orderBook.data[0] ? (orderBook.data[0].bids || []) : [],
        asks: orderBook.data && orderBook.data[0] ? (orderBook.data[0].asks || []) : []
      };
    } else if (sourceName === 'Gate.io') {
      normalizedOrderBook = {
        bids: orderBook.bids || orderBook.asks ? [] : [],
        asks: orderBook.asks || []
      };
    }
  }
  
  // K 线数据已经是标准化格式
  const normalizedKlines = klines;
  
  return {
    ticker: normalizedTicker,
    orderBook: normalizedOrderBook,
    klines: normalizedKlines,
    source: sourceName
  };
}

// ============ 技术指标 ============

function RSI(prices, period = 14) {
  if (prices.length < period + 1) return 50;
  let gains = 0, losses = 0;
  for (let i = prices.length - period; i < prices.length; i++) {
    const change = prices[i] - prices[i - 1];
    if (change > 0) gains += change; else losses -= change;
  }
  const avgGain = gains / period, avgLoss = losses / period;
  if (avgLoss === 0) return 100;
  return 100 - (100 / (1 + avgGain / avgLoss));
}

function EMA(prices, period) {
  if (prices.length < period) return prices.at(-1);
  const k = 2 / (period + 1);
  let ema = prices.slice(0, period).reduce((a, b) => a + b) / period;
  for (let i = period; i < prices.length; i++) ema = prices[i] * k + ema * (1 - k);
  return ema;
}

function SMA(prices, period) {
  if (prices.length < period) return prices.at(-1);
  return prices.slice(-period).reduce((a, b) => a + b, 0) / period;
}

function MACD(prices) {
  const ema12 = EMA(prices, 12), ema26 = EMA(prices, 26);
  const macd = ema12 - ema26;
  const signal = EMA([macd, ...prices.slice(-9).map((_, i) => EMA(prices.slice(0, prices.length - 26 + i), 12) - EMA(prices.slice(0, prices.length - 26 + i), 26))], 9);
  const histogram = macd - signal;
  return { macd, signal, histogram };
}

function Bollinger(prices, period = 20, stdDev = 2) {
  if (prices.length < period) return { upper: prices.at(-1), middle: prices.at(-1), lower: prices.at(-1), width: 0 };
  const slice = prices.slice(-period);
  const middle = slice.reduce((a, b) => a + b) / period;
  const variance = slice.reduce((s, p) => s + (p - middle) ** 2, 0) / period;
  const sd = Math.sqrt(variance);
  return {
    upper: middle + stdDev * sd,
    middle,
    lower: middle - stdDev * sd,
    width: (2 * stdDev * sd / middle) * 100
  };
}

function ATR(ohlcv, period = 14) {
  if (ohlcv.length < period + 1) return 0;
  let trSum = 0;
  for (let i = ohlcv.length - period; i < ohlcv.length; i++) {
    const { high, low } = ohlcv[i];
    const prevClose = ohlcv[i - 1].close;
    trSum += Math.max(high - low, Math.abs(high - prevClose), Math.abs(low - prevClose));
  }
  return trSum / period;
}

function Stochastic(ohlcv, kPeriod = 14, dPeriod = 3) {
  if (ohlcv.length < kPeriod) return { k: 50, d: 50 };
  const lows = ohlcv.slice(-kPeriod).map(k => k.low);
  const highs = ohlcv.slice(-kPeriod).map(k => k.high);
  const currentClose = ohlcv.at(-1).close;
  const lowestLow = Math.min(...lows);
  const highestHigh = Math.max(...highs);
  const k = ((currentClose - lowestLow) / (highestHigh - lowestLow)) * 100;
  // 简化 D 值
  const d = k;
  return { k, d };
}

function VolumeProfile(ohlcv) {
  const recent = ohlcv.slice(-20);
  const totalVol = recent.reduce((s, k) => s + k.volume, 0);
  const avgVol = totalVol / recent.length;
  const currentVol = ohlcv.at(-1).volume;
  return { currentVol, avgVol, ratio: currentVol / avgVol };
}

function calculatePivots(ohlcv) {
  const last = ohlcv.at(-1);
  const { high: H, low: L, close: C } = last;
  const P = (H + L + C) / 3;
  return {
    r3: H + 2 * (P - L),
    r2: P + (H - L),
    r1: 2 * P - L,
    pivot: P,
    s1: 2 * P - H,
    s2: P - (H - L),
    s3: L - 2 * (H - P)
  };
}

function calculateFib(ohlcv) {
  const closes = ohlcv.map(k => k.close);
  const high = Math.max(...closes), low = Math.min(...closes);
  const range = high - low;
  return {
    fib0: high,
    fib236: high - range * 0.236,
    fib382: high - range * 0.382,
    fib500: high - range * 0.5,
    fib618: high - range * 0.618,
    fib786: high - range * 0.786,
    fib1000: low
  };
}

function getOrderBookImbalance(orderBook) {
  const bids = orderBook.bids.map(b => parseFloat(b[1])).reduce((a, b) => a + b, 0);
  const asks = orderBook.asks.map(a => parseFloat(a[1])).reduce((a, b) => a + b, 0);
  const total = bids + asks;
  return {
    bidVol: bids,
    askVol: asks,
    ratio: bids / total,
    imbalance: ((bids - asks) / total) * 100
  };
}

// ============ 分析引擎 ============

function analyze(klines, label, dailyKlines = null) {
  const closes = klines.map(k => k.close);
  const price = closes.at(-1);
  
  const rsi = RSI(closes);
  const ema9 = EMA(closes, 9);
  const ema20 = EMA(closes, 20);
  const ema50 = EMA(closes, 50);
  const ema200 = closes.length >= 200 ? EMA(closes, 200) : null;
  const sma20 = SMA(closes, 20);
  const macd = MACD(closes);
  const bb = Bollinger(closes);
  const atr = ATR(klines);
  const stoch = Stochastic(klines);
  const volProfile = VolumeProfile(klines);
  // 枢轴点使用日线数据计算（前一日 High/Low/Close）
  // 使用倒数第二根 K 线（昨天），因为最后一根是今天未完成的 K 线
  const pivotKlines = dailyKlines || klines;
  const yesterdayKlines = pivotKlines.length >= 2 ? pivotKlines.slice(0, -1) : pivotKlines;
  const lastCandle = yesterdayKlines.at(-1);
  console.log(`[DEBUG] 枢轴点数据：High=${lastCandle?.high}, Low=${lastCandle?.low}, Close=${lastCandle?.close}`);
  const pivots = calculatePivots(yesterdayKlines);
  const fib = calculateFib(klines);
  
  // 趋势
  let trend = '震荡', trendScore = 0;
  if (ema9 > ema20 && ema20 > ema50 && price > ema9) { trend = '强上涨'; trendScore = 3; }
  else if (ema9 > ema20 && price > ema9) { trend = '上涨'; trendScore = 2; }
  else if (ema9 > ema20 || price > ema20) { trend = '偏涨'; trendScore = 1; }
  else if (ema9 < ema20 && ema20 < ema50 && price < ema9) { trend = '强下跌'; trendScore = -3; }
  else if (ema9 < ema20 && price < ema9) { trend = '下跌'; trendScore = -2; }
  else if (ema9 < ema20 || price < ema20) { trend = '偏跌'; trendScore = -1; }
  
  // 信号评分
  let signalScore = 0;
  const signals = [];
  
  if (rsi > 70) { signalScore -= 2; signals.push('RSI 超买'); }
  else if (rsi < 30) { signalScore += 2; signals.push('RSI 超卖'); }
  
  if (macd.histogram > 0) { signalScore += 1; signals.push('MACD 多头'); }
  else { signalScore -= 1; signals.push('MACD 空头'); }
  
  if (price > bb.middle) { signalScore += 1; }
  else { signalScore -= 1; }
  
  if (stoch.k > 80) { signalScore -= 1; signals.push('KDJ 超买'); }
  else if (stoch.k < 20) { signalScore += 1; signals.push('KDJ 超卖'); }
  
  if (volProfile.ratio > 1.5) signals.push('放量');
  else if (volProfile.ratio < 0.5) signals.push('缩量');
  
  // 综合建议
  let signal = '观望', confidence = '中', action = '等待方向明确';
  if (signalScore >= 4) { signal = '强烈买入'; confidence = '高'; action = '积极做多'; }
  else if (signalScore >= 2) { signal = '买入'; confidence = '中高'; action = '逢低做多'; }
  else if (signalScore >= 1) { signal = '偏多'; confidence = '中'; action = '轻仓试多'; }
  else if (signalScore <= -4) { signal = '强烈卖出'; confidence = '高'; action = '积极做空'; }
  else if (signalScore <= -2) { signal = '卖出'; confidence = '中高'; action = '逢高做空'; }
  else if (signalScore <= -1) { signal = '偏空'; confidence = '中'; action = '轻仓试空'; }
  
  return {
    label, price, rsi, ema9, ema20, ema50, ema200, sma20, macd, bb, atr, stoch, volProfile,
    trend, trendScore, signal, confidence, action, signals, pivots, fib
  };
}

// ============ 报告生成 ============

function formatTime() {
  const now = new Date();
  const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  return `${now.toISOString().slice(0, 10)} ${weekdays[now.getDay()]}，更新：${now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })}`;
}

function fmt(n, d = 2) { return n.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }); }
function fmtMoney(n) {
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  return `$${n.toFixed(2)}`;
}

function generateCard(data) {
  const { ticker, orderBook, klines, source } = data;
  const price = parseFloat(ticker.lastPrice);
  const change24h = parseFloat(ticker.priceChangePercent);
  const high24h = parseFloat(ticker.high24h) || price;
  const low24h = parseFloat(ticker.low24h) || price;
  const vol24h = parseFloat(ticker.volume24h) || 0;
  const marketCap = price * 19750000;
  const obImbalance = orderBook ? getOrderBookImbalance(orderBook) : { imbalance: 0 };
  
  // 检查是否有 K 线数据（至少需要 1h、4h 或 1d 之一）
  const has1h = klines && klines['1h'] && klines['1h'].length > 0;
  const has4h = klines && klines['4h'] && klines['4h'].length > 0;
  const has1d = klines && klines['1d'] && klines['1d'].length > 0;
  const hasKlines = has1h || has4h || has1d;
  
  if (!hasKlines) {
    console.log('⚠️ 警告：K 线数据不可用，使用简化分析模式');
  }
  
  const a15m = (klines && klines['15m'] && klines['15m'].length > 0) ? analyze(klines['15m'], '15M') : null;
  const a1h = has1h ? analyze(klines['1h'], '1H') : null;
  const a4h = has4h ? analyze(klines['4h'], '4H', has1d ? klines['1d'] : null) : null;
  const a1d = has1d ? analyze(klines['1d'], '1D') : null;
  
  // 综合评分（如果 K 线数据不可用，使用简化评分）
  let totalScore = 0;
  if (hasKlines) {
    totalScore = (a15m?.trendScore || 0) + (a1h?.trendScore || 0) + (a4h?.trendScore || 0) + (a1d?.trendScore || 0);
  } else {
    // 简化模式：仅基于价格变化
    totalScore = change24h > 0 ? 2 : change24h < 0 ? -2 : 0;
  }
  let overall = '观望 - 等待机会', overallEmoji = '🟡';
  if (totalScore >= 8) { overall = '强烈做多 - 全周期共振'; overallEmoji = '🟢🟢🟢'; }
  else if (totalScore >= 4) { overall = '强烈做多 - 多周期共振'; overallEmoji = '🟢🟢'; }
  else if (totalScore >= 2) { overall = '偏多 - 短线强势'; overallEmoji = '🟢'; }
  else if (totalScore <= -8) { overall = '强烈做空 - 全周期共振'; overallEmoji = '🔴🔴🔴'; }
  else if (totalScore <= -4) { overall = '强烈做空 - 多周期共振'; overallEmoji = '🔴🔴'; }
  else if (totalScore <= -2) { overall = '偏空 - 短线弱势'; overallEmoji = '🔴'; }
  
  // 订单簿情绪
  let obSentiment = '中性';
  if (obImbalance.imbalance > 10) obSentiment = '多头占优 🟢';
  else if (obImbalance.imbalance < -10) obSentiment = '空头占优 🔴';
  
  // 波动率（优先 4H，其次 1D）
  const pivotSource = a4h || a1d;
  const volatility = pivotSource ? fmt(pivotSource.atr / price * 100, 2) : 'N/A';
  const volatilityStatus = pivotSource && parseFloat(volatility) < 2 ? '✅ 正常' : '⚠️ 较高';
  
  // RSI 超买检查
  const rsiOverbought = (a1h?.rsi > 70) || (a4h?.rsi > 70) || (a1d?.rsi > 70);
  
  // 情景推演概率
  const bullProb = totalScore >= 4 ? 60 : totalScore >= 2 ? 45 : 25;
  const bearProb = totalScore <= -4 ? 60 : totalScore <= -2 ? 45 : 25;
  const neutralProb = 100 - bullProb - bearProb;
  
  // 核心逻辑
  const coreLogic = [];
  if (hasKlines) {
    if (totalScore >= 4) coreLogic.push('多周期均线多头排列，趋势强劲');
    else if (totalScore <= -4) coreLogic.push('多周期均线空头排列，趋势疲弱');
    if (a4h?.macd?.histogram > 0) coreLogic.push('MACD 持续放量，动能充足');
    else coreLogic.push('MACD 动能减弱，需谨慎');
    if (rsiOverbought) coreLogic.push('RSI 超买，警惕短期回调风险');
    if ((a1d?.trendScore || 0) > 0) coreLogic.push('日线级别仍有上行空间');
    else if ((a1d?.trendScore || 0) < 0) coreLogic.push('日线级别承压');
  } else {
    coreLogic.push('K 线数据暂时不可用');
    if (change24h > 0) coreLogic.push('24 小时上涨趋势');
    else if (change24h < 0) coreLogic.push('24 小时下跌趋势');
    else coreLogic.push('价格波动较小');
  }
  
  return `
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 BTC 比特币深度分析报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 ${formatTime()}
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
├─ 24h 成交量：${fmtMoney(vol24h)}
├─ 总市值：${fmtMoney(marketCap)}
└─ 订单簿情绪：${obSentiment}

══════════════════════════════════
🎯 二、综合研判
══════════════════════════════════

${overallEmoji} ${overall}

综合评分：${totalScore > 0 ? '+' : ''}${totalScore} / 12
置信度：${a4h?.confidence || '中'}

核心逻辑：
${coreLogic.map(logic => `• ${logic}`).join('\n')}

══════════════════════════════════
📊 三、多周期技术分析
══════════════════════════════════

${hasKlines ? `15 分钟线 (超短线)
├─ 趋势：${a15m ? a15m.trend : '数据不足'}
├─ RSI: ${a15m ? fmt(a15m.rsi, 0) : 'N/A'}
├─ MACD: ${a15m ? (a15m.macd.histogram > 0 ? '多头' : '空头') : 'N/A'}
├─ EMA: 9(${a15m ? '$'+fmt(a15m.ema9) : 'N/A'}) ${a15m && a15m.ema9 > a15m.ema20 ? '> 20 ✓' : ''}
└─ 波动率：${a15m ? fmt(a15m.atr / a15m.price * 100, 2) + '%' : 'N/A'}

1 小时线 (短线)
├─ 趋势：${a1h ? a1h.trend : '数据不足'}
├─ RSI: ${a1h ? fmt(a1h.rsi, 0) : 'N/A'}${a1h && a1h.rsi > 70 ? ' ⚠️ 超买' : a1h && a1h.rsi < 30 ? ' ⚠️ 超卖' : ''}
├─ MACD: ${a1h ? (a1h.macd.histogram > 0 ? '多头' : '空头') : 'N/A'}
├─ EMA: 9(${a1h ? '$'+fmt(a1h.ema9) : 'N/A'}) ${a1h && a1h.ema9 > a1h.ema20 ? '> 20 ✓' : ''}
└─ 波动率：${a1h ? fmt(a1h.atr / a1h.price * 100, 2) + '%' : 'N/A'}

4 小时线 (中线)
├─ 趋势：${a4h ? a4h.trend : '数据不足'}
├─ RSI: ${a4h ? fmt(a4h.rsi, 0) : 'N/A'}${a4h && a4h.rsi > 70 ? ' ⚠️ 超买' : a4h && a4h.rsi < 30 ? ' ⚠️ 超卖' : ''}
├─ MACD: ${a4h ? (a4h.macd.histogram > 0 ? '多头' : '空头') : 'N/A'}
├─ EMA: 9(${a4h ? '$'+fmt(a4h.ema9) : 'N/A'}) | 20(${a4h ? '$'+fmt(a4h.ema20) : 'N/A'}) | 50(${a4h ? '$'+fmt(a4h.ema50) : 'N/A'})
└─ 波动率：${a4h ? fmt(a4h.atr / a4h.price * 100, 2) + '%' : 'N/A'}

日线 (长线)
├─ 趋势：${a1d ? a1d.trend : '数据不足'}
├─ RSI: ${a1d ? fmt(a1d.rsi, 0) : 'N/A'}
├─ MACD: ${a1d ? (a1d.macd.histogram > 0 ? '多头' : '空头') : 'N/A'}
└─ 波动率：${a1d ? fmt(a1d.atr / a1d.price * 100, 2) + '%' : 'N/A'}` : '⚠️ K 线数据暂时不可用，无法提供详细技术分析\n   请检查网络连接或 API 状态'}

══════════════════════════════════
📐 四、关键价位系统
══════════════════════════════════

${hasKlines && (a4h || a1d) ? `枢轴点 ${a4h ? '(4H)' : '(1D)'}
├─ R3 (强阻力): $${fmt((a4h || a1d).pivots.r3)}
├─ R2 (阻力): $${fmt((a4h || a1d).pivots.r2)}
├─ R1 (弱阻力): $${fmt((a4h || a1d).pivots.r1)}
├─ Pivot (中枢): $${fmt((a4h || a1d).pivots.pivot)}
├─ S1 (弱支撑): $${fmt((a4h || a1d).pivots.s1)}
├─ S2 (支撑): $${fmt((a4h || a1d).pivots.s2)}
└─ S3 (强支撑): $${fmt((a4h || a1d).pivots.s3)}

斐波那契回撤 ${a4h ? '(4H)' : '(1D)'}
├─ 0% (高点): $${fmt((a4h || a1d).fib.fib0)}
├─ 23.6%: $${fmt((a4h || a1d).fib.fib236)}
├─ 38.2%: $${fmt((a4h || a1d).fib.fib382)} ← 浅回调
├─ 50%: $${fmt((a4h || a1d).fib.fib500)} ← 中位
├─ 61.8%: $${fmt((a4h || a1d).fib.fib618)} ← 黄金分割
├─ 78.6%: $${fmt((a4h || a1d).fib.fib786)}
└─ 100% (低点): $${fmt((a4h || a1d).fib.fib1000)}` : '⚠️ K 线数据暂时不可用，无法计算关键价位\n   恢复后将自动提供支撑/阻力分析'}

══════════════════════════════════
${hasKlines && pivotSource ? `💡 五、实操策略建议
══════════════════════════════════

📋 短线交易 (${a4h ? '4H' : '1D'})
├─ 方向：${totalScore >= 2 ? '逢低做多' : totalScore <= -2 ? '逢高做空' : '观望'}
├─ 入场 (多): $${fmt(pivotSource.pivots.s1 * 1.001)}
├─ 入场 (空): $${fmt(pivotSource.pivots.r1 * 0.999)}
├─ 止损：$${fmt(pivotSource.pivots.s2 * 0.995)}
├─ 目标 1: $${fmt(pivotSource.pivots.r1)}
├─ 目标 2: $${fmt(pivotSource.pivots.r2)}
└─ 盈亏比：1:${fmt(Math.abs((pivotSource.pivots.r1 - pivotSource.pivots.s1) / (pivotSource.pivots.s1 - pivotSource.pivots.s2)))}

📋 中线交易 (1D)
├─ 方向：${a1d && a1d.trendScore ? (a1d.trendScore > 0 ? '持有多头' : a1d.trendScore < 0 ? '持有空头' : '观望') : '数据不足'}
├─ 关键支撑：${a1d && a1d.pivots ? '$'+fmt(a1d.pivots.s2) : 'N/A'}
├─ 关键阻力：${a1d && a1d.pivots ? '$'+fmt(a1d.pivots.r2) : 'N/A'}
└─ 仓位：${totalScore >= 4 ? '60-80%' : totalScore >= 2 ? '40-60%' : totalScore <= -4 ? '60-80% 空' : totalScore <= -2 ? '40-60% 空' : '20-30%'}

⚠️ 风险警示
├─ 波动率：${volatility}% ${volatilityStatus}
├─ RSI 超买：${rsiOverbought ? '⚠️ 是' : '✅ 否'}
└─ 仓位上限：建议单笔不超过总资金的 5-10%

══════════════════════════════════
📝 六、情景推演
══════════════════════════════════

🟢 看涨情景 (概率：${bullProb}%)
├─ 触发：站稳 $${fmt(pivotSource.pivots.pivot)} 上方
├─ 目标：R1 $${fmt(pivotSource.pivots.r1)} → R2 $${fmt(pivotSource.pivots.r2)} → R3 $${fmt(pivotSource.pivots.r3)}
└─ 失效：跌破 $${fmt(pivotSource.pivots.s1)}

🔴 看跌情景 (概率：${bearProb}%)
├─ 触发：跌破 $${fmt(pivotSource.pivots.s1)}
├─ 目标：S1 $${fmt(pivotSource.pivots.s1)} → S2 $${fmt(pivotSource.pivots.s2)} → S3 $${fmt(pivotSource.pivots.s3)}
└─ 失效：站回 $${fmt(pivotSource.pivots.pivot)} 上方

⚪ 震荡情景 (概率：${neutralProb}%)
├─ 区间：$${fmt(pivotSource.pivots.s2)} - $${fmt(pivotSource.pivots.r2)}
└─ 策略：区间内低多高空，突破后跟随` : `💡 五、简化建议 (K 线数据不可用)
══════════════════════════════════

📋 当前趋势：${change24h > 0 ? '🟢 24 小时上涨 ' + fmt(change24h) + '%' : change24h < 0 ? '🔴 24 小时下跌 ' + fmt(change24h) + '%' : '⚪ 价格波动较小'}
├─ 建议：等待 K 线数据恢复后再做详细分析
└─ 仓位：建议保持低仓位或观望

⚠️ 提醒：详细技术分析将在 K 线数据恢复后提供`}

══════════════════════════════════
⚠️ 免责声明：本报告不构成投资建议，加密货币市场风险极高，请独立判断、谨慎决策
══════════════════════════════════
`.trim().replace('数据来源：Binance API', `数据来源：${source || 'Binance'} API`);
}

// ============ 推送 ============

function sendNotify(message) {
  return new Promise((resolve, reject) => {
    const openclaw = spawn('/Users/zhuxiaolei/.nvm/versions/node/v24.14.1/bin/openclaw', [
      'message', 'send',
      '-t', CONFIG.wechat_user,
      '--channel', 'openclaw-weixin',
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

// 分段推送长消息（iMessage 有长度限制）
async function sendNotifyInParts(fullMessage, maxPartLength = 3000) {
  const parts = [];
  
  // 如果消息超过最大长度，强制分割
  if (fullMessage.length > maxPartLength) {
    for (let i = 0; i < fullMessage.length; i += maxPartLength) {
      parts.push(fullMessage.slice(i, i + maxPartLength));
    }
  } else {
    parts.push(fullMessage);
  }
  
  // 发送所有分段
  for (let i = 0; i < parts.length; i++) {
    const part = parts[i];
    const prefix = parts.length > 1 ? `(Part ${i+1}/${parts.length}) ` : '';
    console.log(`📱 发送第 ${i+1}/${parts.length} 段...`);
    await sendNotify(prefix + part);
    if (i < parts.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 500)); // 间隔 0.5 秒
    }
  }
  console.log(`✅ 完成 ${parts.length} 段推送`);
}

// ============ 防重复机制 ============
// 使用锁文件防止同一分钟内重复执行
const fs = require('fs');
const path = require('path');
const lockFile = path.join(__dirname, '../logs/.btc-analyzer.lock');

function acquireLock() {
  try {
    if (fs.existsSync(lockFile)) {
      const lockContent = fs.readFileSync(lockFile, 'utf8');
      const lockTime = parseInt(lockContent);
      const now = Date.now();
      // 如果锁是 55 秒内获得的，拒绝执行
      if (now - lockTime < 55000) {
        console.log(`⚠️ 检测到 ${Math.round((now - lockTime) / 1000)} 秒内有其他实例运行，跳过本次执行`);
        return false;
      }
    }
    // 获取锁
    fs.writeFileSync(lockFile, Date.now().toString());
    return true;
  } catch (e) {
    console.log(`⚠️ 锁文件操作失败：${e.message}`);
    return true; // 失败时允许执行
  }
}

function releaseLock() {
  try {
    if (fs.existsSync(lockFile)) {
      fs.unlinkSync(lockFile);
    }
  } catch (e) {
    // 忽略清理错误
  }
}

// ============ 主函数 ============

async function main() {
  try {
    // 防重复检查
    if (CONFIG.notify && !acquireLock()) {
      return;
    }
    
    const hour = new Date().getHours();
    if (CONFIG.notify && !CONFIG.force && (hour < CONFIG.startHour || hour > CONFIG.endHour)) {
      console.log(`⏰ 不在推送时段 (${CONFIG.startHour}:00-${CONFIG.endHour}:00)，跳过`);
      return;
    }
    
    if (CONFIG.force) {
      console.log('⚡ 强制推送模式，跳过时间检查');
    }
    
    console.log('🔍 获取 Binance 数据...');
    const data = await getMarketData();
    
    console.log('📊 生成详细分析卡片...');
    const card = generateCard(data);
    console.log(card);
    
    if (CONFIG.notify) {
      await sendNotifyInParts(card);
      console.log('\n✅ 推送成功');
    }
    
  } catch (error) {
    console.error('❌ 错误:', error.message);
    process.exit(1);
  } finally {
    // 释放锁
    if (CONFIG.notify) {
      releaseLock();
    }
  }
}

main();
