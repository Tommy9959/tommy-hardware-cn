#!/bin/bash
# iMessage 监听启动脚本（带回音过滤）
# 2026-04-16 创建

set -e

# 配置
CHAT_ID="${1:-3884}"  # 默认监听主人的聊天（+8618358008400）
LOG_DIR="/Users/zhuxiaolei/.openclaw/workspace/logs/imsg"
LOG_FILE="$LOG_DIR/watch-$(date +%Y%m%d-%H%M%S).log"
PID_FILE="/tmp/imsg-monitor.pid"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 检查依赖
echo "🔍 检查依赖..."
if ! command -v imsg &> /dev/null; then
    echo "❌ imsg 未安装，请先运行：brew install steipete/tap/imsg"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ python3 未安装"
    exit 1
fi

# 检查过滤器脚本
FILTER_SCRIPT="/Users/zhuxiaolei/.openclaw/workspace/skills/imsg/scripts/echo-filter.py"
if [ ! -f "$FILTER_SCRIPT" ]; then
    echo "❌ 回音过滤器不存在：$FILTER_SCRIPT"
    exit 1
fi

# 启动监听
echo "🚀 启动 iMessage 监听..."
echo "📱 监听聊天 ID: $CHAT_ID"
echo "📄 日志文件：$LOG_FILE"
echo "💾 PID 文件：$PID_FILE"

# 后台运行监听
(
    echo "⏰ 启动时间：$(date)"
    imsg watch --chat-id "$CHAT_ID" --json 2>&1 | python3 "$FILTER_SCRIPT" 2>&1 | while read -r line; do
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $line" >> "$LOG_FILE"
        
        # 如果是有效消息（非回音），可以在这里触发 OpenClaw 处理
        # 例如：echo "$line" | openclaw process-imsg-message
    done
) &

# 记录 PID
echo $! > "$PID_FILE"

echo "✅ iMessage 监听已启动！"
echo "📊 查看日志：tail -f $LOG_FILE"
echo "🛑 停止监听：kill $(cat $PID_FILE) 或 bash /Users/zhuxiaolei/.openclaw/workspace/scripts/stop-imsg-monitor.sh"
echo ""
echo "📱 监听配置："
echo "   聊天 ID: $CHAT_ID"
echo "   回音过滤：已启用"
echo "   日志目录：$LOG_DIR"
