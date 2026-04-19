// 尼日利亚客户仪表板图表库
class NigeriaDashboardCharts {
  constructor() {
    this.data = null;
    this.isLoading = false;
  }

  async loadData() {
    if (this.isLoading) return;
    
    this.isLoading = true;
    try {
      // 实际部署时，这里会从真实API获取数据
      // 现在先使用本地样本数据
      const response = await fetch('data/sample-data.json');
      this.data = await response.json();
      this.isLoading = false;
      return this.data;
    } catch (error) {
      console.error('加载数据失败:', error);
      this.isLoading = false;
      return null;
    }
  }

  createGeographicChart(containerId) {
    const container = document.getElementById(containerId);
    if (!container || !this.data) return;

    // 创建简单的地理分布图表（实际项目中会使用地图API）
    const cities = this.data.geographic_data.cities;
    let html = '<div class="geographic-chart">';
    
    // 按客户数量排序
    const sortedCities = [...cities].sort((a, b) => b.clients - a.clients);
    
    sortedCities.forEach(city => {
      const percentage = Math.round((city.clients / this.data.client_summary.total_clients) * 100);
      html += `
        <div class="city-item">
          <div class="city-info">
            <strong>${city.city}</strong>
            <span>${city.clients} 家客户</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${percentage}%"></div>
          </div>
          <span class="percentage">${percentage}%</span>
        </div>
      `;
    });
    
    html += '</div>';
    container.innerHTML = html;
  }

  createABTestChart(containerId) {
    const container = document.getElementById(containerId);
    if (!container || !this.data) return;

    const results = this.data.ab_test_results;
    let html = '<div class="ab-test-chart">';
    
    Object.keys(results).forEach(template => {
      const data = results[template];
      html += `
        <div class="template-card">
          <h4>${template.toUpperCase()}</h4>
          <div class="stat-row">
            <span>发送:</span>
            <strong>${data.sent}</strong>
          </div>
          <div class="stat-row">
            <span>回复:</span>
            <strong>${data.replied}</strong>
          </div>
          <div class="stat-row">
            <span>回复率:</span>
            <strong class="badge badge-${data.reply_rate > 30 ? 'success' : 'warning'}">
              ${data.reply_rate}%
            </strong>
          </div>
          <div class="stat-row">
            <span>平均响应:</span>
            <strong>${data.avg_response_time}</strong>
          </div>
        </div>
      `;
    });
    
    html += '</div>';
    container.innerHTML = html;
  }

  createProductDistributionChart(containerId) {
    const container = document.getElementById(containerId);
    if (!container || !this.data) return;

    const products = this.data.product_distribution;
    const total = Object.values(products).reduce((sum, val) => sum + val, 0);
    
    let html = '<div class="product-chart">';
    
    Object.entries(products).forEach(([product, count]) => {
      const percentage = Math.round((count / total) * 100);
      const productName = this.getProductName(product);
      
      html += `
        <div class="product-item">
          <div class="product-info">
            <strong>${productName}</strong>
            <span>${count} 个客户</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${percentage}%"></div>
          </div>
          <span class="percentage">${percentage}%</span>
        </div>
      `;
    });
    
    html += '</div>';
    container.innerHTML = html;
  }

  createCompetitorPricingChart(containerId) {
    const container = document.getElementById(containerId);
    if (!container || !this.data) return;

    const pricing = this.data.competitor_pricing;
    let html = '<table class="competitor-table">';
    
    // 表头
    html += '<thead><tr><th>产品类别</th><th>Alibaba</th><th>本地供应商</th><th>我们</th><th>优势</th></tr></thead>';
    
    // 数据行
    html += '<tbody>';
    for (let i = 0; i < pricing.categories.length; i++) {
      const category = pricing.categories[i];
      const alibaba = pricing.alibaba_prices[i];
      const local = pricing.local_prices[i];
      const ours = pricing.our_prices[i];
      const advantage = Math.round(((local - ours) / local) * 100);
      
      html += `
        <tr>
          <td>${category}</td>
          <td>$${alibaba}</td>
          <td>$${local}</td>
          <td class="success">$${ours}</td>
          <td class="success"><strong>${advantage}%</strong> 更低</td>
        </tr>
      `;
    }
    html += '</tbody></table>';
    
    container.innerHTML = html;
  }

  getProductName(key) {
    const names = {
      'door_hardware': '门控五金',
      'furniture_hardware': '家具五金', 
      'building_materials': '建材配件'
    };
    return names[key] || key;
  }

  updateSummaryStats() {
    if (!this.data) return;
    
    const summary = this.data.client_summary;
    document.getElementById('total-clients').textContent = summary.total_clients;
    document.getElementById('new-clients').textContent = summary.new_clients_today;
    document.getElementById('high-potential').textContent = summary.high_potential;
    document.getElementById('large-clients').textContent = summary.large_clients;
  }

  async refreshData() {
    const button = document.querySelector('.refresh-btn');
    button.textContent = '刷新中...';
    button.disabled = true;
    
    await this.loadData();
    this.updateAllCharts();
    
    button.textContent = '刷新数据';
    button.disabled = false;
  }

  updateAllCharts() {
    this.updateSummaryStats();
    this.createGeographicChart('geographic-chart');
    this.createABTestChart('ab-test-chart');
    this.createProductDistributionChart('product-chart');
    this.createCompetitorPricingChart('pricing-chart');
  }

  init() {
    // 加载初始数据
    this.loadData().then(() => {
      this.updateAllCharts();
    });
    
    // 绑定刷新按钮
    const refreshBtn = document.querySelector('.refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.refreshData();
      });
    }
  }
}

// 初始化图表
document.addEventListener('DOMContentLoaded', () => {
  const dashboard = new NigeriaDashboardCharts();
  dashboard.init();
});