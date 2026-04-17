#!/usr/bin/env python3
"""
iMessage 回音过滤器
功能：过滤掉 OpenClaw 自己发送的消息，防止无限循环回复
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# 配置
MY_PHONE = "+8618358008400"  # 主人的手机号
MY_EMAIL = "z946487044@icloud.com"
SENT_LOG_PATH = Path("/Users/zhuxiaolei/.openclaw/workspace/logs/imsg-sent.json")
TTL_SECONDS = 300  # 5 分钟内发送的消息被过滤

def load_sent_messages():
    """加载已发送的消息日志"""
    if not SENT_LOG_PATH.exists():
        return []
    
    try:
        with open(SENT_LOG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 过滤掉过期的记录
            cutoff = time.time() - TTL_SECONDS
            return [msg for msg in data if msg.get('timestamp', 0) > cutoff]
    except:
        return []

def save_sent_message(message_id, text, to):
    """记录已发送的消息"""
    SENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    messages = load_sent_messages()
    messages.append({
        'id': message_id,
        'text': text,
        'to': to,
        'timestamp': time.time()
    })
    
    with open(SENT_LOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def is_echo(sender, text):
    """检查是否是回音消息"""
    # 检查发送者是否是自己
    if sender in [MY_PHONE, MY_EMAIL, 'me', 'self']:
        return True
    
    # 检查是否在已发送消息中
    sent_messages = load_sent_messages()
    for msg in sent_messages:
        if msg.get('text') == text:
            return True
    
    return False

def main():
    """主函数：从 stdin 读取消息，过滤回音后输出"""
    print("🔍 iMessage 回音过滤器已启动", file=sys.stderr)
    print(f"📱 我的号码：{MY_PHONE}", file=sys.stderr)
    print(f"⏰ TTL: {TTL_SECONDS}秒", file=sys.stderr)
    
    for line in sys.stdin:
        try:
            message = json.loads(line.strip())
            sender = message.get('sender', '')
            text = message.get('text', '')
            
            if is_echo(sender, text):
                print(f"⏭️  跳过回音消息：{text[:50]}...", file=sys.stderr)
                continue
            
            # 输出非回音消息
            print(f"📨 收到消息：来自 {sender} - {text[:50]}...", file=sys.stderr)
            print(json.dumps(message, ensure_ascii=False))
            
        except json.JSONDecodeError:
            print(f"⚠️ 无效 JSON: {line.strip()}", file=sys.stderr)
        except Exception as e:
            print(f"❌ 错误：{e}", file=sys.stderr)

if __name__ == '__main__':
    main()
