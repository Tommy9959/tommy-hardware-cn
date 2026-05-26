#!/usr/bin/env python3
"""为没有真实图片的产品生成带产品名的 SVG 占位图"""
import os, re

SITE_DIR = os.path.expanduser("~/Sites/hardware-site")
STATIC_DIR = f"{SITE_DIR}/static/images/products"

# 需要生成图片的分类和产品名
categories = {
    "door-handles": "Door Handle",
    "sofa-legs": "Sofa Leg",
    "sliding-tracks": "Sliding Track",
    "cabinet-hardware": "Cabinet Hardware Furniture Fittings",
    "furniture-fittings": "Furniture Fitting",
    "steel-pipes-flanges": "Steel Pipe Flange",
    "door-accessories": "Door Accessory",
}

def generate_svg(product_name, model, category_cn="", color="#1a73e8"):
    """生成专业风格的产品 SVG 示意图"""
    # 清理产品名
    clean_name = product_name.replace("'", "").replace('"', "")
    clean_model = model.replace("'", "").replace('"', "")
    
    # 根据分类选择合适的图标
    icons = {
        "door-handles": "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z",  # 水滴形（门把手形似）
        "sofa-legs": "M4 4h16v4H4zM4 12h16v8H4zM8 4v8M16 4v8",  # 矩形+腿
        "sliding-tracks": "M2 6h20v4H2zM2 14h20v4H2zM12 10v4",  # 平行滑轨
        "cabinet-hardware": "M10 2h4v12h-4zM6 8h12v2H6zM6 12h12v2H6z",  # 把手形
        "furniture-fittings": "M8 4h8v2H8zM6 8h12v2H6zM10 12h4v8h-4z",  # L型连接件
        "steel-pipes-flanges": "M6 6h12v12H6zM10 10h4v4h-4zM3 12h3M18 12h3M12 3v3M12 18v3",  # 管道法兰
        "door-accessories": "M6 4h12v16H6zM9 4v8M15 4v8M6 12h12",  # 门配件
    }
    
    # 确定分类并选图标
    for key in icons:
        if key in model.lower() or key.replace("-","") in model.lower():
            icon_path = icons[key]
            break
    else:
        icon_path = icons["door-accessories"]  # 默认
    
    # 从 category 推导颜色
    color_map = {
        "door-handles": "#1565C0",
        "sofa-legs": "#2E7D32",
        "sliding-tracks": "#6A1B9A",
        "cabinet-hardware": "#E65100",
        "furniture-fittings": "#C62828",
        "steel-pipes-flanges": "#37474F",
        "door-accessories": "#00838F",
    }
    color = color_map.get(category_cn, "#1a73e8")
    
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#f5f5f5;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="icon" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{color};stop-opacity:0.7" />
      <stop offset="100%" style="stop-color:{color};stop-opacity:0.3" />
    </linearGradient>
  </defs>
  <rect width="400" height="400" rx="8" fill="url(#bg)" stroke="#e0e0e0" stroke-width="1"/>
  <g transform="translate(100,60) scale(3.3)">
    <path d="{icon_path}" fill="url(#icon)" stroke="{color}" stroke-width="1" stroke-linejoin="round"/>
  </g>
  <text x="200" y="250" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#333" font-weight="bold">{clean_name}</text>
  <text x="200" y="275" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#666">{clean_model}</text>
  <text x="200" y="310" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#999">SOLA Hardware</text>
  <text x="200" y="330" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#bbb">Image coming soon</text>
</svg>'''
    return svg


def get_product_name_and_model(filepath):
    """从产品 frontmatter 提取 product_name 和 model"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None, None
    
    fm_text = match.group(1)
    product_name = None
    model = None
    
    for line in fm_text.split('\n'):
        m = re.match(r'^product_name:\s*[\\\'\"](.+)[\\\'\"]\s*$', line)
        if not m:
            m = re.match(r'^product_name:\s*["\']?(.+?)["\']?\s*$', line)
        if m:
            product_name = m.group(1).strip()
        m2 = re.match(r"^title:\s*['\"](.+?)['\"]", line)
        if m2:
            model = m2.group(1).strip()
    
    return product_name, model


def generate_missing_images():
    """为所有缺失图片的产品生成 SVG"""
    count = 0
    for cat, cat_label in categories.items():
        cat_dir = f"{STATIC_DIR}/{cat}"
        os.makedirs(cat_dir, exist_ok=True)
        
        for lang in ['en']:
            content_dir = f"{SITE_DIR}/content/{lang}/products/{cat}"
            if not os.path.isdir(content_dir):
                continue
            
            for fname in os.listdir(content_dir):
                if not fname.endswith('.md') or fname == '_index.md':
                    continue
                
                filepath = f"{content_dir}/{fname}"
                
                # 检查现有的图片字段
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 如果已经有真实图片（非 placeholder），跳过
                img_match = re.search(r'^image:\s*[\'"]?(.+?)[\'"]?\s*$', content, re.MULTILINE)
                if img_match:
                    img_path = img_match.group(1).strip().strip("'").strip('"')
                    if 'placeholder' not in img_path:
                        # 检查实际是否存在（跳过 SVG 检查，因为我们要替换 SVG）
                        actual_file = img_path.replace('/images/products/', f'{STATIC_DIR}/')
                        if os.path.exists(actual_file) and 'svg' not in actual_file:
                            continue  # 已有真实图片
                
                # 获取产品名
                product_name, model = get_product_name_and_model(filepath)
                if not product_name:
                    product_name = fname.replace('.md', '').upper()
                if not model:
                    model = fname.replace('.md', '').upper()
                
                # 生成 SVG 文件名
                base_name = fname.replace('.md', '.svg')
                svg_path = f"{cat_dir}/{base_name}"
                
                if os.path.exists(svg_path):
                    continue  # 已生成
                
                svg_content = generate_svg(product_name, model, cat)
                with open(svg_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                
                print(f"  ✅ {cat}/{base_name} ({product_name})")
                count += 1
    
    print(f"\n生成 {count} 个 SVG 产品图片")


def fix_da007_path():
    """修复 da-007 引用路径（指向 building-materials 而不是 door-accessories）"""
    for lang in ['en', 'zh', 'ar']:
        filepath = f"{SITE_DIR}/content/{lang}/products/door-accessories/da-007.md"
        if not os.path.exists(filepath):
            continue
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content.replace(
            "image: '/images/products/building-materials/angle-bracket-3030.jpg'",
            "image: /images/products/placeholder.svg"
        )
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ 修复 {lang}/da-007 图片路径")


def update_product_images_to_svg():
    """更新所有使用 placeholder.svg 的产品页指向新 SVG"""
    count = 0
    for lang in ['en', 'zh', 'ar']:
        for cat in categories:
            content_dir = f"{SITE_DIR}/content/{lang}/products/{cat}"
            if not os.path.isdir(content_dir):
                continue
            
            for fname in os.listdir(content_dir):
                if not fname.endswith('.md') or fname == '_index.md':
                    continue
                
                filepath = f"{content_dir}/{fname}"
                base = fname.replace('.md', '.svg')
                svg_path = f"/images/products/{cat}/{base}"
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 如果引用的是 placeholder，改为指向 SVG
                new_content = content.replace(
                    "image: /images/products/placeholder.svg",
                    f"image: {svg_path}"
                )
                new_content = new_content.replace(
                    "image: '/images/products/placeholder.svg'",
                    f"image: {svg_path}"
                )
                new_content = new_content.replace(
                    'image: "/images/products/placeholder.svg"',
                    f"image: {svg_path}"
                )
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    count += 1
    
    print(f"\n更新 {count} 个产品页图片引用")


if __name__ == '__main__':
    print("📦 1. 修复 da-007 路径")
    fix_da007_path()
    
    print("\n📦 2. 生成 SVG 产品示意图")
    generate_missing_images()
    
    print("\n📦 3. 更新产品页引用")
    update_product_images_to_svg()
    
    print("\n✅ 图片问题全部修复")
