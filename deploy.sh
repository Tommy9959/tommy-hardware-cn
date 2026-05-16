#!/bin/bash
# jh-hardware.com 部署脚本
set -e

cd ~/Sites/hardware-site

echo "🔨 Building..."
hugo --destination ../docs

# llms.txt 需要手动复制（Hugo 不复制 .txt 文件）
cp static/llms.txt ../docs/llms.txt 2>/dev/null && echo "📄 llms.txt copied" || true

echo "📤 Committing source..."
git add -A
git commit -m "Update: $(date '+%Y-%m-%d %H:%M')"
git push origin main

echo "🌐 Deploying to gh-pages..."
git worktree add /tmp/deploy gh-pages
rm -rf /tmp/deploy/*
cp -r ../docs/* /tmp/deploy/
echo "jh-hardware.com" > /tmp/deploy/CNAME
cp static/llms.txt /tmp/deploy/llms.txt 2>/dev/null || true

cd /tmp/deploy
git add -A
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M')"
git push origin gh-pages

cd ~/Sites/hardware-site
git worktree remove /tmp/deploy
git checkout main -f

echo "✅ 部署完成"
