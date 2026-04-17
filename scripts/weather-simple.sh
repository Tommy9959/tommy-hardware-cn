#!/bin/bash
# 天气预报脚本 - 温州永嘉人性化详细版
# 每天推送温馨详细的天气预报到微信

# 设置 PATH，确保 cron 能找到 node 和 openclaw
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"

LOG_FILE="/Users/zhuxiaolei/.openclaw/workspace/logs/weather.log"
CITY="yongjia"
LOCATION="温州永嘉"
# 微信推送配置
WECHAT_USER="o9cq80-VOQWTsN3h5bn6gyR2IdY4@im.wechat"
ACCOUNT_ID="ec25a54ce939-im-bot"
# iMessage 配置（保留备用）
IMSG_TO="+8618358008400"

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

# 使用 jq 解析当前天气
CURRENT_TEMP=$(echo "$WEATHER_DATA" | jq -r '.current_condition[0].temp_C')
CURRENT_FEELS=$(echo "$WEATHER_DATA" | jq -r '.current_condition[0].FeelsLikeC')
CURRENT_DESC=$(echo "$WEATHER_DATA" | jq -r '.current_condition[0].weatherDesc[0].value')
CURRENT_HUMIDITY=$(echo "$WEATHER_DATA" | jq -r '.current_condition[0].humidity')
CURRENT_WIND_KMPH=$(echo "$WEATHER_DATA" | jq -r '.current_condition[0].windspeedKmph')
CURRENT_WIND_DIR=$(echo "$WEATHER_DATA" | jq -r '.current_condition[0].winddir16Point')
CURRENT_PRESSURE=$(echo "$WEATHER_DATA" | jq -r '.current_condition[0].pressure')
CURRENT_VISIBILITY=$(echo "$WEATHER_DATA" | jq -r '.current_condition[0].visibility')
CURRENT_UV=$(echo "$WEATHER_DATA" | jq -r '.current_condition[0].uvIndex')
CURRENT_CLOUD=$(echo "$WEATHER_DATA" | jq -r '.current_condition[0].cloudcover')

# 使用 jq 解析今天预报（按小时）
DAY1_MAX=$(echo "$WEATHER_DATA" | jq -r '.weather[0].maxtempC')
DAY1_MIN=$(echo "$WEATHER_DATA" | jq -r '.weather[0].mintempC')
DAY1_DESC=$(echo "$WEATHER_DATA" | jq -r '.weather[0].hourly[6].weatherDesc[0].value')
DAY1_HUMIDITY=$(echo "$WEATHER_DATA" | jq -r '.weather[0].avghumidity')
DAY1_RAIN_CHANCE=$(echo "$WEATHER_DATA" | jq -r '.weather[0].hourly[6].chanceofrain')
DAY1_SUNRISE=$(echo "$WEATHER_DATA" | jq -r '.weather[0].astronomy[0].sunrise')
DAY1_SUNSET=$(echo "$WEATHER_DATA" | jq -r '.weather[0].astronomy[0].sunset')
DAY1_MOONRISE=$(echo "$WEATHER_DATA" | jq -r '.weather[0].astronomy[0].moonrise')
DAY1_MOONSET=$(echo "$WEATHER_DATA" | jq -r '.weather[0].astronomy[0].moonset')
DAY1_MOON_PHASE=$(echo "$WEATHER_DATA" | jq -r '.weather[0].astronomy[0].moon_phase')
DAY1_UV=$(echo "$WEATHER_DATA" | jq -r '.weather[0].uvIndex')

# 使用 jq 解析明天预报
DAY2_MAX=$(echo "$WEATHER_DATA" | jq -r '.weather[1].maxtempC')
DAY2_MIN=$(echo "$WEATHER_DATA" | jq -r '.weather[1].mintempC')
DAY2_DESC=$(echo "$WEATHER_DATA" | jq -r '.weather[1].hourly[6].weatherDesc[0].value')
DAY2_HUMIDITY=$(echo "$WEATHER_DATA" | jq -r '.weather[1].avghumidity')
DAY2_RAIN_CHANCE=$(echo "$WEATHER_DATA" | jq -r '.weather[1].hourly[6].chanceofrain')
DAY2_SUNRISE=$(echo "$WEATHER_DATA" | jq -r '.weather[1].astronomy[0].sunrise')
DAY2_SUNSET=$(echo "$WEATHER_DATA" | jq -r '.weather[1].astronomy[0].sunset')

# 使用 jq 解析后天预报
DAY3_MAX=$(echo "$WEATHER_DATA" | jq -r '.weather[2].maxtempC')
DAY3_MIN=$(echo "$WEATHER_DATA" | jq -r '.weather[2].mintempC')
DAY3_DESC=$(echo "$WEATHER_DATA" | jq -r '.weather[2].hourly[6].weatherDesc[0].value')
DAY3_HUMIDITY=$(echo "$WEATHER_DATA" | jq -r '.weather[2].avghumidity')
DAY3_RAIN_CHANCE=$(echo "$WEATHER_DATA" | jq -r '.weather[2].hourly[6].chanceofrain')

# 获取日期和星期
TODAY=$(date '+%m 月 %d 日')
TODAY_WEEKDAY=$(date '+%A')
TOMORROW=$(date -v+1d '+%m 月 %d 日')
TOMORROW_WEEKDAY=$(date -v+1d '+%A')
DAY_AFTER=$(date -v+2d '+%m 月 %d 日')
DAY_AFTER_WEEKDAY=$(date -v+2d '+%A')

# 人性化天气建议
get_clothing_advice() {
    local temp=$1
    if [ "$temp" -lt 10 ]; then
        echo "❄️ 天气较冷，建议穿厚外套或羽绒服，注意保暖"
    elif [ "$temp" -lt 18 ]; then
        echo "🍂 天气凉爽，建议穿长袖衬衫或薄外套"
    elif [ "$temp" -lt 25 ]; then
        echo "🌤️ 天气舒适，建议穿长袖或短袖 T 恤"
    elif [ "$temp" -lt 30 ]; then
        echo "☀️ 天气较热，建议穿短袖短裤，注意防暑"
    else
        echo "🔥 天气炎热，建议穿透气衣物，避免中暑"
    fi
}

get_rain_advice() {
    local rain=$1
    if [ "$rain" -gt 70 ]; then
        echo "☔ 降雨概率很高，出门务必带伞，注意防范"
    elif [ "$rain" -gt 40 ]; then
        echo "🌂 有降雨可能，建议携带雨具备用"
    elif [ "$rain" -gt 20 ]; then
        echo "⛅ 可能有小雨，可以带把折叠伞"
    else
        echo "🌈 降雨概率较低，天气较好"
    fi
}

get_uv_advice() {
    local uv=$1
    if [ "$uv" -ge 8 ]; then
        echo "⚠️ 紫外线很强，务必涂抹防晒霜，戴帽子和太阳镜"
    elif [ "$uv" -ge 6 ]; then
        echo "☀️ 紫外线较强，外出注意防晒"
    elif [ "$uv" -ge 3 ]; then
        echo "🌤️ 紫外线中等，适当防晒即可"
    else
        echo "🌙 紫外线较弱，无需特别防晒"
    fi
}

get_wind_advice() {
    local wind=$1
    if [ "$wind" -gt 30 ]; then
        echo "💨 风力较大，注意防风，避免高空作业"
    elif [ "$wind" -gt 20 ]; then
        echo "🍃 风力适中，适合放风筝"
    else
        echo "🌬️ 微风徐徐，天气宜人"
    fi
}

get_moon_phase_emoji() {
    local phase=$1
    case "$phase" in
        *"New Moon"*) echo "🌑" ;;
        *"Waxing Crescent"*) echo "🌒" ;;
        *"First Quarter"*) echo "🌓" ;;
        *"Waxing Gibbous"*) echo "🌔" ;;
        *"Full Moon"*) echo "🌕" ;;
        *"Waning Gibbous"*) echo "🌖" ;;
        *"Last Quarter"*) echo "🌗" ;;
        *"Waning Crescent"*) echo "🌘" ;;
        *) echo "🌙" ;;
    esac
}

# 生成人性化建议
CLOTHING_ADVICE=$(get_clothing_advice $DAY1_MAX)
RAIN_ADVICE=$(get_rain_advice $DAY1_RAIN_CHANCE)
UV_ADVICE=$(get_uv_advice $DAY1_UV)
WIND_ADVICE=$(get_wind_advice $CURRENT_WIND_KMPH)
MOON_EMOJI=$(get_moon_phase_emoji "$DAY1_MOON_PHASE")

# 构建温馨详细的消息
MESSAGE="🌤️ ${LOCATION}天气预报

━━━━━━━━━━━━━━━━━━━━
📍 当前实况 · ${TODAY_WEEKDAY}
━━━━━━━━━━━━━━━━━━━━
🌡️ 温度：${CURRENT_TEMP}°C（体感 ${CURRENT_FEELS}°C）
🌦️ 天气：${CURRENT_DESC}
💧 湿度：${CURRENT_HUMIDITY}%
💨 风向：${CURRENT_WIND_DIR} ${CURRENT_WIND_KMPH}km/h
🌫️ 能见度：${CURRENT_VISIBILITY}km
🎯 气压：${CURRENT_PRESSURE}hPa
☁️ 云量：${CURRENT_CLOUD}%
☀️ 紫外线：${CURRENT_UV}

━━━━━━━━━━━━━━━━━━━━
📅 今天 · ${TODAY} ${TODAY_WEEKDAY}
━━━━━━━━━━━━━━━━━━━━
🔺 最高温：${DAY1_MAX}°C  🔻 最低温：${DAY1_MIN}°C
🌦️ 天气：${DAY1_DESC}
🌧️ 降雨概率：${DAY1_RAIN_CHANCE}%
💧 平均湿度：${DAY1_HUMIDITY}%
🌅 日出：${DAY1_SUNRISE}  🌇 日落：${DAY1_SUNSET}
${MOON_EMOJI} 月相：${DAY1_MOON_PHASE}
🌙 月出：${DAY1_MOONRISE}  🌙 月落：${DAY1_MOONSET}
☀️ 紫外线指数：${DAY1_UV}

━━━━━━━━━━━━━━━━━━━━
📅 明天 · ${TOMORROW} ${TOMORROW_WEEKDAY}
━━━━━━━━━━━━━━━━━━━━
🔺 最高温：${DAY2_MAX}°C  🔻 最低温：${DAY2_MIN}°C
🌦️ 天气：${DAY2_DESC}
🌧️ 降雨概率：${DAY2_RAIN_CHANCE}%
💧 平均湿度：${DAY2_HUMIDITY}%
🌅 日出：${DAY2_SUNRISE}  🌇 日落：${DAY2_SUNSET}

━━━━━━━━━━━━━━━━━━━━
📅 后天 · ${DAY_AFTER} ${DAY_AFTER_WEEKDAY}
━━━━━━━━━━━━━━━━━━━━
🔺 最高温：${DAY3_MAX}°C  🔻 最低温：${DAY3_MIN}°C
🌦️ 天气：${DAY3_DESC}
🌧️ 降雨概率：${DAY3_RAIN_CHANCE}%
💧 平均湿度：${DAY3_HUMIDITY}%

━━━━━━━━━━━━━━━━━━━━
💡 生活指数建议
━━━━━━━━━━━━━━━━━━━━
👔 穿衣建议：${CLOTHING_ADVICE}
☔ 防雨建议：${RAIN_ADVICE}
🧴 防晒建议：${UV_ADVICE}
💨 防风建议：${WIND_ADVICE}

━━━━━━━━━━━━━━━━━━━━
🌸 黛玉的温馨小贴士
━━━━━━━━━━━━━━━━━━━━
• 早晚温差较大，注意适时增减衣物
• 保持室内通风，空气清新
• 多喝水，保持身体水分充足
• 雨天路滑，出行注意安全
• 保持好心情，迎接美好的一天！

祝晓雷哥哥今天工作顺利，心情愉快！🌸
黛玉一直陪着你～ 💕"

log "天气数据获取成功"

# 通过微信发送（OpenClaw）
/opt/homebrew/bin/openclaw message send -t "$WECHAT_USER" --channel openclaw-weixin --account "$ACCOUNT_ID" -m "$MESSAGE" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log "天气推送成功 (微信)"
else
    log "天气推送失败"
fi

log "脚本执行完成"
