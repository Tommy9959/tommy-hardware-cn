#!/usr/bin/env node
// 天气预报脚本 - 温州永嘉人性化详细版
// 每天推送温馨详细的天气预报到微信

const { execSync } = require('child_process');
const path = require('path');

const LOG_FILE = '/Users/zhuxiaolei/.openclaw/workspace/logs/weather.log';
const WECHAT_USER = 'o9cq80-VOQWTsN3h5bn6gyR2IdY4@im.wechat';
const ACCOUNT_ID = 'ec25a54ce939-im-bot';

function log(message) {
    const timestamp = new Date().toLocaleString('zh-CN', { hour12: false });
    const logLine = `[${timestamp}] ${message}\n`;
    execSync(`echo "${logLine.trim()}" >> "${LOG_FILE}"`, { stdio: 'pipe' });
}

function getWeatherEmoji(code) {
    const map = {
        'Sunny': '☀️', 'Clear': '🌙', 'Partly cloudy': '⛅', 'Cloudy': '☁️',
        'Overcast': '☁️', 'Mist': '🌫️', 'Fog': '🌫️', 'Patchy rain nearby': '🌦️',
        'Patchy rain possible': '🌦️', 'Moderate rain': '🌧️', 'Heavy rain': '🌧️',
        'Thundery outbreaks possible': '⛈️', 'Thundery outbreaks in nearby': '⛈️'
    };
    return map[code] || '🌤️';
}

function getMoonPhaseEmoji(phase) {
    if (phase.includes('New')) return '🌑';
    if (phase.includes('Crescent') && phase.includes('Waxing')) return '🌒';
    if (phase.includes('First')) return '🌓';
    if (phase.includes('Gibbous') && phase.includes('Waxing')) return '🌔';
    if (phase.includes('Full')) return '🌕';
    if (phase.includes('Gibbous') && phase.includes('Waning')) return '🌖';
    if (phase.includes('Last')) return '🌗';
    if (phase.includes('Crescent') && phase.includes('Waning')) return '🌘';
    return '🌙';
}

function getChineseWeekday(day) {
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    return days[day];
}

function getClothingAdvice(temp) {
    if (temp < 10) return '❄️ 天气较冷，建议穿厚外套或羽绒服，注意保暖';
    if (temp < 18) return '🍂 天气凉爽，建议穿长袖衬衫或薄外套';
    if (temp < 25) return '🌤️ 天气舒适，建议穿长袖或短袖 T 恤';
    if (temp < 30) return '☀️ 天气较热，建议穿短袖短裤，注意防暑';
    return '🔥 天气炎热，建议穿透气衣物，避免中暑';
}

function getRainAdvice(rain) {
    if (rain > 70) return '☔ 降雨概率很高，出门务必带伞，注意防范';
    if (rain > 40) return '🌂 有降雨可能，建议携带雨具备用';
    if (rain > 20) return '⛅ 可能有小雨，可以带把折叠伞';
    return '🌈 降雨概率较低，天气较好';
}

function getUVAdvice(uv) {
    if (uv >= 8) return '⚠️ 紫外线很强，务必涂抹防晒霜，戴帽子和太阳镜';
    if (uv >= 6) return '☀️ 紫外线较强，外出注意防晒';
    if (uv >= 3) return '🌤️ 紫外线中等，适当防晒即可';
    return '🌙 紫外线较弱，无需特别防晒';
}

async function main() {
    log('开始获取天气预报...');
    
    try {
        const response = await fetch('https://wttr.in/Wenzhou?format=j1');
        const data = await response.json();
        
        log('天气数据获取成功');
        
        const current = data.current_condition[0];
        const day1 = data.weather[0];
        const day2 = data.weather[1];
        const day3 = data.weather[2];
        
        const now = new Date();
        const today = (now.getMonth() + 1).toString().padStart(2, '0') + '/' + now.getDate().toString().padStart(2, '0');
        const todayWeekday = getChineseWeekday(now.getDay());
        
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const tomorrowStr = (tomorrow.getMonth() + 1).toString().padStart(2, '0') + '/' + tomorrow.getDate().toString().padStart(2, '0');
        const tomorrowWeekday = getChineseWeekday(tomorrow.getDay());
        
        const dayAfter = new Date(now);
        dayAfter.setDate(dayAfter.getDate() + 2);
        const dayAfterStr = (dayAfter.getMonth() + 1).toString().padStart(2, '0') + '/' + dayAfter.getDate().toString().padStart(2, '0');
        const dayAfterWeekday = getChineseWeekday(dayAfter.getDay());
        
        const clothingAdvice = getClothingAdvice(parseInt(day1.maxtempC));
        const rainAdvice = getRainAdvice(parseInt(day1.hourly[6].chanceofrain || 0));
        const uvAdvice = getUVAdvice(parseInt(day1.uvIndex));
        const weatherEmoji = getWeatherEmoji(day1.hourly[6].weatherDesc[0].value);
        const moonEmoji = getMoonPhaseEmoji(day1.astronomy[0].moon_phase);
        
        const message = `🌤️ 温州永嘉天气预报

━━━━━━━━━━━━━━━━━━━━
📍 当前实况 · ${todayWeekday}
━━━━━━━━━━━━━━━━━━━━
🌡️ 温度：${current.temp_C}°C（体感 ${current.FeelsLikeC}°C）
${getWeatherEmoji(current.weatherDesc[0].value)} 天气：${current.weatherDesc[0].value === 'Partly cloudy' ? '多云' : current.weatherDesc[0].value === 'Sunny' ? '晴朗' : current.weatherDesc[0].value === 'Clear' ? '晴朗' : current.weatherDesc[0].value === 'Cloudy' ? '阴天' : current.weatherDesc[0].value === 'Mist' ? '薄雾' : current.weatherDesc[0].value}
💧 湿度：${current.humidity}%
💨 风向：${current.winddir16Point} ${current.windspeedKmph}km/h
🌫️ 能见度：${current.visibility}km
🎯 气压：${current.pressure}hPa
☁️ 云量：${current.cloudcover}%
☀️ 紫外线：${current.uvIndex}

━━━━━━━━━━━━━━━━━━━━
📅 今天 · ${today} ${todayWeekday}
━━━━━━━━━━━━━━━━━━━━
🔺 最高温：${day1.maxtempC}°C  🔻 最低温：${day1.mintempC}°C
${weatherEmoji} 天气：${day1.hourly[6].weatherDesc[0].value === 'Sunny' ? '晴朗' : day1.hourly[6].weatherDesc[0].value === 'Partly cloudy' ? '多云' : day1.hourly[6].weatherDesc[0].value === 'Patchy rain nearby' ? '局部有雨' : day1.hourly[6].weatherDesc[0].value}
🌧️ 降雨概率：${day1.hourly[6].chanceofrain || 0}%
💧 平均湿度：${day1.avghumidity}%
🌅 日出：${day1.astronomy[0].sunrise}  🌇 日落：${day1.astronomy[0].sunset}
${moonEmoji} 月相：${day1.astronomy[0].moon_phase}
🌙 月出：${day1.astronomy[0].moonrise}  🌙 月落：${day1.astronomy[0].moonset}
☀️ 紫外线指数：${day1.uvIndex}

━━━━━━━━━━━━━━━━━━━━
📅 明天 · ${tomorrowStr} ${tomorrowWeekday}
━━━━━━━━━━━━━━━━━━━━
🔺 最高温：${day2.maxtempC}°C  🔻 最低温：${day2.mintempC}°C
${getWeatherEmoji(day2.hourly[6].weatherDesc[0].value)} 天气：${day2.hourly[6].weatherDesc[0].value === 'Sunny' ? '晴朗' : day2.hourly[6].weatherDesc[0].value === 'Partly cloudy' ? '多云' : day2.hourly[6].weatherDesc[0].value === 'Patchy rain nearby' ? '局部有雨' : day2.hourly[6].weatherDesc[0].value}
🌧️ 降雨概率：${day2.hourly[6].chanceofrain || 0}%
💧 平均湿度：${day2.avghumidity}%
🌅 日出：${day2.astronomy[0].sunrise}  🌇 日落：${day2.astronomy[0].sunset}

━━━━━━━━━━━━━━━━━━━━
📅 后天 · ${dayAfterStr} ${dayAfterWeekday}
━━━━━━━━━━━━━━━━━━━━
🔺 最高温：${day3.maxtempC}°C  🔻 最低温：${day3.mintempC}°C
${getWeatherEmoji(day3.hourly[6].weatherDesc[0].value)} 天气：${day3.hourly[6].weatherDesc[0].value === 'Sunny' ? '晴朗' : day3.hourly[6].weatherDesc[0].value === 'Partly cloudy' ? '多云' : day3.hourly[6].weatherDesc[0].value === 'Patchy rain nearby' ? '局部有雨' : day3.hourly[6].weatherDesc[0].value}
🌧️ 降雨概率：${day3.hourly[6].chanceofrain || 0}%
💧 平均湿度：${day3.avghumidity}%

━━━━━━━━━━━━━━━━━━━━
💡 生活指数建议
━━━━━━━━━━━━━━━━━━━━
👔 穿衣建议：${clothingAdvice}
☔ 防雨建议：${rainAdvice}
🧴 防晒建议：${uvAdvice}

━━━━━━━━━━━━━━━━━━━━
🌸 黛玉的温馨小贴士
━━━━━━━━━━━━━━━━━━━━
• 早晚温差较大，注意适时增减衣物
• 保持室内通风，空气清新
• 多喝水，保持身体水分充足
• 雨天路滑，出行注意安全
• 保持好心情，迎接美好的一天！

祝晓雷哥哥今天工作顺利，心情愉快！🌸
黛玉一直陪着你～ 💕`;

        // 发送微信
        try {
            execSync(`/opt/homebrew/bin/openclaw message send -t "${WECHAT_USER}" --channel openclaw-weixin --account "${ACCOUNT_ID}" -m "${message.replace(/"/g, '\\"')}"`, { stdio: 'pipe' });
            log('天气推送成功 (微信)');
        } catch (sendError) {
            log('天气推送失败 (微信): ' + sendError.message);
        }
        
        log('脚本执行完成');
        
    } catch (error) {
        log('错误：无法获取天气数据 - ' + error.message);
        process.exit(1);
    }
}

main();
