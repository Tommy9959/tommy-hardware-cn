#!/bin/bash
# 天气预报脚本 - 简化版
# 每天推送金华天气预报到微信

LOG_FILE="/Users/zhuxiaolei/.openclaw/workspace/logs/weather.log"
CITY="jinhua"
WECHAT_USER="o9cq80-VOQWTsN3h5bn6gyR2IdY4@im.wechat"
ACCOUNT_ID="ec25a54ce939-im-bot"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "开始获取天气预报..."

# 获取 wttr.in 天气数据
WEATHER_DATA=$(curl -s "https://wttr.in/${CITY}?format=j1" 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$WEATHER_DATA" ]; then
    log "错误：无法获取天气数据"
    exit 1
fi

# 解析天气数据
CURRENT_TEMP=$(echo "$WEATHER_DATA" | grep -o '"temp_C":"[^"]*"' | head -1 | cut -d'"' -f4)
CURRENT_DESC=$(echo "$WEATHER_DATA" | grep -o '"desc_zh":"[^"]*"' | head -1 | cut -d'"' -f4)
CURRENT_HUMIDITY=$(echo "$WEATHER_DATA" | grep -o '"humidity":"[^"]*"' | head -1 | cut -d'"' -f4)
CURRENT_WIND=$(echo "$WEATHER_DATA" | grep -o '"windspeedKmph":"[^"]*"' | head -1 | cut -d'"' -f4)

# 获取未来 3 天预报
DAY1_TEMP_MAX=$(echo "$WEATHER_DATA" | grep -o '"maxtempC":"[^"]*"' | head -1 | cut -d'"' -f4)
DAY1_TEMP_MIN=$(echo "$WEATHER_DATA" | grep -o '"mintempC":"[^"]*"' | head -1 | cut -d'"' -f4)
DAY1_DESC=$(echo "$WEATHER_DATA" | grep -o '"desc_zh":"[^"]*"' | head -2 | tail -1 | cut -d'"' -f4)

# 构建消息
MESSAGE="🌤️ 金华天气预报

📍 当前天气
🌡️ 温度：${CURRENT_TEMP}°C
🌦️ ${CURRENT_DESC}
💧 湿度：${CURRENT_HUMIDITY}%
💨 风速：${CURRENT_WIND} km/h

📅 今天预报
🔺 最高：${DAY1_TEMP_MAX}°C
🔻 最低：${DAY1_TEMP_MIN}°C
🌦️ ${DAY1_DESC}

祝你今天心情愉快！☀️"

log "天气数据获取成功"

# 通过微信发送（OpenClaw）
openclaw message send -t "$WECHAT_USER" --channel openclaw-weixin --account "$ACCOUNT_ID" -m "$MESSAGE" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log "天气推送成功"
else
    log "天气推送失败"
fi

log "脚本执行完成"
