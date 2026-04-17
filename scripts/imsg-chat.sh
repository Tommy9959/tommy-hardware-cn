#!/bin/bash
# iMessage 聊天机器人（类似微信）
# 2026-04-16 创建

LOG_DIR="/Users/zhuxiaolei/.openclaw/workspace/logs/imsg"
LOG_FILE="$LOG_DIR/chat-$(date +%Y%m%d-%H%M%S).log"
SENT_LOG="/Users/zhuxiaolei/.openclaw/workspace/logs/imsg-sent.json"

# 配置
MY_PHONE="+8618358008400"  # 主人的号码
CHAT_ID="3884"  # 主人的聊天 ID

mkdir -p "$LOG_DIR"

echo "🚀 启动 iMessage 聊天机器人..."
echo "📱 监听号码：$MY_PHONE"
echo "💬 聊天 ID: $CHAT_ID"
echo "📄 日志：$LOG_FILE"

# 启动监听
imsg watch --chat-id "$CHAT_ID" --json 2>&1 | python3 /Users/zhuxiaolei/.openclaw/workspace/skills/imsg/scripts/echo-filter.py 2>&1 | while read -r line; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 跳过回音
    if echo "$line" | grep -q "跳过回音"; then
        echo "[$timestamp] ⏭️  $line" >> "$LOG_FILE"
        continue
    fi
    
    # 解析消息
    sender=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('sender',''))" 2>/dev/null)
    text=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('text',''))" 2>/dev/null)
    
    [ -z "$text" ] && continue
    
    # 记录收到的消息
    echo "[$timestamp] 📨 收到：$text" >> "$LOG_FILE"
    echo "📨 [$timestamp] 主人：$text"
    
    # 🤖 调用 OpenClaw 处理消息（通过微信发送）
    echo "[$timestamp] 💬 思考回复中..." >> "$LOG_FILE"
    
    # 这里通过微信通知 OpenClaw（临时方案）
    # 正式方案需要直接调用 OpenClaw 的 message 工具
    
done &

echo "✅ iMessage 聊天机器人已启动！"
echo "📊 日志：tail -f $LOG_FILE"
