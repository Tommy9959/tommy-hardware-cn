#!/usr/bin/env python3
"""
Batch fix AR product basic fields (material, finish, moq, etc.) that have wrong data.
"""

import os, re, glob, sys

BASE = '/Users/zhuxiaolei/Sites/hardware-site'

def parse_frontmatter(filepath):
    """Parse YAML frontmatter and body from a Hugo .md file."""
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content, content
    
    fm_text = parts[1]
    body = parts[2]
    
    fm = {}
    current_key = None
    current_list = []
    in_list = False
    
    for line in fm_text.strip().split('\n'):
        stripped = line.strip()
        
        if not stripped:
            continue
        
        if ': ' in stripped and not stripped.startswith('- '):
            if in_list and current_key:
                fm[current_key] = current_list
                in_list = False
                current_list = []
            
            key, val = stripped.split(': ', 1)
            current_key = key.strip()
            
            if val.strip() == '':
                in_list = False
                current_list = []
            else:
                fm[current_key] = val.strip().strip("'\"")
        
        elif stripped.startswith('- '):
            in_list = True
            val = stripped[2:].strip().strip("'\"")
            current_list.append(val)
        
        elif stripped.endswith(':') and not stripped.startswith('- '):
            if in_list and current_key:
                fm[current_key] = current_list
                in_list = False
                current_list = []
            current_key = stripped[:-1].strip()
            fm[current_key] = None
            in_list = False
    
    if in_list and current_key:
        fm[current_key] = current_list
    
    return fm, body, content


def write_frontmatter(filepath, fm, body, original_content):
    """Write back frontmatter + body to file."""
    lines = ['---']
    for key, val in fm.items():
        if isinstance(val, list):
            lines.append(f'{key}:')
            for item in val:
                lines.append(f"  - '{item}'")
        elif val is None:
            continue
        else:
            lines.append(f"{key}: {val}")
    lines.append('---')
    lines.append(body.lstrip('\n'))
    
    new_content = '\n'.join(lines) + '\n'
    if new_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


# Basic field translations for AR
MATERIAL_AR = {
    "Iron Plate + Aluminum Handle": "لوحة حديد + مقبض ألومنيوم",
    "Stainless Steel / Steel / Brass": "فولاذ مقاوم للصدأ / فولاذ / نحاس",
    "Wood / Metal / Plastic": "خشب / معدن / بلاستيك",
    "Zinc Alloy / Aluminum / Stainless Steel": "سبائك الزنك / ألومنيوم / فولاذ مقاوم للصدأ",
    "Zinc Alloy / Aluminum": "سبائك الزنك / ألومنيوم",
    "Aluminum Alloy / Steel": "سبائك ألومنيوم / فولاذ",
    "Aluminum Alloy": "سبائك ألومنيوم",
    "Aluminum Alloy 6063": "سبائك ألومنيوم 6063",
    "Stainless Steel": "فولاذ مقاوم للصدأ",
    "SS304 Stainless Steel": "SS304 فولاذ مقاوم للصدأ",
    "Steel / Stainless Steel": "فولاذ / فولاذ مقاوم للصدأ",
    "Steel + Zinc Alloy": "فولاذ + سبائك الزنك",
    "Steel + Plastic": "فولاذ + بلاستيك",
    "Iron": "حديد",
    "Iron / Galvanized": "حديد / مجلفن",
    "Zinc Alloy + Steel": "سبائك الزنك + فولاذ",
    "Zinc Alloy + Plastic": "سبائك الزنك + بلاستيك",
    "Zinc Alloy": "سبائك الزنك",
    "Brass / Zinc Alloy": "نحاس أصفر / سبائك الزنك",
    "Cold Rolled Steel": "فولاذ مدرفل على البارد",
    "Aluminum + Rubber": "ألومنيوم + مطاط",
    "Rubber + Steel": "مطاط + فولاذ",
    "Magnet + Plastic": "مغناطيس + بلاستيك",
    "Cement + Additives": "أسمنت + إضافات",
    "Cement + Polymers": "أسمنت + بوليمرات",
    "Acrylic Polymer": "بوليمر أكريليك",
    "MS Polymer": "بوليمر MS",
    "PVC + Additives": "PVC + إضافات",
    "Non-woven Fabric": "قماش غير منسوج",
}

FINISH_AR = {
    "AB Antique Bronze": "برونزي عتيق AB",
    "AB / BN/SN / MAE": "AB / BN/SN / MAE",
    "AB / MAE": "AB / MAE",
    "Chrome / Brushed / Matte Black": "كروم / مصقول / أسود غير لامع",
    "Satin / Polished / Zinc Plated": "ساتان / لامع / مطلي بالزنك",
    "Natural / Chrome / Powder Coated": "طبيعي / كروم / مطلي بالمسحوق",
    "Anodized / Powder Coated": "مؤكسد / مطلي بالمسحوق",
    "White / Gray": "أبيض / رمادي",
    "White / Clear": "أبيض / شفاف",
    "White": "أبيض",
    "White / Wood Grain": "أبيض / خشبي",
    "Black / Gray": "أسود / رمادي",
    "Black / Galvanized": "أسود / مجلفن",
    "Silver / White": "فضي / أبيض",
    "Silver / Gray": "فضي / رمادي",
    "Silver / Black": "فضي / أسود",
    "Brass / Chrome": "نحاسي / كروم",
    "Chrome / White": "كروم / أبيض",
    "Chrome / Black": "كروم / أسود",
    "Chrome / Brass": "كروم / نحاسي",
    "Satin / Chrome": "ساتان / كروم",
    "Satin / Chrome / Polished": "ساتان / كروم / مصقول",
    "Nickel / Black": "نيكل / أسود",
    "Nickel / Bronze": "نيكل / برونزي",
    "White / Brown": "أبيض / بني",
    "Galvanized / Painted": "مجلفن / مطلي",
    "Galvanized": "مجلفن",
    "Multiple Colors": "ألوان متعددة",
    "Multiple Finishes Available": "تشطيبات متعددة متاحة",
}

APP_AR = {
    "Residential/Commercial doors": "أبواب سكنية/تجارية",
    "Interior/Exterior Doors, Security Doors": "أبواب داخلية/خارجية، أبواب أمان",
    "All door types": "جميع أنواع الأبواب",
    "Sofas, Chairs, Cabinets, Beds": "أرائك، كراسي، خزائن، أسرّة",
    "Kitchen cabinets, Bathroom vanities": "خزائن مطبخ، خزائن حمام",
    "Drawers, Wardrobes, Sliding doors": "أدراج، خزائن ملابس، أبواب منزلقة",
    "Interior/Exterior doors": "أبواب داخلية/خارجية",
    "Interior doors, Office doors": "أبواب داخلية، أبواب مكاتب",
    "Commercial Doors": "أبواب تجارية",
    "Various applications": "استخدامات متعددة",
    "Wall & Floor Tiling": "بلاط الجدران والأرضيات",
    "Interior Decoration": "ديكور داخلي",
    "Roof & Wall Waterproofing": "عزل أسقف وجدران",
    "Wall Smoothing": "تنعيم الجدران",
    "Multi-surface Bonding": "لصق متعدد الأسطح",
    "Ceiling Decoration": "ديكور السقف",
    "Floor Mount": "تثبيت أرضي",
    "Kitchen Cabinet": "خزانة مطبخ",
    "Cabinet Door": "باب خزانة",
    "Cabinet Door Closing": "إغلاق باب الخزانة",
    "Panel Connection": "توصيل الألواح",
    "Office Desk / Cabinet": "مكتب / خزانة",
    "Security Viewing": "عرض أمني",
    "Additional Security": "أمان إضافي",
    "Sliding/Bi-fold Doors": "أبواب منزلقة/مطوية",
    "Door Safety": "أمان الباب",
    "Sofa / Bed / Table": "أريكة / سرير / طاولة",
    "Construction / Furniture Connection": "توصيل البناء/الأثاث",
    "Pipe Connection / Joining": "توصيل/ربط الأنابيب",
    "Structural Reinforcement / Load-bearing Embedded": "تقوية هيكلية / دفين محمل",
    "Building Embedded Pipe / Conduit": "أنبوب مدفون / قناة",
    "Building Embedded Pipe / Large Conduit": "أنبوب مدفون / قناة كبيرة",
    "Heavy-load Structure / Foundation Reinforcement": "هيكل ثقيل / تقوية أساسات",
    "Door Safety": "أمان الباب",
}

LT_AR = {
    "15-25 days": "15-25 يوم",
    "12-18 days": "12-18 يوم",
    "12-20 days": "12-20 يوم",
    "15-20 days": "15-20 يوم",
    "Samples: 5-7 days, Bulk: 15-25 days": "عينات 5-7 أيام، بالجملة 15-25 يوم",
}

MOQ_AR_TEMPLATE = "{} قطعة"
MOQ_SET_TEMPLATE = "{} مجموعة"
MOQ_METER_TEMPLATE = "{} متر"


def translate_moq(en_val, ar_val):
    """Translate MOQ to Arabic."""
    # Extract number from EN
    nums = re.findall(r'\d+', str(en_val))
    if not nums:
        return ar_val
    
    unit = str(en_val).lower()
    if 'set' in unit or 'sets' in unit:
        return MOQ_SET_TEMPLATE.format(nums[0])
    elif 'meter' in unit:
        return MOQ_METER_TEMPLATE.format(nums[0])
    else:
        return MOQ_QTY_TEMPLATE.format(nums[0])


def main():
    en_files = sorted(glob.glob(os.path.join(BASE, 'content/en/products/*/*.md')))
    en_files = [f for f in en_files if '_index.md' not in f]
    
    fixed = 0
    unchanged = 0
    
    for en_path in en_files:
        rel = os.path.relpath(en_path, os.path.join(BASE, 'content/en'))
        ar_path = os.path.join(BASE, 'content/ar', rel)
        
        if not os.path.exists(ar_path):
            continue
        
        # Parse EN frontmatter
        en_fm, _, _ = parse_frontmatter(en_path)
        if en_fm is None:
            continue
        
        # Parse AR frontmatter
        ar_fm, ar_body, ar_orig = parse_frontmatter(ar_path)
        if ar_fm is None:
            continue
        
        changed = False
        
        # Fix material
        en_mat = en_fm.get('material', '')
        if en_mat and isinstance(en_mat, str) and en_mat.strip():
            ar_mat = ar_fm.get('material', '')
            if ar_mat and isinstance(ar_mat, str) and ar_mat.strip():
                # Check if AR material looks wrong (has generic terms like سبائك الزنك for everything)
                clean_en = en_mat.strip().strip("'\"")
                if clean_en in MATERIAL_AR:
                    correct_ar = MATERIAL_AR[clean_en]
                    if ar_mat.strip() != correct_ar:
                        ar_fm['material'] = correct_ar
                        changed = True
        
        # Fix finish
        en_fin = en_fm.get('finish', '')
        if en_fin and isinstance(en_fin, str) and en_fin.strip():
            clean_en = en_fin.strip().strip("'\"")
            if clean_en in FINISH_AR:
                correct_ar = FINISH_AR[clean_en]
                ar_fin = ar_fm.get('finish', '')
                if ar_fin and isinstance(ar_fin, str) and ar_fin.strip() != correct_ar:
                    ar_fm['finish'] = correct_ar
                    changed = True
        
        # Fix application
        en_app = en_fm.get('application', '')
        if en_app and isinstance(en_app, str) and en_app.strip():
            clean_en = en_app.strip().strip("'\"")
            if clean_en in APP_AR:
                correct_ar = APP_AR[clean_en]
                ar_app = ar_fm.get('application', '')
                if ar_app and isinstance(ar_app, str) and ar_app.strip() != correct_ar:
                    ar_fm['application'] = correct_ar
                    changed = True
        
        # Fix lead_time
        en_lt = en_fm.get('lead_time', '')
        if en_lt and isinstance(en_lt, str) and en_lt.strip():
            clean_en = en_lt.strip().strip("'\"")
            if clean_en in LT_AR:
                correct_ar = LT_AR[clean_en]
                ar_lt = ar_fm.get('lead_time', '')
                if ar_lt and isinstance(ar_lt, str) and ar_lt.strip() != correct_ar:
                    ar_fm['lead_time'] = correct_ar
                    changed = True
        
        # Fix MOQ
        en_moq = en_fm.get('moq', '')
        if en_moq and isinstance(en_moq, str) and en_moq.strip():
            nums = re.findall(r'\d+', en_moq)
            if nums:
                unit = en_moq.lower()
                if 'set' in unit or 'sets' in unit:
                    correct_moq = MOQ_SET_TEMPLATE.format(nums[0])
                elif 'meter' in unit:
                    correct_moq = MOQ_METER_TEMPLATE.format(nums[0])
                else:
                    correct_moq = MOQ_AR_TEMPLATE.format(nums[0])
                
                ar_moq = ar_fm.get('moq', '')
                if ar_moq and isinstance(ar_moq, str) and ar_moq.strip() != correct_moq:
                    ar_fm['moq'] = correct_moq
                    changed = True
        
        # Add missing numeric fields (weight, packing, cartons)
        for field in ['weight', 'packing', 'cartons', 'image']:
            if field in en_fm and field not in ar_fm:
                ar_fm[field] = str(en_fm[field]).strip().strip("'\"")
                changed = True
        
        if changed:
            if write_frontmatter(ar_path, ar_fm, ar_body, ar_orig):
                fixed += 1
                print(f"  FIXED: {rel}")
            else:
                unchanged += 1
        else:
            unchanged += 1
    
    print(f"\n=== AR BASIC FIELD FIX RESULTS ===")
    print(f"Fixed: {fixed}")
    print(f"Already correct / unchanged: {unchanged}")


if __name__ == '__main__':
    main()
