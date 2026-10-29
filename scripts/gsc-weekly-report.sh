#!/bin/bash
# ==========================================================
# GSC SEO 周报生成脚本
# 每周日运行，自动生成 SEO 周报并保存
# ==========================================================

# 配置
WEBSITE="https://jh-hardware.com"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SITE_DIR="$(dirname "$SCRIPT_DIR")"
REPORT_DIR="$SITE_DIR/docs"
LOG_DIR="/Users/zhuxiaolei/.openclaw/workspace/logs"

# 代理配置（统一走 clash mixed-port）
PROXY="http://127.0.0.1:7890"

# Python 解释器（系统 python3 缺 dotenv/google 依赖，优先用 hermes venv）
PYTHON="/Users/zhuxiaolei/.hermes/hermes-agent/venv/bin/python"
[ -x "$PYTHON" ] || PYTHON="python3"

export HTTP_PROXY="$PROXY"
export HTTPS_PROXY="$PROXY"
export http_proxy="$PROXY"
export https_proxy="$PROXY"
export ALL_PROXY="socks5://127.0.0.1:7890"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
WEEK_START=$(date -v -6d "+%Y-%m-%d")
WEEK_END=$(date -v +0d "+%Y-%m-%d")
REPORT_FILE="$REPORT_DIR/gsc-weekly-report-$(date +%Y%m%d).md"
LOG_FILE="$LOG_DIR/gsc-weekly-cron.log"

mkdir -p "$LOG_DIR" "$REPORT_DIR"

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

notify() {
    local msg="$1"
    echo "$msg" | /opt/homebrew/bin/imsg rpc +8618358008400 >/dev/null 2>&1 || true
}

# 基本 SEO 检测
basic_seo_check() {
    local report_section=""
    
    local http_code=$(curl -s -x "$PROXY" -o /dev/null -w "%{http_code}" "$WEBSITE" 2>/dev/null)
    if [ "$http_code" = "200" ]; then
        report_section+="| 网站可访问性 | ✅ | HTTP 200 正常 |\\n"
    else
        report_section+="| 网站可访问性 | ❌ | HTTP $http_code |\\n"
    fi
    
    local sitemap_code=$(curl -s -x "$PROXY" -o /dev/null -w "%{http_code}" "$WEBSITE/sitemap.xml" 2>/dev/null)
    # sitemap.xml 是 sitemapindex（en/zh/ar 三个子 sitemap），必须累加子 sitemap 的 URL 数
    local sm_root=$(curl -s -x "$PROXY" "$WEBSITE/sitemap.xml" 2>/dev/null)
    local url_count=0
    local sitemap_desc=""
    if echo "$sm_root" | grep -q "<sitemapindex"; then
        for _lang in en zh ar; do
            local _n=$(curl -s -x "$PROXY" "$WEBSITE/$_lang/sitemap.xml" 2>/dev/null | grep -o "<loc>" | wc -l | tr -d " ")
            url_count=$((url_count + ${_n:-0}))
        done
        sitemap_desc="$url_count 个 URL（en/zh/ar 三语言合计）"
    else
        url_count=$(echo "$sm_root" | grep -o "<loc>" | wc -l | tr -d " ")
        sitemap_desc="$url_count 个 URL"
    fi
    if [ "$sitemap_code" = "200" ]; then
        report_section+="| sitemap.xml | ✅ | 可访问，$sitemap_desc |\\n"
    else
        report_section+="| sitemap.xml | ❌ | HTTP $sitemap_code |\\n"
    fi
    
    local robots_code=$(curl -s -x "$PROXY" -o /dev/null -w "%{http_code}" "$WEBSITE/robots.txt" 2>/dev/null)
    if [ "$robots_code" = "200" ]; then
        report_section+="| robots.txt | ✅ | 可访问 |\\n"
    else
        report_section+="| robots.txt | ⚠️ | HTTP $robots_code |\\n"
    fi
    
    local load_time=$(curl -s -x "$PROXY" -o /dev/null -w "%{time_total}" "$WEBSITE" 2>/dev/null)
    local load_fmt=$(printf "%.2f" "$load_time" 2>/dev/null || echo "?.??")
    if [ -n "$load_time" ] && [ "$(echo "$load_time < 2" | bc 2>/dev/null)" = "1" ]; then
        report_section+="| 页面加载速度 | ✅ | ${load_fmt}s |\\n"
    else
        report_section+="| 页面加载速度 | ⚠️ | ${load_fmt}s（建议 <2s） |\\n"
    fi
    
    local ga_found=$(curl -s -x "$PROXY" "$WEBSITE" 2>/dev/null | grep -c "G-EW8MR1LQWY" || echo "0")
    if [ "$ga_found" -gt 0 ]; then
        report_section+="| Google Analytics | ✅ | 已集成 |\\n"
    fi
    
    echo -e "$report_section"
}

# 检查产品页面数量
check_product_pages() {
    local en_products=$(find "$SITE_DIR/content/en/products" -name "*.md" | wc -l)
    local zh_products=$(find "$SITE_DIR/content/zh/products" -name "*.md" | wc -l)
    local ar_products=$(find "$SITE_DIR/content/ar/products" -name "*.md" | wc -l)
    echo "| 英文产品页 | ✅ | $en_products 个 |"
    echo "| 中文产品页 | ✅ | $zh_products 个 |"
    echo "| 阿拉伯语产品页 | ✅ | $ar_products 个 |"
}

# 检查 llms.txt
check_llms_txt() {
    # 线上检查更可靠
    local llms_code=$(curl -s -x "$PROXY" -o /dev/null -w "%{http_code}" "$WEBSITE/llms.txt" 2>/dev/null)
    if [ "$llms_code" = "200" ]; then
        echo "| llms.txt / .well-known/llms.txt | ✅ | 线上可访问 |"
    else
        echo "| llms.txt | ⚠️ | HTTP $llms_code（线上检查） |"
    fi
}

# 检查结构化数据
check_schema() {
    local schema_count=$(grep -r "schema.org" "$SITE_DIR/content" --include="*.md" -l 2>/dev/null | wc -l)
    if [ "$schema_count" -gt 0 ]; then
        echo "| 结构化数据 (Schema) | ✅ | $schema_count 个页面有标注 |"
    else
        echo "| 结构化数据 (Schema) | ⚠️ | 未检测到 |"
    fi
}

# 检查 GSC 凭据
check_gsc_credentials() {
    local token="$HOME/.openclaw/service-env/gsc-oauth-token.json"
    if [ ! -f "$token" ]; then
        echo "| GSC API 凭据 | ⏸️ | 未配置（运行 scripts/gsc-api-setup.py 授权） |"
        return
    fi

    # Token 过期日期（refresh token 失效后必须重新授权，不会自动恢复）
    local exp=$("$PYTHON" -c "import json,sys;print(json.load(open(sys.argv[1])).get('expiry','')[:10])" "$token" 2>/dev/null)
    if [ -n "$exp" ]; then
        if [ "$exp" \< "$(date +%Y-%m-%d)" ]; then
            echo "| GSC API 凭据 | ❌ | Token 已于 $exp 过期 |"
        else
            echo "| GSC API 凭据 | ✅ | Token 有效至 $exp |"
        fi
    fi

    rm -f /tmp/gsc-weekly-data.json /tmp/gsc-weekly-err.log
    "$PYTHON" "$SCRIPT_DIR/gsc_fetch.py" --raw --days 7 > /tmp/gsc-weekly-data.json 2>/tmp/gsc-weekly-err.log

    if grep -q "total_impressions" /tmp/gsc-weekly-data.json 2>/dev/null; then
        echo "| GSC 数据拉取 | ✅ | 成功 |"
    else
        local reason="未知错误"
        if grep -q "invalid_grant" /tmp/gsc-weekly-err.log /tmp/gsc-weekly-data.json 2>/dev/null; then
            reason="refresh token 失效(invalid_grant) → 必须重新授权"
        elif grep -q "Max retries\|ProxyError\|Connection" /tmp/gsc-weekly-err.log 2>/dev/null; then
            reason="网络/代理不通（检查 Clash 7890 端口）"
        elif grep -q "No module named" /tmp/gsc-weekly-err.log 2>/dev/null; then
            reason="Python 依赖缺失"
        fi
        echo "| GSC 数据拉取 | ❌ | $reason |"
        echo "| 处理办法 | 🔧 | $PYTHON $SCRIPT_DIR/gsc-api-setup.py --auth（浏览器重新授权） |"
        notify "⚠️ GSC 周报数据拉取失败：$reason（$TIMESTAMP）"
    fi
}

# 生成周报
generate_weekly_report() {
    log "生成 SEO 周报..."
    
    local basic_data=$(basic_seo_check)
    local product_data=$(check_product_pages)
    local llms_status=$(check_llms_txt)
    local schema_status=$(check_schema)
    local gsc_status=$(check_gsc_credentials)
    
    cat > "$REPORT_FILE" << 'REPORTHEADER'
# 📊 jh-hardware.com SEO 周报
REPORTHEADER
    echo "" >> "$REPORT_FILE"
    echo "**报告周期：** ${WEEK_START} ~ ${WEEK_END}" >> "$REPORT_FILE"
    echo "**生成时间：** ${TIMESTAMP}" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "---" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "## 1. 🔧 网站健康检查" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "| 检查项 | 状态 | 详情 |" >> "$REPORT_FILE"
    echo "|--------|------|------|" >> "$REPORT_FILE"
    echo -e "$basic_data" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "## 2. 📄 SEO 配置" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "| 项目 | 状态 | 详情 |" >> "$REPORT_FILE"
    echo "|------|------|------|" >> "$REPORT_FILE"
    echo "$llms_status" >> "$REPORT_FILE"
    echo "$schema_status" >> "$REPORT_FILE"
    echo "$gsc_status" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "## 3. 📄 内容覆盖" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "| 项目 | 状态 | 数量 |" >> "$REPORT_FILE"
    echo "|------|------|------|" >> "$REPORT_FILE"
    echo "$product_data" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "## 4. 🌐 语言覆盖" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "| 语言 | 状态 | 覆盖地区 |" >> "$REPORT_FILE"
    echo "|------|------|----------|" >> "$REPORT_FILE"
    echo "| 🇬🇧 英文 | ✅ | 全球/非洲/中东 |" >> "$REPORT_FILE"
    echo "| 🇨🇳 中文 | ✅ | 中国供应商/中文用户 |" >> "$REPORT_FILE"
    echo "| 🇸🇦 阿拉伯语 | ✅ | 中东/北非 |" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "## 5. 🎯 本周行动建议" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "- ✅ 持续检查网站可访问性和 sitemap 状态" >> "$REPORT_FILE"
    echo "- ✅ 关注 Google Search Console 数据变化" >> "$REPORT_FILE"
    echo "- ✅ 持续更新客户案例和博客内容" >> "$REPORT_FILE"
    echo "- ✅ 检查产品页面是否保持最新" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    if grep -q "total_impressions" /tmp/gsc-weekly-data.json 2>/dev/null; then
        echo "## 6. 📈 搜索表现（近 7 天）" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        "$PYTHON" - /tmp/gsc-weekly-data.json >> "$REPORT_FILE" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))
print("| 指标 | 数值 |")
print("|------|------|")
print(f"| 点击 | {d.get('total_clicks', 0)} |")
print(f"| 展示 | {d.get('total_impressions', 0)} |")
print(f"| CTR | {d.get('avg_ctr_percent', 0)}% |")
print(f"| 平均排名 | {d.get('avg_position', 0)} |")
rows = d.get('top_queries', [])[:10]
if rows:
    print("")
    print("**Top 关键词**")
    print("")
    print("| 关键词 | 展示 | 点击 | 排名 |")
    print("|--------|------|------|------|")
    for r in rows:
        print(f"| {r['keyword']} | {r['impressions']} | {r['clicks']} | {r['position']} |")
pages = d.get('top_pages', [])[:8]
if pages:
    print("")
    print("**Top 页面**")
    print("")
    print("| 页面 | 展示 | 点击 | 排名 |")
    print("|------|------|------|------|")
    for r in pages:
        print(f"| {r['page']} | {r['impressions']} | {r['clicks']} | {r['position']} |")
PYEOF
        echo "" >> "$REPORT_FILE"
    fi

    echo "---" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    local report_date=$(date '+%Y-%m-%d %H:%M')
    echo "*自动生成时间: ${report_date}*" >> "$REPORT_FILE"

    log "✅ SEO 周报已生成: $REPORT_FILE"
    
    # 清理临时文件
    rm -f /tmp/gsc-weekly-latest.md
}

# 主函数
main() {
    echo "============================="
    echo "📊 开始生成 SEO 周报"
    echo "============================="
    
    generate_weekly_report
    
    echo "✅ SEO 周报生成完成"
    echo "📁 文件: $REPORT_FILE"
    echo "============================="
}

main
