#!/usr/bin/env python3
"""把 SVG 保存为 .png 以防止 Cloudflare 404 缓存问题"""
import os, glob, shutil

SITE_DIR = os.path.expanduser("~/Sites/hardware-site")
STATIC_DIR = f"{SITE_DIR}/static/images/products"

# 把 SVG 复制為 .png
cats = ["door-handles", "sofa-legs", "sliding-tracks", "cabinet-hardware",
        "furniture-fittings", "steel-pipes-flanges", "door-accessories"]

count = 0
for cat in cats:
    cat_dir = f"{STATIC_DIR}/{cat}"
    for f in glob.glob(f"{cat_dir}/*.svg"):
        png_path = f.replace(".svg", ".png")
        if not os.path.exists(png_path):
            shutil.copy2(f, png_path)
            count += 1
            print(f"  ✅ {cat}/{os.path.basename(png_path)}")

print(f"\n转换 {count} 个 SVG → PNG")

# 更新产品页图片引用
updated = 0
for lang in ['en', 'zh', 'ar']:
    for cat in cats:
        content_dir = f"{SITE_DIR}/content/{lang}/products/{cat}"
        if not os.path.isdir(content_dir):
            continue
        for fname in os.listdir(content_dir):
            if not fname.endswith('.md') or fname == '_index.md':
                continue
            filepath = f"{content_dir}/{fname}"
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            base = fname.replace('.md', '')
            old = f"/images/products/{cat}/{base}.svg"
            new = f"/images/products/{cat}/{base}.png"
            if old in content:
                content = content.replace(old, new)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated += 1

print(f"\n更新 {updated} 个产品页引用 SVG→PNG")
