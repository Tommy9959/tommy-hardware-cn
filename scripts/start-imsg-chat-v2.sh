#!/bin/bash
# iMessage 聊天 v2（改进版 - 稳定监听）
# 2026-04-16 创建

LOG_DIR="/Users/zhuxiaolei/.openclaw/workspace/logs/imsg"
LOG_FILE="$LOG_DIR/chat-v2-$(date +%Y%m%d-%H%M%S).log"
PID_FILE="/tmp/imsg-chat-v2.pid"

# 配置
CHAT_ID="3884"

mkdir -p "$LOG_DIR"

echo "🚀 启动 iMessage 聊天 v2（稳定版）..."
echo "💬 聊天 ID: $CHAT_ID"
echo "📄 日志：$LOG_FILE"
echo ""

# 后台运行
(
    echo "⏰ 启动时间：$(date)" >> "$LOG_FILE"
    
    while true; do
        # 监听消息（每次只处理一条，避免阻塞）
        imsg watch --chat-id "$CHAT_ID" --json --limit 1 2>&1 | while read -r line; do
            timestamp=$(date '+%Y-%m-%d %H:%M:%S')
            
            # 解析消息
            sender=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('sender',''))" 2>/dev/null || echo "")
            text=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('text',''))" 2>/dev/null || echo "")
            
            # 跳过空消息
            [ -z "$text" ] && continue
            
            # 记录收到的消息
            echo "[$timestamp] 📨 收到：$text" >> "$LOG_FILE"
            echo "📨 [$timestamp] 主人：$text"
            
            # 🤖 生成智能回复
            echo "[$timestamp] 💬 思考回复中..." >> "$LOG_FILE"
            
            # 简单智能回复逻辑
            if [[ "$text" == *"你好"* ]] || [[ "$text" == *"您好"* ]]; then
                reply="您好！🌸 黛玉在的，有什么可以帮您的吗？"
            elif [[ "$text" == *"测试"* ]]; then
                reply="测试成功！✅ iMessage 聊天功能正常工作～"
            elif [[ "$text" == *"再见"* ]] || [[ "$text" == *"拜拜"* ]]; then
                reply="再见！🌸 有事随时找黛玉～"
            elif [[ "$text" == *"谢谢"* ]]; then
                reply="不客气！🌸 这是黛玉应该做的～"
            else
                reply="🌸 黛玉收到您的消息了：\"$text\"\n（智能回复持续优化中～）"
            fi
            
            # 发送回复
            echo "[$timestamp] 💬 回复：$reply" >> "$LOG_FILE"
            echo "💬 黛玉：$reply"
            
            # 通过 imsg 发送
            imsg send --chat-id "$CHAT_ID" --text "$reply" 2>> "$LOG_FILE"
            
            # 等待 2 秒，避免频率过快
            sleep 2
        done
        
        # 如果 watch 退出，等待 5 秒后重启
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  监听中断，5 秒后重启..." >> "$LOG_FILE"
        sleep 5
    done
) &

echo $! > "$PID_FILE"

echo "✅ iMessage 聊天 v2 已启动！"
echo "📊 日志：tail -f $LOG_FILE"
echo "🛑 停止：kill $(cat $PID_FILE)"
echo ""
echo "💡 现在请用 iPhone 发送 iMessage 测试！"
