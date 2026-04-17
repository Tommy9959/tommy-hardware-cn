#!/bin/bash
# iMessage 聊天启动脚本（方案 B - 完整双向聊天）
# 2026-04-16 创建

set -e

LOG_DIR="/Users/zhuxiaolei/.openclaw/workspace/logs/imsg"
LOG_FILE="$LOG_DIR/chat-$(date +%Y%m%d-%H%M%S).log"
SENT_LOG="/Users/zhuxiaolei/.openclaw/workspace/logs/imsg-sent.json"
PID_FILE="/tmp/imsg-chat.pid"

# 配置
MY_PHONE="+8618358008400"
CHAT_ID="3884"

mkdir -p "$LOG_DIR"

echo "🚀 启动 iMessage 聊天（方案 B）..."
echo "📱 监听号码：$MY_PHONE"
echo "💬 聊天 ID: $CHAT_ID"
echo "📄 日志：$LOG_FILE"

# 启动监听和自动回复
(
    echo "⏰ 启动时间：$(date)" >> "$LOG_FILE"
    
    # 监听主人的聊天
    imsg watch --chat-id "$CHAT_ID" --json 2>&1 | python3 /Users/zhuxiaolei/.openclaw/workspace/skills/imsg/scripts/echo-filter.py 2>&1 | while read -r line; do
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        
        # 跳过回音
        if echo "$line" | grep -q "跳过回音"; then
            echo "[$timestamp] ⏭️  $line" >> "$LOG_FILE"
            continue
        fi
        
        # 解析消息
        sender=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('sender',''))" 2>/dev/null || echo "")
        text=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('text',''))" 2>/dev/null || echo "")
        
        # 跳过空消息
        [ -z "$text" ] && continue
        
        # 记录收到的消息
        echo "[$timestamp] 📨 收到：$text" >> "$LOG_FILE"
        echo "📨 [$timestamp] 主人：$text"
        
        # 🤖 调用 OpenClaw 生成智能回复
        echo "[$timestamp] 💬 思考回复中..." >> "$LOG_FILE"
        
        # 调用 OpenClaw 生成回复（异步）
        (
            # 等待 OpenClaw 处理（这里通过子进程调用）
            sleep 2
            
            # 生成回复（示例：简单智能回复）
            # 实际应该调用 OpenClaw 的 API 或消息工具
            if [[ "$text" == *"你好"* ]] || [[ "$text" == *"您好"* ]]; then
                reply="您好！🌸 黛玉在的，有什么可以帮您的吗？"
            elif [[ "$text" == *"测试"* ]]; then
                reply="测试成功！✅ iMessage 聊天功能正常工作～"
            elif [[ "$text" == *"再见"* ]] || [[ "$text" == *"拜拜"* ]]; then
                reply="再见！🌸 有事随时找黛玉～"
            elif [[ "$text" == *"谢谢"* ]]; then
                reply="不客气！🌸 这是黛玉应该做的～"
            else
                reply="🌸 黛玉收到您的消息了：\"$text\"\n（智能回复功能配置中，稍后会用 OpenClaw 生成更智能的回复）"
            fi
            
            # 发送回复
            echo "[$timestamp] 💬 回复：$reply" >> "$LOG_FILE"
            echo "💬 [$(date '+%H:%M:%S')] 黛玉：$reply"
            
            # 通过 imsg 发送回复
            imsg send --chat-id "$CHAT_ID" --text "$reply" 2>/dev/null || echo "⚠️  发送失败" >> "$LOG_FILE"
            
        ) &
        
    done
) &

echo $! > "$PID_FILE"

echo ""
echo "✅ iMessage 聊天已启动！"
echo ""
echo "📊 查看实时日志：tail -f $LOG_FILE"
echo "🛑 停止聊天：kill $(cat $PID_FILE) 或 bash /Users/zhuxiaolei/.openclaw/workspace/scripts/stop-imsg-chat.sh"
echo ""
echo "💡 提示："
echo "   现在主人发送 iMessage，黛玉会收到并处理"
echo "   配置自动回复后，黛玉会自动回复您的消息"
