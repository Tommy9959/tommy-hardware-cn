#!/bin/bash
# BTC 分析脚本启动器
# 用于 crontab/launchd 调用，确保 PATH 正确

# 设置完整的 PATH 环境变量
export PATH=/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export NODE_PATH=/opt/homebrew/lib/node_modules

# 确保 openclaw 命令可用
export OPENCLAW_PATH=/Users/zhuxiaolei/.nvm/versions/node/v24.14.1/bin
export PATH=$OPENCLAW_PATH:$PATH

# 切换到脚本目录
cd /Users/zhuxiaolei/.openclaw/workspace/scripts

# 运行 BTC 分析脚本
/opt/homebrew/bin/node btc-analyzer.js --notify
