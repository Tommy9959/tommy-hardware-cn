#!/usr/bin/env python3
"""Hugo 构建后合并多语言 sitemap"""
import os, re
from xml.sax.saxutils import escape

SITE_DIR = os.path.expanduser("~/Sites/hardware-site")
DOCS_DIR = os.path.join(SITE_DIR, "..", "docs")
BASE_URL = "https://jh-hardware.com"

def extract_urls(filepath):
    """从 sitemap XML 中提取所有 URL"""
    urls = []
    with open(filepath, "r") as f:
        content = f.read()
    for match in re.finditer(r"<loc>(.*?)</loc>", content):
        urls.append(match.group(1))
    return urls

def build_sitemap(urls):
    """构建合并后的 sitemap XML"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    
    lines = ['<?xml version="1.0" encoding="utf-8" standalone="yes"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for url in urls:
        lines.append(f"  <url><loc>{escape(url)}</loc><lastmod>{today}</lastmod></url>")
    lines.append("</urlset>")
    return "\n".join(lines)

# 收集所有语言页面的 URL（不含 en/ 后缀的）
all_urls = []
for lang in ['en', 'zh', 'ar']:
    sitemap_path = os.path.join(DOCS_DIR, lang, 'sitemap.xml')
    if os.path.exists(sitemap_path):
        urls = extract_urls(sitemap_path)
        all_urls.extend(urls)
        print(f"  {lang}: {len(urls)} 条URL")
    else:
        print(f"  {lang}: 不存在")

# 去重
all_urls = list(dict.fromkeys(all_urls))  # 保持顺序去重

# 写回主 sitemap
output_path = os.path.join(DOCS_DIR, 'sitemap.xml')
with open(output_path, "w") as f:
    f.write(build_sitemap(all_urls))

print(f"\n合并后: {len(all_urls)} 条URL")
print(f"输出: {output_path}")
print(f"前5条:")
for u in all_urls[:5]:
    print(f"  {u}")
