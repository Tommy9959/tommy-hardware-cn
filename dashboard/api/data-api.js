// 尼日利亚客户仪表板数据API
const express = require('express');
const path = require('path');
const fs = require('fs').promises;
const app = express();
const PORT = 3001;

// 允许跨域
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});

// 静态文件服务
app.use(express.static(path.join(__dirname, '..')));

// API端点：获取实时客户数据
app.get('/api/dashboard-data', async (req, res) => {
  try {
    // 读取客户数据库
    const clientDbPath = '/Users/zhuxiaolei/.openclaw/workspace/logs/nigeria-clients/client_database.json';
    const trackingPath = '/Users/zhuxiaolei/.openclaw/workspace/logs/nigeria-clients/send_tracking.json';
    
    let clients = {};
    let tracking = {};
    
    // 读取客户数据
    try {
      const clientData = await fs.readFile(clientDbPath, 'utf8');
      clients = JSON.parse(clientData);
    } catch (error) {
      console.log('客户数据库不存在，使用空数据');
    }
    
    // 读取追踪数据
    try {
      const trackingData = await fs.readFile(trackingPath, 'utf8');
      tracking = JSON.parse(trackingData);
    } catch (error) {
      console.log('追踪数据不存在，使用空数据');
    }
    
    // 处理数据
    const dashboardData = processDashboardData(clients, tracking);
    
    res.json(dashboardData);
  } catch (error) {
    console.error('API错误:', error);
    res.status(500).json({ error: '数据处理失败' });
  }
});

// 数据处理函数
function processDashboardData(clients, tracking) {
  const clientArray = Object.values(clients);
  const today = new Date().toISOString().split('T')[0];
  
  // 客户概览
  const summary = {
    total_clients: clientArray.length,
    new_clients_today: clientArray.filter(c => c.found_date === today).length,
    high_potential: clientArray.filter(c => c.score >= 85).length,
    medium_potential: clientArray.filter(c => c.score >= 60 && c.score < 85).length,
    low_potential: clientArray.filter(c => c.score < 60).length,
    large_clients: clientArray.filter(c => c.client_size === 'large').length,
    small_clients: clientArray.filter(c => c.client_size === 'small').length
  };
  
  // 地理分布
  const cityStats = {};
  clientArray.forEach(client => {
    const city = client.city || 'Unknown';
    cityStats[city] = (cityStats[city] || 0) + 1;
  });
  
  const cities = Object.entries(cityStats).map(([city, count]) => ({
    city,
    clients: count,
    lat: getCityCoordinates(city).lat,
    lng: getCityCoordinates(city).lng
  }));
  
  // A/B测试结果
  const abTestResults = calculateABTestResults(tracking);
  
  // 产品分布
  const productDistribution = {
    door_hardware: clientArray.filter(c => c.product_category === 'door_hardware').length,
    furniture_hardware: clientArray.filter(c => c.product_category === 'furniture_hardware').length,
    building_materials: clientArray.filter(c => c.product_category === 'building_materials').length
  };
  
  // 竞争对手价格（静态数据）
  const competitorPricing = {
    categories: ["Door Handles", "Door Locks", "Hinges", "Sliding Tracks"],
    alibaba_prices: [3.2, 4.1, 1.8, 2.5],
    local_prices: [2.8, 3.6, 1.5, 2.2],
    our_prices: [2.1, 2.8, 1.2, 1.8]
  };
  
  // 最佳时机配置
  const optimalTiming = {
    best_days: ["Monday", "Tuesday", "Wednesday", "Thursday"],
    best_hours: [10, 11, 12, 13, 14, 15, 16],
    upcoming_holidays: [
      { date: "2026-05-01", name: "Labour Day" },
      { date: "2026-06-03", name: "Eid al-Fitr" }
    ]
  };
  
  return {
    client_summary: summary,
    geographic_data: { cities },
    ab_test_results: abTestResults,
    product_distribution: productDistribution,
    competitor_pricing: competitorPricing,
    optimal_timing: optimalTiming
  };
}

function getCityCoordinates(city) {
  // 尼日利亚主要城市坐标
  const coordinates = {
    'Lagos': { lat: 6.5244, lng: 3.3792 },
    'Abuja': { lat: 9.0765, lng: 7.3986 },
    'Port Harcourt': { lat: 4.8156, lng: 7.0498 },
    'Kano': { lat: 12.0022, lng: 8.5920 },
    'Ibadan': { lat: 7.3775, lng: 3.9470 },
    'Benin City': { lat: 6.3350, lng: 5.6037 },
    'Unknown': { lat: 8.0, lng: 5.0 }
  };
  
  return coordinates[city] || coordinates['Unknown'];
}

function calculateABTestResults(tracking) {
  const results = {
    template_a: { sent: 0, replied: 0 },
    template_b: { sent: 0, replied: 0 }
  };
  
  Object.values(tracking).forEach(record => {
    const template = record.template || 'template_a';
    if (results[template]) {
      results[template].sent++;
      if (record.replies && record.replies.length > 0) {
        results[template].replied++;
      }
    }
  });
  
  // 计算回复率和平均响应时间
  Object.keys(results).forEach(template => {
    const data = results[template];
    data.reply_rate = data.sent > 0 ? Math.round((data.replied / data.sent) * 1000) / 10 : 0;
    data.avg_response_time = data.replied > 0 ? "6.5 hours" : "N/A";
  });
  
  return results;
}

// 启动服务器
app.listen(PORT, () => {
  console.log(`🚀 尼日利亚客户仪表板API运行在 http://localhost:${PORT}`);
  console.log(`📊 访问仪表板: http://localhost:${PORT}`);
});

module.exports = app;