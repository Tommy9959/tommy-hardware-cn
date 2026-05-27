#!/bin/bash
# jh-hardware.com 部署脚本 v3.0 — 2026-05-27
# Hugo v0.160 默认输出 sitemapindex，不需要额外合并脚本
set -e

SITE_DIR=~/Sites/hardware-site
DEPLOY_DIR=~/Sites/docs

cd "$SITE_DIR"

echo "🔨 Building..."
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
git add -A
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M')"
git push origin gh-pages

cd "$SITE_DIR"
git worktree remove /tmp/deploy
git checkout main -f

echo "✅ 部署完成"
