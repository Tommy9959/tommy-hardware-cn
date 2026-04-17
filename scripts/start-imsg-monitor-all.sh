#!/bin/bash
# iMessage 监听启动脚本（监听所有聊天）
# 2026-04-16 创建

set -e

LOG_DIR="/Users/zhuxiaolei/.openclaw/workspace/logs/imsg"
LOG_FILE="$LOG_DIR/watch-all-$(date +%Y%m%d-%H%M%S).log"
PID_FILE="/tmp/imsg-monitor-all.pid"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 检查依赖
echo "🔍 检查依赖..."
if ! command -v imsg &> /dev/null; then
    echo "❌ imsg 未安装，请先运行：brew install steipete/tap/imsg"
    exit 1
fi

# 检查过滤器脚本
FILTER_SCRIPT="/Users/zhuxiaolei/.openclaw/workspace/skills/imsg/scripts/echo-filter.py"
if [ ! -f "$FILTER_SCRIPT" ]; then
    echo "❌ 回音过滤器不存在：$FILTER_SCRIPT"
    exit 1
fi

# 获取所有聊天 ID
echo "📱 获取所有聊天 ID..."
CHAT_IDS=$(imsg chats --limit 50 2>/dev/null | grep -E '^\[' | sed 's/\[\([0-9]*\)\].*/\1/' | tr '\n' ' ')
echo "📋 监听聊天数：$(echo $CHAT_IDS | wc -w) 个"

# 启动监听
echo "🚀 启动 iMessage 监听（所有聊天）..."
echo "📄 日志文件：$LOG_FILE"
echo "💾 PID 文件：$PID_FILE"

# 后台运行监听
(
    echo "⏰ 启动时间：$(date)"
    echo "📱 监听聊天：$CHAT_IDS"
    
    # 监听所有聊天
    for chat_id in $CHAT_IDS; do
        (
            imsg watch --chat-id "$chat_id" --json 2>&1 | python3 "$FILTER_SCRIPT" 2>&1 | while read -r line; do
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] [Chat:$chat_id] $line" >> "$LOG_FILE"
            done
        ) &
    done
    
    # 等待所有子进程
    wait
) &

# 记录 PID
echo $! > "$PID_FILE"

echo "✅ iMessage 监听已启动（所有聊天）！"
echo "📊 查看日志：tail -f $LOG_FILE"
echo "🛑 停止监听：kill $(cat $PID_FILE) 或 bash /Users/zhuxiaolei/.openclaw/workspace/scripts/stop-imsg-monitor-all.sh"
