#!/bin/bash
# ==========================================================
# GSC 索引健康检查脚本
# 每周一运行，检查索引状态和错误
# ==========================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="/Users/zhuxiaolei/.openclaw/workspace/logs"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
REPORT_FILE="$LOG_DIR/gsc-index-check-$(date +%Y%m%d).md"
LOG_FILE="$LOG_DIR/gsc-index-cron.log"

mkdir -p "$LOG_DIR"

log() { echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"; }

log "=========================================="
log "📊 开始 GSC 索引健康检查"
log "=========================================="

# 1. 网站可访问性
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://jh-hardware.com")
if [ "$HTTP_CODE" = "200" ]; then
    log "✅ 网站正常 (HTTP 200)"
else
    log "❌ 网站异常 (HTTP $HTTP_CODE)"
fi

# 2. sitemap 检查
SITEMAP_URLS=$(curl -s "https://jh-hardware.com/sitemap.xml" | grep -c "<loc>" 2>/dev/null)
log "📄 sitemap 包含 $SITEMAP_URLS 个 URL"

# 3. GSC 数据拉取（更新 token 并获取最新性能数据）
python3 "$SCRIPT_DIR/gsc-api-setup.py" --report --output /tmp/gsc-latest.md 2>&1 | grep -E "✅|❌|⚠️|Token|📝"

# 4. 从拉取的数据中提取关键指标
if [ -f /tmp/gsc-latest.md ]; then
    TOTAL_CLICKS=$(grep "总点击" /tmp/gsc-latest.md 2>/dev/null | grep -oE '[0-9]+' | head -1)
    TOTAL_IMPS=$(grep "总展示" /tmp/gsc-latest.md 2>/dev/null | grep -oE '[0-9]+' | head -1)
    AVG_RANK=$(grep "平均" /tmp/gsc-latest.md 2>/dev/null | grep -oE '[0-9.]+' | head -1)
    
    log "📊 近3个月性能: 点击$TOTAL_CLICKS 展示$TOTAL_IMPS 平均排名$AVG_RANK"
    
    cat /tmp/gsc-latest.md > "$REPORT_FILE"
    log "✅ 报告已保存: $REPORT_FILE"
else
    log "⚠️ GSC 数据拉取失败"
    echo "# ⚠️ GSC 数据拉取失败" > "$REPORT_FILE"
    echo "时间: $TIMESTAMP" >> "$REPORT_FILE"
    echo "请在 GSC 后台手动检查索引状态: https://search.google.com/search-console" >> "$REPORT_FILE"
fi

rm -f /tmp/gsc-latest.md

log "✅ GSC 索引健康检查完成"
log "=========================================="
