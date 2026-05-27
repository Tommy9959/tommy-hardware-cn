#!/usr/bin/env python3
"""
扁平 sitemap.xml 生成器 v3
从 Hugo 构建后的多语言 sitemap 合并为扁平 sitemap.xml
兜底：从文件系统直接扫描生成的 HTML 页面
"""
import xml.etree.ElementTree as ET
import os, sys, argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--deploy-dir', default=None, help='部署目录路径')
args = parser.parse_args()

if args.deploy_dir:
    DOCS_DIR = os.path.abspath(args.deploy_dir)
else:
    SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DOCS_DIR = os.path.join(SITE_DIR, 'docs')

OUTPUT = os.path.join(DOCS_DIR, 'sitemap.xml')
BASE_URL = 'https://jh-hardware.com'
TODAY = datetime.now().strftime('%Y-%m-%d')

# Try method 1: Read language-specific sitemaps
sitemap_files = [
    os.path.join(DOCS_DIR, 'en', 'sitemap.xml'),
    os.path.join(DOCS_DIR, 'zh', 'sitemap.xml'),
    os.path.join(DOCS_DIR, 'ar', 'sitemap.xml'),
]

urls = []
found_via_sitemap = False

for f in sitemap_files:
    if os.path.exists(f):
        try:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            for url in root.findall('.//sm:url', ns):
                loc = url.find('sm:loc', ns)
                lastmod = url.find('sm:lastmod', ns)
                urls.append({
                    'loc': loc.text if loc is not None else '',
                    'lastmod': lastmod.text if lastmod is not None else TODAY,
                })
            found_via_sitemap = True
        except Exception as e:
            print(f"⚠️  无法解析 {f}: {e}")

# Method 2 (fallback): Scan filesystem for index.html files
if not found_via_sitemap:
    print("📂 语言 sitemap 未找到，从文件系统扫描...")
    for root_dir, dirs, files in os.walk(DOCS_DIR):
        if 'index.html' in files:
            rel_path = os.path.relpath(root_dir, DOCS_DIR)
            # Skip hidden directories
            if any(p.startswith('.') for p in rel_path.split(os.sep)):
                continue
            url_path = '/' + rel_path.replace(os.sep, '/')
            url_path = url_path.rstrip('/') or '/'
            urls.append({
                'loc': BASE_URL + url_path,
                'lastmod': TODAY,
            })

# Sort URLs
urls.sort(key=lambda x: x['loc'])

if not urls:
    print("❌ 未找到任何页面，无法生成 sitemap")
    sys.exit(1)

# Generate flat sitemap.xml
lines = ['<?xml version="1.0" encoding="utf-8" standalone="yes"?>']
lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
for u in urls:
    lines.append('  <url>')
    lines.append(f'    <loc>{u["loc"]}</loc>')
    if u.get("lastmod"):
        lines.append(f'    <lastmod>{u["lastmod"]}</lastmod>')
    lines.append('  </url>')
lines.append('</urlset>')

with open(OUTPUT, 'w') as f:
    f.write('\n'.join(lines))

# Clean up language-specific sitemaps if they still exist
for f in sitemap_files:
    if os.path.exists(f):
        os.remove(f)

print(f"✅ 扁平sitemap已生成: {OUTPUT}")
print(f"   总URL: {len(urls)}")
