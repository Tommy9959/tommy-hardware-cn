#!/usr/bin/env python3
"""
合并多语言 sitemap → 单个扁平 sitemap.xml
解决：en/sitemap.xml 被 Cloudflare 301 到 sitemap.xml 导致的循环引用问题

策略：将 en/zh/ar 子 sitemap 的所有 <url> 条目合并到根 sitemap.xml
使用纯文本操作避免 XML 序列化带来的命名空间问题

用法：python3 scripts/merge-sitemap.py <deploy_dir>
"""

import sys, os, re

SITE_URL = 'https://jh-hardware.com'

def merge_sitemaps(deploy_dir: str) -> bool:
    root_sitemap = os.path.join(deploy_dir, 'sitemap.xml')
    if not os.path.exists(root_sitemap):
        print(f"❌ 未找到 {root_sitemap}")
        return False

    # 读取各语言子 sitemap 的 <url> 块
    languages = ['en', 'zh', 'ar']
    all_url_blocks = []
    urls_seen = set()
    
    for lang in languages:
        sitemap_path = os.path.join(deploy_dir, lang, 'sitemap.xml')
        if not os.path.exists(sitemap_path):
            print(f"⚠️  跳过 {lang}: 未找到 {sitemap_path}")
            continue
        
        with open(sitemap_path, 'r') as f:
            content = f.read()
        
        # 提取所有 <url>...</url> 块
        url_blocks = re.findall(r'<url>(.*?)</url>', content, re.DOTALL)
        print(f"  {lang}: {len(url_blocks)} URLs")
        
        for block in url_blocks:
            # 提取 <loc>
            loc_match = re.search(r'<loc>(.*?)</loc>', block)
            if loc_match:
                loc = loc_match.group(1).rstrip('/')
                if loc not in urls_seen:
                    urls_seen.add(loc)
                    all_url_blocks.append(block)
    
    print(f"\n  去重后: {len(all_url_blocks)} URLs")
    
    # 构建新的 sitemap
    lines = []
    lines.append('<?xml version="1.0" encoding="utf-8" standalone="yes"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml">')
    
    for block in all_url_blocks:
        lines.append('<url>')
        for line in block.split('\n'):
            stripped = line.strip()
            if stripped:
                lines.append(f'  {stripped}')
        lines.append('</url>')
    
    lines.append('</urlset>')
    lines.append('')
    
    output = '\n'.join(lines)
    
    with open(root_sitemap, 'w') as f:
        f.write(output)
    
    print(f"✅ 合并完成: {root_sitemap}")
    print(f"  总 URL 数: {len(all_url_blocks)}")
    
    # 统计各语言
    en_count = sum(1 for loc in urls_seen if not '/zh/' in loc and not '/ar/' in loc)
    zh_count = sum(1 for loc in urls_seen if '/zh/' in loc)
    ar_count = sum(1 for loc in urls_seen if '/ar/' in loc)
    print(f"  英文: {en_count} | 中文: {zh_count} | 阿拉伯: {ar_count}")
    
    # 验证可解析性
    with open(root_sitemap, 'r') as f:
        content = f.read()
    url_count = content.count('<url>')
    loc_count = content.count('<loc>')
    print(f"  验证: {url_count} 个 <url>, {loc_count} 个 <loc>")
    
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 merge-sitemap.py <deploy_dir>")
        sys.exit(1)
    
    deploy_dir = os.path.expanduser(sys.argv[1])
    if not os.path.isdir(deploy_dir):
        print(f"❌ 目录不存在: {deploy_dir}")
        sys.exit(1)
    
    print(f"📄 合并 sitemap...")
    print(f"  源目录: {deploy_dir}")
    
    success = merge_sitemaps(deploy_dir)
    sys.exit(0 if success else 1)
