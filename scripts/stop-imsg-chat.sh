#!/bin/bash
# iMessage 聊天停止脚本

PID_FILE="/tmp/imsg-chat.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        rm "$PID_FILE"
        echo "✅ iMessage 聊天已停止 (PID: $PID)"
    else
        rm "$PID_FILE"
        echo "⚠️  进程不存在，已清理 PID 文件"
    fi
else
    echo "⚠️  PID 文件不存在，聊天可能未运行"
    # 尝试查找并终止所有 imsg watch 进程
    pkill -f "imsg watch" && echo "✅ 已停止所有 imsg watch 进程" || echo "ℹ️  未找到 imsg watch 进程"
fi
