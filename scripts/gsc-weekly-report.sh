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
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
WEEK_START=$(date -v -6d "+%Y-%m-%d")
WEEK_END=$(date -v +0d "+%Y-%m-%d")
REPORT_FILE="$REPORT_DIR/gsc-weekly-report-$(date +%Y%m%d).md"
LOG_FILE="$LOG_DIR/gsc-weekly-cron.log"

mkdir -p "$LOG_DIR" "$REPORT_DIR"

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# 基本 SEO 检测
basic_seo_check() {
    local report_section=""
    
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$WEBSITE" 2>/dev/null)
    if [ "$http_code" = "200" ]; then
        report_section+="| 网站可访问性 | ✅ | HTTP 200 正常 |\\n"
    else
        report_section+="| 网站可访问性 | ❌ | HTTP $http_code |\\n"
    fi
    
    local sitemap_code=$(curl -s -o /dev/null -w "%{http_code}" "$WEBSITE/sitemap.xml" 2>/dev/null)
    local url_count=$(curl -s "$WEBSITE/sitemap.xml" 2>/dev/null | grep -c "<loc>" || echo "0")
    if [ "$sitemap_code" = "200" ]; then
        report_section+="| sitemap.xml | ✅ | 可访问，$url_count 个 URL |\\n"
    else
        report_section+="| sitemap.xml | ❌ | HTTP $sitemap_code |\\n"
    fi
    
    local robots_code=$(curl -s -o /dev/null -w "%{http_code}" "$WEBSITE/robots.txt" 2>/dev/null)
    if [ "$robots_code" = "200" ]; then
        report_section+="| robots.txt | ✅ | 可访问 |\\n"
    else
        report_section+="| robots.txt | ⚠️ | HTTP $robots_code |\\n"
    fi
    
    local load_time=$(curl -s -o /dev/null -w "%{time_total}" "$WEBSITE" 2>/dev/null)
    local load_fmt=$(printf "%.2f" "$load_time" 2>/dev/null || echo "?.??")
    if [ -n "$load_time" ] && [ "$(echo "$load_time < 2" | bc 2>/dev/null)" = "1" ]; then
        report_section+="| 页面加载速度 | ✅ | ${load_fmt}s |\\n"
    else
        report_section+="| 页面加载速度 | ⚠️ | ${load_fmt}s（建议 <2s） |\\n"
    fi
    
    local ga_found=$(curl -s "$WEBSITE" 2>/dev/null | grep -c "G-EW8MR1LQWY" || echo "0")
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
    if [ -f "$SITE_DIR/static/llms.txt" ]; then
        echo "| llms.txt | ✅ | 已配置（服务 AI 搜索引擎） |"
    else
        echo "| llms.txt | ⚠️ | 未配置 |"
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
    if [ -f "$HOME/.openclaw/service-env/gsc-oauth-token.json" ]; then
        echo "| GSC API 凭据 | ✅ | OAuth Token 已配置 |"
        # 尝试获取 GSC 数据（使用 perl 做跨平台超时，兼容 macOS 无 timeout 命令）
        local gsc_output=$(perl -e 'alarm shift @ARGV; exec @ARGV' 15 python3 "$SCRIPT_DIR/gsc-api-setup.py" --report --output /tmp/gsc-weekly-latest.md 2>/dev/null)
        if [ -f /tmp/gsc-weekly-latest.md ] && [ -s /tmp/gsc-weekly-latest.md ]; then
            echo "| GSC 数据拉取 | ✅ | 成功 |"
        else
            echo "| GSC 数据拉取 | ⚠️ | API 调用失败 |"
        fi
    elif [ -f "$HOME/.openclaw/service-env/gsc-credentials.json" ]; then
        echo "| GSC API 凭据 | ⏸️ | 旧版 service account 凭据，建议用 OAuth 重授权 |"
    else
        echo "| GSC API 凭据 | ⏸️ | 未配置（运行 gsc-api-setup.py --auth 授权） |"
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
