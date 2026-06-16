#!/bin/bash
# jh-hardware.com 部署脚本 v3.1 — 2026-06-16 (已修复 sitemap 循环引用问题)
# 修复：en/sitemap.xml 被 Cloudflare 301 到 sitemap.xml 导致 Google 无法索引
# 方案：部署后将 en/zh/ar 子 sitemap 合并到单个扁平 root sitemap.xml
set -e

SITE_DIR=~/Sites/hardware-site
DEPLOY_DIR=~/Sites/docs

cd "$SITE_DIR"

echo "🔨 Building..."
hugo --destination "$DEPLOY_DIR"

# llms.txt（Hugo 不复制 .txt 文件）
cp static/llms.txt "$DEPLOY_DIR/llms.txt" 2>/dev/null && echo "📄 llms.txt copied" || true

# 合并 sitemap（修复 en/sitemap.xml 被 Cloudflare 301 的问题）
echo "🔗 Merging sitemap (fixing Cloudflare 301 redirect loop)..."
python3 "$SITE_DIR/scripts/merge-sitemap.py" "$DEPLOY_DIR"

echo "📤 Committing source..."
git add -A
git commit -m "Update: $(date '+%Y-%m-%d %H:%M')"
git push origin main

echo "🌐 Deploying to gh-pages..."
git worktree add /tmp/deploy gh-pages
rm -rf /tmp/deploy/*
cp -r "$DEPLOY_DIR"/* /tmp/deploy/
echo "jh-hardware.com" > /tmp/deploy/CNAME
cp static/llms.txt /tmp/deploy/llms.txt 2>/dev/null || true

cd /tmp/deploy
git add -A
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M')"
git push origin gh-pages

cd "$SITE_DIR"
git worktree remove /tmp/deploy
git checkout main -f

echo ""
echo "✅ 部署完成"
echo "   📄 sitemap 已合并为单个扁平文件"
echo "   💡 记得到 GSC 请求重新提交 sitemap.xml"
