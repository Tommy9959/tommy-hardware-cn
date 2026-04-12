#!/bin/bash

# Google Search Console 每日检查脚本
# 用于监控 jh-hardware.com 的 SEO 状态

# 配置
WEBSITE="https://jh-hardware.com"
LOG_FILE="/Users/zhuxiaolei/.openclaw/workspace/logs/gsc-daily-check.log"
REPORT_FILE="/Users/zhuxiaolei/.openclaw/workspace/logs/gsc-daily-report-$(date +%Y-%m-%d).md"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# 检查网站可访问性
check_website() {
    log "检查网站可访问性..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$WEBSITE" 2>/dev/null)
    
    if [ "$HTTP_CODE" = "200" ]; then
        log "${GREEN}✅ 网站状态正常 (HTTP $HTTP_CODE)${NC}"
        return 0
    else
        log "${RED}❌ 网站访问异常 (HTTP $HTTP_CODE)${NC}"
        return 1
    fi
}

# 检查 robots.txt
check_robots() {
    log "检查 robots.txt..."
    ROBOTS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$WEBSITE/robots.txt" 2>/dev/null)
    
    if [ "$ROBOTS_CODE" = "200" ]; then
        log "${GREEN}✅ robots.txt 可访问${NC}"
        return 0
    else
        log "${YELLOW}⚠️ robots.txt 访问异常${NC}"
        return 1
    fi
}

# 检查 sitemap.xml
check_sitemap() {
    log "检查 sitemap.xml..."
    SITEMAP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$WEBSITE/sitemap.xml" 2>/dev/null)
    
    if [ "$SITEMAP_CODE" = "200" ]; then
        log "${GREEN}✅ sitemap.xml 可访问${NC}"
        # 统计 sitemap 中的 URL 数量
        URL_COUNT=$(curl -s "$WEBSITE/sitemap.xml" 2>/dev/null | grep -c "<loc>" || echo "0")
        log "sitemap 中包含 $URL_COUNT 个 URL"
        return 0
    else
        log "${RED}❌ sitemap.xml 访问异常${NC}"
        return 1
    fi
}

# 检查 Google Analytics
check_analytics() {
    log "检查 Google Analytics 集成..."
    GA_FOUND=$(curl -s "$WEBSITE" 2>/dev/null | grep -c "G-EW8MR1LQWY" || echo "0")
    
    if [ "$GA_FOUND" -gt 0 ]; then
        log "${GREEN}✅ Google Analytics 代码已集成${NC}"
        return 0
    else
        log "${YELLOW}⚠️ Google Analytics 代码未找到${NC}"
        return 1
    fi
}

# 生成日报
generate_report() {
    cat > "$REPORT_FILE" << EOF
# 📊 jh-hardware.com SEO 日报

**日期：** $(date +%Y-%m-%d)
**检查时间：** $TIMESTAMP

## ✅ 检查结果

| 检查项 | 状态 | 详情 |
|--------|------|------|
| 网站可访问性 | $([ "$HTTP_CODE" = "200" ] && echo "✅ 正常" || echo "❌ 异常") | HTTP $HTTP_CODE |
| robots.txt | $([ "$ROBOTS_CODE" = "200" ] && echo "✅ 正常" || echo "⚠️ 异常") | HTTP $ROBOTS_CODE |
| sitemap.xml | $([ "$SITEMAP_CODE" = "200" ] && echo "✅ 正常" || echo "❌ 异常") | HTTP $SITEMAP_CODE, $URL_COUNT 个 URL |
| Google Analytics | $([ "$GA_FOUND" -gt 0 ] && echo "✅ 已集成" || echo "⚠️ 未找到") | G-EW8MR1LQWY |

## 📈 需要关注的指标

请登录 Google Search Console 查看：
- 索引状态：https://search.google.com/search-console/index
- 效果报告：https://search.google.com/search-console/performance
- 网站地图：https://search.google.com/search-console/sitemap

## 🎯 行动建议

$([ "$HTTP_CODE" != "200" ] && echo "- ❌ 网站访问异常，需要立即检查" || echo "- ✅ 网站运行正常")
$([ "$SITEMAP_CODE" != "200" ] && echo "- ❌ sitemap 访问异常，需要修复" || echo "- ✅ sitemap 正常")

---

*自动生成报告 | 下次检查：明天 9:00 AM*
EOF

    log "日报已生成：$REPORT_FILE"
}

# 发送微信通知（通过 OpenClaw）
send_wechat_notification() {
    local status=$1
    local message=$2
    
    # 这里调用 OpenClaw 的消息功能
    # 实际使用时需要根据 OpenClaw 的 API 调整
    log "准备发送微信通知..."
    log "状态：$status"
    log "消息：$message"
}

# 主函数
main() {
    log "=========================================="
    log "开始每日 SEO 检查"
    log "=========================================="
    
    # 执行检查
    check_website
    WEBSITE_STATUS=$?
    
    check_robots
    ROBOTS_STATUS=$?
    
    check_sitemap
    SITEMAP_STATUS=$?
    
    check_analytics
    ANALYTICS_STATUS=$?
    
    # 生成报告
    generate_report
    
    # 汇总状态
    log "=========================================="
    if [ $WEBSITE_STATUS -eq 0 ] && [ $SITEMAP_STATUS -eq 0 ]; then
        log "${GREEN}✅ 所有检查通过${NC}"
        send_wechat_notification "success" "今日 SEO 检查全部通过"
    else
        log "${RED}❌ 发现问题，需要处理${NC}"
        send_wechat_notification "error" "今日 SEO 检查发现问题"
    fi
    log "=========================================="
}

# 执行
main
