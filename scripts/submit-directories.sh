#!/bin/bash
# 提交 jh-hardware.com 到高质量目录
# 用法: ./submit-directories.sh

URL="https://jh-hardware.com"
TITLE="SOLA Hardware - China Door Hardware Factory for Africa"
DESCRIPTION="Factory-direct door hardware & building materials supplier for Nigeria, Kenya, and Africa. 10+ years export experience. Door locks, padlocks, hinges, handles, iron casing pipes."
EMAIL="z946487044@icloud.com"
KEYWORDS="door hardware, door locks, padlocks, Nigeria hardware, building materials China, Africa import"

echo "=== 提交到高质量免费目录 ==="

# 1. DMOZ-like directories
echo -n "→ hotfrog.com ... "
curl -s -o /dev/null -w "%{http_code}" "https://www.hotfrog.com/company/add" -d "name=SOLA+Hardware&url=$URL&description=$DESCRIPTION" 2>/dev/null || echo "skip"
echo ""

echo -n "→ cylex.com ... "
curl -s -o /dev/null -w "%{http_code}" "https://www.cylex.com/company" -d "name=SOLA+Hardware&url=$URL" 2>/dev/null || echo "skip"
echo ""

echo -n "→ yelp.com ... (manual - CAPTCHA)"
echo ""

echo ""
echo "=== 提交完成 ==="
echo "注意: 多数高质量目录需要手动验证, 建议每周手动提交2-3个"
echo "高优先级: tradewheel.com, made-in-china.com, alibaba.com"
