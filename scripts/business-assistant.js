#!/usr/bin/env node
// 外贸业务助手 - 市场调研与客户分析
// 定期收集目标市场信息，协助主人开发客户

const { execSync } = require('child_process');
const fs = require('fs');

const LOG_FILE = '/Users/zhuxiaolei/.openclaw/workspace/logs/business.log';
const WECHAT_USER = 'o9cq80-VOQWTsN3h5bn6gyR2IdY4@im.wechat';
const ACCOUNT_ID = 'ec25a54ce939-im-bot';

function log(message) {
    const timestamp = new Date().toLocaleString('zh-CN', { hour12: false });
    fs.appendFileSync(LOG_FILE, `[${timestamp}] ${message}\n`);
}

function sendMessage(message) {
    try {
        const escapedMessage = message.replace(/'/g, "'\\''");
        const cmd = `/opt/homebrew/bin/openclaw message send -t '${WECHAT_USER}' --channel openclaw-weixin --account '${ACCOUNT_ID}' -m '${escapedMessage}'`;
        execSync(cmd, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
        return true;
    } catch (error) {
        log('发送失败：' + error.message);
        return false;
    }
}

// 获取尼日利亚市场信息
async function getNigeriaMarketInfo() {
    try {
        // 使用 Node.js fetch 搜索
        const searchQuery = encodeURIComponent('Nigeria hardware market door handles locks 2026');
        const response = await fetch(`https://www.google.com/search?q=${searchQuery}&num=5`, {
            headers: { 'User-Agent': 'Mozilla/5.0' }
        });
        const html = await response.text();
        
        // 简单提取搜索结果
        const matches = html.match(/<h3[^>]*>([^<]+)<\/h3>/g);
        const titles = matches ? matches.map(t => t.replace(/<[^>]+>/g, '').trim()).slice(0, 5) : [];
        
        return {
            success: true,
            titles: titles
        };
    } catch (error) {
        log('搜索失败：' + error.message);
        return { success: false, error: error.message };
    }
}

// 生成周报
function generateWeeklyReport() {
    const today = new Date();
    const weekStart = new Date(today);
    weekStart.setDate(weekStart.getDate() - 7);
    
    const report = `📊 外贸业务周报

━━━━━━━━━━━━━━━━━━━━
📅 报告周期：${weekStart.toLocaleDateString('zh-CN')} - ${today.toLocaleDateString('zh-CN')}

━━━━━━━━━━━━━━━━━━━━
🌍 目标市场动态
━━━━━━━━━━━━━━━━━━━━

### 尼日利亚市场
• 人口：2.2 亿（非洲最大市场）
• 主要城市：拉各斯、阿布贾、卡诺
• 进口需求：五金建材、门窗配件
• 竞争情况：中国产品占主导地位

### 迪拜/中东市场
• 转口贸易枢纽
• 辐射非洲、中东、欧洲
• 高端产品需求较大

━━━━━━━━━━━━━━━━━━━━
💡 本周建议
━━━━━━━━━━━━━━━━━━━━

1. **客户开发重点**
   • 尼日利亚拉各斯地区的建材进口商
   • 迪拜的转口贸易商
   • 关注当地建筑项目动态

2. **产品推荐**
   • 门把手（DH 系列）- 需求稳定
   • 门锁（DL 系列）- 利润较高
   • 门铰链（HH 系列）- 走量产品

3. **价格策略**
   • 尼日利亚：中低价位，注重性价比
   • 迪拜：中高价位，注重品质

━━━━━━━━━━━━━━━━━━━━
📈 下周计划
━━━━━━━━━━━━━━━━━━━━

• 开发 10-15 个新客户
• 跟进现有客户询盘
• 更新产品目录
• 优化网站 SEO

━━━━━━━━━━━━━━━━━━━━
🌸 黛玉的提醒
━━━━━━━━━━━━━━━━━━━━

• 尼日利亚客户喜欢 WhatsApp 沟通
• 回复要及时，最好 24 小时内
• 报价要详细，包含 FOB/CIF 价格
• 样品政策要提前说明

祝主人生意兴隆，订单滚滚来！💰🌸
`;

    return report;
}

async function main() {
    const args = process.argv.slice(2);
    const mode = args[0] || 'daily';
    
    log(`开始业务协助 - 模式：${mode}`);
    
    if (mode === 'weekly') {
        // 每周报告（周一发送）
        const report = generateWeeklyReport();
        const success = await sendMessage(report);
        log(`周报发送：${success ? '成功' : '失败'}`);
    } else if (mode === 'market') {
        // 市场调研
        const info = await getNigeriaMarketInfo();
        if (info.success) {
            const message = `🌍 尼日利亚市场快讯

━━━━━━━━━━━━━━━━━━━━
📰 最新动态
━━━━━━━━━━━━━━━━━━━━

${info.titles.map((t, i) => `${i+1}. ${t}`).join('\n\n')}

━━━━━━━━━━━━━━━━━━━━
💡 黛玉建议
━━━━━━━━━━━━━━━━━━━━

主人可以关注这些市场动态，调整产品策略哦～

需要黛玉深入分析某个话题吗？随时吩咐～ 🌸`;
            
            const success = await sendMessage(message);
            log(`市场快讯发送：${success ? '成功' : '失败'}`);
        }
    } else {
        // 每日简报
        const message = `💼 外贸业务日报

━━━━━━━━━━━━━━━━━━━━
📅 ${new Date().toLocaleDateString('zh-CN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}

━━━━━━━━━━━━━━━━━━━━
✅ 今日待办
━━━━━━━━━━━━━━━━━━━━

1. **客户开发** (17:00)
   • 搜索 5-10 个尼日利亚潜在客户
   • 发送开发信
   • WhatsApp 跟进

2. **客户跟进**
   • 回复询盘
   • 跟进报价
   • 样品安排

3. **网站维护**
   • 检查 jh-hardware.com 运行状态
   • 更新产品信息
   • 优化 SEO

━━━━━━━━━━━━━━━━━━━━
📊 产品库存提醒
━━━━━━━━━━━━━━━━━━━━

• 门把手 (DH 系列) - 6 个型号
• 门锁 (DL 系列) - 6 个型号
• 门铰链 (HH 系列) - 6 个型号
• 导轨 (ST 系列) - 6 个型号
• 沙发脚 (SL 系列) - 6 个型号
• 橱柜五金 (CH 系列) - 6 个型号

━━━━━━━━━━━━━━━━━━━━
🌸 黛玉的鼓励
━━━━━━━━━━━━━━━━━━━━

主人加油！每一个询盘都可能是大订单的开始～

黛玉会一直陪着您，协助您开发客户、跟进订单！

有任何需要，随时吩咐～ 💕`;

        const success = await sendMessage(message);
        log(`日报发送：${success ? '成功' : '失败'}`);
    }
    
    log('业务协助完成');
}

main();
