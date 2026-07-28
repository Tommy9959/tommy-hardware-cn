#!/bin/bash
# ==========================================================
# GSC 索引健康检查 + SEO 优化分析（周一 09:30 运行）
# 
# 职责：不仅仅是检查，而是输出可执行的 SEO 优化建议
# ==========================================================

# 代理
PROXY="http://127.0.0.1:7890"
export HTTP_PROXY="$PROXY" HTTPS_PROXY="$PROXY" http_proxy="$PROXY" https_proxy="$PROXY"
export ALL_PROXY="socks5://127.0.0.1:7890"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="/Users/zhuxiaolei/.openclaw/workspace/logs"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
REPORT_FILE="$LOG_DIR/gsc-index-check-$(date +%Y%m%d).md"
LOG_FILE="$LOG_DIR/gsc-index-cron.log"
JSON_DATA="/tmp/gsc-raw-data.json"

mkdir -p "$LOG_DIR"

log() { echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"; }
notify() { echo "$1" | /opt/homebrew/bin/imsg rpc +8618358008400 2>/dev/null || true; }

log "=========================================="
log "📊 GSC SEO 分析（周一索引检查）"
log "=========================================="

# 1. 网站可访问性
HTTP_CODE=$(curl -s -x "$PROXY" -o /dev/null -w "%{http_code}" "https://jh-hardware.com")
if [ "$HTTP_CODE" = "200" ]; then
    log "✅ 网站正常 (HTTP 200)"
else
    log "❌ 网站异常 (HTTP $HTTP_CODE)"
    notify "⚠️ GSC 检查：网站返回 HTTP $HTTP_CODE"
fi

# 2. 线上 sitemap 真实数量
SITEMAP_URLS=$(curl -s -x "$PROXY" "https://jh-hardware.com/sitemap.xml" | grep -c "<loc>" 2>/dev/null)
log "📄 sitemap 包含 $SITEMAP_URLS 个 URL（线上）"

# 3. 拉取 GSC 7天真实数据（JSON 格式）
log "📡 拉取 GSC 数据..."
python3 "$SCRIPT_DIR/gsc-api-setup.py" --raw --days 7 > "$JSON_DATA" 2>&1
if grep -q "total_impressions" "$JSON_DATA" 2>/dev/null; then
    log "✅ GSC 数据拉取成功"
else
    log "⚠️ GSC 数据拉取异常"
    cat "$JSON_DATA" >> "$LOG_FILE"
    notify "⚠️ GSC 数据拉取失败，需重新授权"
fi

# 4. 生成包含优化建议的完整报告
python3 "$SCRIPT_DIR/gsc-api-setup.py" --report 7 --output "$REPORT_FILE" 2>&1 | grep -E "✅|⚠️|📝" >> "$LOG_FILE"
log "✅ 报告已保存: $REPORT_FILE"

# 5. 从 JSON 提取关键指标做 SEO 推送
TOTAL_IMPS=$(python3 -c "import json; d=json.load(open('$JSON_DATA')); print(d['total_impressions'])" 2>/dev/null || echo "?")
TOTAL_CLICKS=$(python3 -c "import json; d=json.load(open('$JSON_DATA')); print(d['total_clicks'])" 2>/dev/null || echo "?")
AVG_POS=$(python3 -c "import json; d=json.load(open('$JSON_DATA')); print(d['avg_position'])" 2>/dev/null || echo "?")

log "📊 近7天: 展示$TOTAL_IMPS 点击$TOTAL_CLICKS 平均排名$AVG_POS"

# 6. AI 分析：找出本周优化点
# 6. 触发索引优化：重新提交 sitemap + 检查覆盖率
log "🔄 每周索引优化..."
python3 "$SCRIPT_DIR/gsc-index-optimizer.py" 2>&1 | grep -v "^=\|^$" >> "$LOG_FILE"
log "✅ 索引优化完成"

# 7. 推送简短 SEO 摘要给主人
SUMMARY=$(python3 << PYEOF 2>/dev/null
import json
with open("$JSON_DATA") as f:
    d = json.load(f)

imp = d["total_impressions"]
clk = d["total_clicks"]
pos = d["avg_position"]
ctr = d["avg_ctr_percent"]

kw_list = q = d.get("top_queries", [])
top_kw = q[0]["keyword"] if q else "?"

# 看有没有关键词排名前10
top10 = [x for x in q if x["position"] <= 10 and x["impressions"] >= 5]
if top10:
    kw_items = '/'.join([f"{x['keyword']}(#{int(x['position'])})" for x in top10[:3]])
    kw_note = f"排名前10: {kw_items}"
else:
    kw_note = "暂无关键词进前10"

# 优化建议
opps = [x for x in q if 11 <= x["position"] <= 30 and x["impressions"] >= 5]
opp_note = f"可优化: {opps[0]['keyword']}(#{int(opps[0]['position'])})" if opps else "暂无"

print(f"📊 GSC周报：{imp}展示 {clk}点击 CTR{ctr}% #{pos}位")
print(f"  {kw_note}")
print(f"  {opp_note}")
PYEOF
)

if [ -n "$SUMMARY" ]; then
    # 去换行，单行推送避免 imsg parse error
    ONE_LINE=$(echo "$SUMMARY" | tr '\n' ' ' | sed 's/  */ /g')
    notify "$ONE_LINE"
    log "📲 已推送 SEO 摘要"
fi

rm -f "$JSON_DATA"

log "✅ GSC SEO 分析完成"
log "=========================================="
