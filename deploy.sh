#!/bin/bash
# jh-hardware.com 部署脚本 v4.0 — 2026-06-24
# 使用 Hugo v0.160 原生 sitemapindex（不再手动合并扁平 sitemap）
# Cloudflare 对 en/zh/ar/sitemap.xml 返回正常 200，无 301 循环
set -e

SITE_DIR=~/Sites/hardware-site
DEPLOY_DIR=~/Sites/docs

cd "$SITE_DIR"

echo "🔨 Building..."
rm -rf "$DEPLOY_DIR"/*
hugo --destination "$DEPLOY_DIR"

# llms.txt（Hugo 不复制 .txt 文件）
cp static/llms.txt "$DEPLOY_DIR/llms.txt" 2>/dev/null && echo "📄 llms.txt copied" || true

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
# GitHub Pages 需要 .nojekyll 防止 Jekyll 干扰
touch .nojekyll
git add -A
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M')"
git push origin gh-pages

cd "$SITE_DIR"
git worktree remove /tmp/deploy
git checkout main -f

echo ""
echo "✅ 部署完成"
echo "   📄 使用 Hugo v0.160 原生 sitemapindex 结构"
echo "   💡 记得到 GSC 请求重新提交 sitemap.xml"
