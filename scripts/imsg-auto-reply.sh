#!/bin/bash
# iMessage 自动回复脚本（带回音过滤）
# 2026-04-16 创建

set -e

LOG_DIR="/Users/zhuxiaolei/.openclaw/workspace/logs/imsg"
LOG_FILE="$LOG_DIR/auto-reply-$(date +%Y%m%d-%H%M%S).log"
SENT_LOG="/Users/zhuxiaolei/.openclaw/workspace/logs/imsg-sent.json"
PID_FILE="/tmp/imsg-auto-reply.pid"

# 我的号码（发送消息的号码，用于回音过滤）
MY_PHONE="+8618358008400"

# 创建日志目录
mkdir -p "$LOG_DIR"

echo "🚀 启动 iMessage 自动回复..."
echo "📱 我的号码：$MY_PHONE"
echo "📄 日志文件：$LOG_FILE"
echo "💾 发送日志：$SENT_LOG"

# 获取所有聊天 ID
CHAT_IDS=$(imsg chats --limit 50 2>/dev/null | grep -E '^\[' | sed 's/\[\([0-9]*\)\].*/\1/' | tr '\n' ' ')
echo "📋 监听聊天数：$(echo $CHAT_IDS | wc -w) 个"

# 后台运行
(
    echo "⏰ 启动时间：$(date)" >> "$LOG_FILE"
    
    # 监听所有聊天
    for chat_id in $CHAT_IDS; do
        (
            imsg watch --chat-id "$chat_id" --json 2>&1 | python3 /Users/zhuxiaolei/.openclaw/workspace/skills/imsg/scripts/echo-filter.py 2>&1 | while read -r line; do
                timestamp=$(date '+%Y-%m-%d %H:%M:%S')
                
                # 检查是否是有效消息（非回音）
                if echo "$line" | grep -q "跳过回音"; then
                    echo "[$timestamp] [Chat:$chat_id] ⏭️  $line" >> "$LOG_FILE"
                    continue
                fi
                
                # 解析消息
                sender=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('sender',''))" 2>/dev/null || echo "")
                text=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('text',''))" 2>/dev/null || echo "")
                
                # 跳过空消息
                [ -z "$text" ] && continue
                
                # 记录收到的消息
                echo "[$timestamp] [Chat:$chat_id] 📨 收到：来自 $sender - $text" >> "$LOG_FILE"
                
                # 🤖 这里调用 OpenClaw 处理消息并生成回复
                # 示例：调用 OpenClaw 处理
                # reply=$(openclaw process-imsg --sender "$sender" --text "$text" 2>/dev/null)
                
                # 简单测试回复（临时）
                if [ -n "$sender" ] && [ -n "$text" ]; then
                    echo "[$timestamp] [Chat:$chat_id] 💬 准备回复：$text" >> "$LOG_FILE"
                    # 实际使用时，这里调用 OpenClaw 生成回复
                    # imsg send --chat-id "$chat_id" --text "$reply"
                fi
            done
        ) &
    done
    
    wait
) &

echo $! > "$PID_FILE"

echo "✅ iMessage 自动回复已启动！"
echo "📊 查看日志：tail -f $LOG_FILE"
echo "🛑 停止：kill $(cat $PID_FILE)"
