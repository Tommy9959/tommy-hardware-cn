#!/usr/bin/env python3
"""
Batch fix product pages: add missing features/specifications/tags YAML to ZH and AR files.
Translates from EN source using lookup maps.
"""

import os, re, glob, sys

BASE = '/Users/zhuxiaolei/Sites/hardware-site'

# ===== TRANSLATION MAPS =====

FEATURES_ZH = {
    "Factory direct pricing": "工厂直销价格",
    "Iron plate + aluminum handle construction": "铁面板+铝执手结构",
    "Antique bronze finish": "青古铜表面处理",
    "Residential and commercial use": "家用和商用两用",
    "100% quality inspection": "100% 质量检验",
    "Premium quality material": "优质材料",
    "Durable construction": "耐用结构",
    "Custom orders accepted": "接受定制订单",
    "Fast delivery": "快速交货",
    "Easy installation": "安装简便",
    "Premium material construction": "高级材料结构",
    "Corrosion resistant finish": "耐腐蚀表面处理",
    "Smooth operation": "运行顺畅",
    "Factory direct wholesale price": "工厂批发价",
    "High quality materials, durable": "高品质材料、经久耐用",
    "Custom design accepted (OEM/ODM)": "接受定制设计 (OEM/ODM)",
    "Fast delivery 15-25 days": "快速交货 15-25 天",
    "ISO 9001, CE, SGS certified": "ISO 9001、CE、SGS 认证",
    "Fast delivery to Nigeria": "快速发货至尼日利亚",
    "Custom lengths accepted": "接受定制长度",
    "Durable iron construction": "耐用铁质结构",
    "Thicker wall for higher load capacity": "加厚管壁，承载能力更强",
    "Precision-rolled for consistent diameter": "精密轧制，直径一致",
    "Large 25mm bore for heavy cable routing": "大25mm孔径，适用于重型线缆布线",
    "Large 25mm diameter bore": "大25mm直径孔径",
    "Extra-thick 2.5mm wall for maximum load": "超厚2.5mm管壁，最大承载",
    "Premium iron construction": "优质铁质结构",
    "Precision-fit for 16mm and 25mm pipes": "精密适配16mm和25mm管材",
    "Galvanized for corrosion resistance": "镀锌处理，耐腐蚀",
}

FEATURES_AR = {
    "Factory direct pricing": "سعر المصنع المباشر",
    "Iron plate + aluminum handle construction": "هيكل لوحة حديد + مقبض ألومنيوم",
    "Antique bronze finish": "تشطيب برونزي عتيق",
    "Residential and commercial use": "للاستخدام السكني والتجاري",
    "100% quality inspection": "فحص جودة 100%",
    "Premium quality material": "مواد عالية الجودة",
    "Durable construction": "بناء متين",
    "Custom orders accepted": "قبول الطلبات المخصصة",
    "Fast delivery": "تسليم سريع",
    "Easy installation": "سهولة التركيب",
    "Premium material construction": "بناء من مواد متميزة",
    "Corrosion resistant finish": "تشطيب مقاوم للصدأ",
    "Smooth operation": "تشغيل سلس",
    "Factory direct wholesale price": "سعر جملة من المصنع",
    "High quality materials, durable": "مواد عالية الجودة، متينة",
    "Custom design accepted (OEM/ODM)": "قبول التصميم المخصص (OEM/ODM)",
    "Fast delivery 15-25 days": "تسليم سريع 15-25 يوم",
    "ISO 9001, CE, SGS certified": "معتمد ISO 9001, CE, SGS",
    "Fast delivery to Nigeria": "توصيل سريع إلى نيجيريا",
    "Custom lengths accepted": "أطوال مخصصة مقبولة",
    "Durable iron construction": "بناء حديدي متين",
    "Thicker wall for higher load capacity": "جدار أكثر سمكًا لسعة تحميل أعلى",
    "Precision-rolled for consistent diameter": "درفلة دقيقة لقطر ثابت",
    "Large 25mm bore for heavy cable routing": "فتحة 25 مم كبيرة لتمديد الكابلات الثقيلة",
    "Large 25mm diameter bore": "فتحة قطر 25 مم كبيرة",
    "Extra-thick 2.5mm wall for maximum load": "جدار فائق السمك 2.5 مم لأقصى حمولة",
    "Premium iron construction": "بناء حديدي ممتاز",
    "Precision-fit for 16mm and 25mm pipes": "ملاءمة دقيقة لأنابيب 16 مم و 25 مم",
    "Galvanized for corrosion resistance": "مجلفن لمقاومة التآكل",
}

SPECS_ZH = {
    "Material: Iron Plate + Aluminum Handle": "材质：铁面板 + 铝执手",
    "Material: Stainless Steel / Steel / Brass": "材质：不锈钢 / 钢 / 铜",
    "Material: Wood / Metal / Plastic": "材质：木材 / 金属 / 塑料",
    "Material: Zinc Alloy / Aluminum / Stainless Steel": "材质：锌合金 / 铝合金 / 不锈钢",
    "Material: Premium material": "材质：优质材料",
    "Material: Aluminum Alloy / Steel": "材质：铝合金 / 钢",
    "Material: High Quality Material": "材质：高品质材料",
    "Material: Iron": "材质：铁",
    "Material: Cement + Additives": "材质：水泥 + 添加剂",
    "Material: Non-woven Fabric": "材质：无纺布",
    "Material: Acrylic Polymer": "材质：丙烯酸聚合物",
    "Material: Cement + Polymers": "材质：水泥 + 聚合物",
    "Material: MS Polymer": "材质：MS 聚合物",
    "Material: PVC + Additives": "材质：PVC + 添加剂",
    "Material: Rubber + Steel": "材质：橡胶 + 钢",
    "Material: Zinc Alloy + Steel": "材质：锌合金 + 钢",
    "Material: Brass / Zinc Alloy": "材质：黄铜 / 锌合金",
    "Material: Steel + Zinc Alloy": "材质：钢 + 锌合金",
    "Material: Stainless Steel": "材质：不锈钢",
    "Material: Aluminum + Rubber": "材质：铝合金 + 橡胶",
    "Material: Steel / Stainless Steel": "材质：钢 / 不锈钢",
    "Material: SS304 Stainless Steel": "材质：SS304 不锈钢",
    "Material: Aluminum Alloy 6063": "材质：6063 铝合金",
    "Material: Aluminum Alloy": "材质：铝合金",
    "Material: Zinc Alloy + Plastic": "材质：锌合金 + 塑料",
    "Material: Steel + Plastic": "材质：钢 + 塑料",
    "Material: Cold Rolled Steel": "材质：冷轧钢",
    "Material: Zinc Alloy": "材质：锌合金",
    "Material: Magnet + Plastic": "材质：磁铁 + 塑料",
    "Material: Iron / Galvanized": "材质：铁 / 镀锌",
    
    "Finish: AB Antique Bronze": "表面处理：AB 青古铜",
    "Finish: Various finishes available": "表面处理：多种可选",
    "Finish: Standard finish": "表面处理：标准处理",
    "Finish: Anodized / Powder Coated": "表面处理：阳极氧化 / 喷塑",
    "Finish: Chrome / Brushed / Matte Black": "表面处理：镀铬 / 拉丝 / 哑黑",
    "Finish: Satin / Polished / Zinc Plated": "表面处理：缎面 / 抛光 / 镀锌",
    "Finish: Natural / Chrome / Powder Coated": "表面处理：原木色 / 镀铬 / 喷塑",
    "Finish: AB / BN/SN / MAE": "表面处理：AB / BN/SN / MAE",
    "Finish: AB / MAE": "表面处理：AB / MAE",
    "Finish: White / Gray": "表面处理：白色 / 灰色",
    "Finish: Multiple Colors": "表面处理：多种颜色",
    "Finish: White / Clear": "表面处理：白色 / 透明",
    "Finish: White": "表面处理：白色",
    "Finish: White / Wood Grain": "表面处理：白色 / 木纹",
    "Finish: Black / Gray": "表面处理：黑色 / 灰色",
    "Finish: Silver / White": "表面处理：银色 / 白色",
    "Finish: Brass / Chrome": "表面处理：黄铜色 / 镀铬",
    "Finish: Chrome / White": "表面处理：镀铬 / 白色",
    "Finish: Satin / Chrome": "表面处理：缎面 / 镀铬",
    "Finish: Silver / Gray": "表面处理：银色 / 灰色",
    "Finish: Galvanized / Painted": "表面处理：镀锌 / 喷漆",
    "Finish: Satin / Chrome / Polished": "表面处理：缎面 / 镀铬 / 抛光",
    "Finish: Silver / Black": "表面处理：银色 / 黑色",
    "Finish: Nickel / Black": "表面处理：镍色 / 黑色",
    "Finish: Chrome / Black": "表面处理：镀铬 / 黑色",
    "Finish: Nickel / Bronze": "表面处理：镍色 / 青铜色",
    "Finish: Chrome / Brass": "表面处理：镀铬 / 黄铜色",
    "Finish: White / Brown": "表面处理：白色 / 棕色",
    "Finish: Galvanized": "表面处理：镀锌",
    "Finish: Black / Galvanized": "表面处理：黑色 / 镀锌",
    "Finish: Multiple Finishes Available": "表面处理：多种可选",
    
    "Application: Residential/Commercial doors": "用途：家用/商用门",
    "Application: Interior/Exterior Doors, Security Doors": "用途：室内/室外门、防盗门",
    "Application: All door types": "用途：所有门类型",
    "Application: Sofas, Chairs, Cabinets, Beds": "用途：沙发、椅子、橱柜、床",
    "Application: Kitchen cabinets, Bathroom vanities": "用途：厨房橱柜、浴室柜",
    "Application: Various applications": "用途：多种用途",
    "Application: Drawers, Wardrobes, Sliding doors": "用途：抽屉、衣柜、推拉门",
    "Application: Interior/Exterior doors": "用途：室内/室外门",
    "Application: Structural Reinforcement / Load-bearing Embedded": "用途：结构加固 / 承重预埋",
    "Application: Wall & Floor Tiling": "用途：墙面和地面瓷砖",
    "Application: Interior Decoration": "用途：室内装饰",
    "Application: Roof & Wall Waterproofing": "用途：屋顶和墙面防水",
    "Application: Wall Smoothing": "用途：墙面找平",
    "Application: Multi-surface Bonding": "用途：多表面粘接",
    "Application: Ceiling Decoration": "用途：天花板装饰",
    "Application: Floor Mount": "用途：地面安装",
    "Application: Commercial Doors": "用途：商用门",
    "Application: Security Viewing": "用途：安全观察",
    "Application: Additional Security": "用途：额外安全防护",
    "Application: Sliding/Bi-fold Doors": "用途：推拉/折叠门",
    "Application: Door Safety": "用途：门安全防护",
    "Application: Construction / Furniture Connection": "用途：建筑/家具连接",
    "Application: Interior doors, Office doors": "用途：室内门、办公室门",
    "Application: Kitchen Cabinet": "用途：橱柜",
    "Application: Panel Connection": "用途：面板连接",
    "Application: Sofa / Bed / Table": "用途：沙发 / 床 / 桌子",
    "Application: Cabinet Door": "用途：柜门",
    "Application: Office Desk / Cabinet": "用途：办公桌 / 柜",
    "Application: Cabinet Door Closing": "用途：柜门闭合",
    "Application: Building Embedded Pipe / Conduit": "用途：建筑预埋管 / 线管",
    "Application: Building Embedded Pipe / Large Conduit": "用途：建筑预埋管 / 大型线管",
    "Application: Heavy-load Structure / Foundation Reinforcement": "用途：重载结构 / 基础加固",
    "Application: Pipe Connection / Joining": "用途：管道连接/对接",
    
    "MOQ: 400 pcs": "最小起订量：400 个",
    "MOQ: 500 pcs": "最小起订量：500 个",
    "MOQ: 1000 pcs": "最小起订量：1000 个",
    "MOQ: 100 sets": "最小起订量：100 套",
    "MOQ: 500 meters": "最小起订量：500 米",
    "MOQ: 2000 pcs": "最小起订量：2000 个",
    
    "Lead Time: 15-25 days": "交货期：15-25 天",
    "Lead Time: 12-18 days": "交货期：12-18 天",
    "Lead Time: 12-20 days": "交货期：12-20 天",
    "Lead Time: Samples: 5-7 days, Bulk: 15-25 days": "交货期：样品 5-7 天，大货 15-25 天",
    "Lead Time: 15-20 days": "交货期：15-20 天",
    
    "Standard Lengths: 3m / 6m": "标准长度：3米 / 6米",
    "Outer Diameter: 25mm": "外径：25mm",
    "Outer Diameter: 16mm": "外径：16mm",
    "Wall Thickness: 1.5mm": "壁厚：1.5mm",
    "Wall Thickness: 2.0mm": "壁厚：2.0mm",
    "Wall Thickness: 2.5mm": "壁厚：2.5mm",
    "Compatible Sizes: 16mm and 25mm casing pipes": "适配尺寸：16mm 和 25mm 预埋管",
}

SPECS_AR = {
    "Material: Iron Plate + Aluminum Handle": "المادة: لوحة حديد + مقبض ألومنيوم",
    "Material: Stainless Steel / Steel / Brass": "المادة: فولاذ مقاوم / فولاذ / نحاس",
    "Material: Wood / Metal / Plastic": "المادة: خشب / معدن / بلاستيك",
    "Material: Zinc Alloy / Aluminum / Stainless Steel": "المادة: سبائك الزنك / ألومنيوم / فولاذ مقاوم",
    "Material: Premium material": "المادة: مواد ممتازة",
    "Material: Aluminum Alloy / Steel": "المادة: سبائك ألومنيوم / فولاذ",
    "Material: High Quality Material": "المادة: مواد عالية الجودة",
    "Material: Iron": "المادة: حديد",
    "Material: Cement + Additives": "المادة: أسمنت + إضافات",
    "Material: Non-woven Fabric": "المادة: قماش غير منسوج",
    "Material: Acrylic Polymer": "المادة: بوليمر أكريليك",
    "Material: Cement + Polymers": "المادة: أسمنت + بوليمرات",
    "Material: MS Polymer": "المادة: بوليمر MS",
    "Material: PVC + Additives": "المادة: PVC + إضافات",
    "Material: Rubber + Steel": "المادة: مطاط + فولاذ",
    "Material: Zinc Alloy + Steel": "المادة: سبائك الزنك + فولاذ",
    "Material: Brass / Zinc Alloy": "المادة: نحاس أصفر / سبائك الزنك",
    "Material: Steel + Zinc Alloy": "المادة: فولاذ + سبائك الزنك",
    "Material: Stainless Steel": "المادة: فولاذ مقاوم للصدأ",
    "Material: Aluminum + Rubber": "المادة: ألومنيوم + مطاط",
    "Material: Steel / Stainless Steel": "المادة: فولاذ / فولاذ مقاوم للصدأ",
    "Material: SS304 Stainless Steel": "المادة: SS304 فولاذ مقاوم للصدأ",
    "Material: Aluminum Alloy 6063": "المادة: سبائك ألومنيوم 6063",
    "Material: Aluminum Alloy": "المادة: سبائك ألومنيوم",
    "Material: Zinc Alloy + Plastic": "المادة: سبائك الزنك + بلاستيك",
    "Material: Steel + Plastic": "المادة: فولاذ + بلاستيك",
    "Material: Cold Rolled Steel": "المادة: فولاذ مدرفل على البارد",
    "Material: Zinc Alloy": "المادة: سبائك الزنك",
    "Material: Magnet + Plastic": "المادة: مغناطيس + بلاستيك",
    "Material: Iron / Galvanized": "المادة: حديد / مجلفن",
    
    "Finish: AB Antique Bronze": "التشطيب: برونزي عتيق AB",
    "Finish: Various finishes available": "التشطيب: تشطيبات متعددة متاحة",
    "Finish: Standard finish": "التشطيب: تشطيب قياسي",
    "Finish: Anodized / Powder Coated": "التشطيب: مؤكسد / مطلي بالمسحوق",
    "Finish: Chrome / Brushed / Matte Black": "التشطيب: كروم / مصقول / أسود غير لامع",
    "Finish: Satin / Polished / Zinc Plated": "التشطيب: ساتان / لامع / مطلي بالزنك",
    "Finish: Natural / Chrome / Powder Coated": "التشطيب: طبيعي / كروم / مطلي بالمسحوق",
    "Finish: AB / BN/SN / MAE": "التشطيب: AB / BN/SN / MAE",
    "Finish: AB / MAE": "التشطيب: AB / MAE",
    "Finish: White / Gray": "التشطيب: أبيض / رمادي",
    "Finish: Multiple Colors": "التشطيب: ألوان متعددة",
    "Finish: White / Clear": "التشطيب: أبيض / شفاف",
    "Finish: White": "التشطيب: أبيض",
    "Finish: White / Wood Grain": "التشطيب: أبيض / خشبي",
    "Finish: Black / Gray": "التشطيب: أسود / رمادي",
    "Finish: Silver / White": "التشطيب: فضي / أبيض",
    "Finish: Brass / Chrome": "التشطيب: نحاسي / كروم",
    "Finish: Chrome / White": "التشطيب: كروم / أبيض",
    "Finish: Satin / Chrome": "التشطيب: ساتان / كروم",
    "Finish: Silver / Gray": "التشطيب: فضي / رمادي",
    "Finish: Galvanized / Painted": "التشطيب: مجلفن / مطلي",
    "Finish: Satin / Chrome / Polished": "التشطيب: ساتان / كروم / مصقول",
    "Finish: Silver / Black": "التشطيب: فضي / أسود",
    "Finish: Nickel / Black": "التشطيب: نيكل / أسود",
    "Finish: Chrome / Black": "التشطيب: كروم / أسود",
    "Finish: Nickel / Bronze": "التشطيب: نيكل / برونزي",
    "Finish: Chrome / Brass": "التشطيب: كروم / نحاسي",
    "Finish: White / Brown": "التشطيب: أبيض / بني",
    "Finish: Galvanized": "التشطيب: مجلفن",
    "Finish: Black / Galvanized": "التشطيب: أسود / مجلفن",
    "Finish: Multiple Finishes Available": "التشطيب: تشطيبات متعددة متاحة",
    
    "Application: Residential/Commercial doors": "الاستخدام: أبواب سكنية/تجارية",
    "Application: Interior/Exterior Doors, Security Doors": "الاستخدام: أبواب داخلية/خارجية، أبواب أمان",
    "Application: All door types": "الاستخدام: جميع أنواع الأبواب",
    "Application: Sofas, Chairs, Cabinets, Beds": "الاستخدام: أرائك، كراسي، خزائن، أسرّة",
    "Application: Kitchen cabinets, Bathroom vanities": "الاستخدام: خزائن مطبخ، خزائن حمام",
    "Application: Various applications": "الاستخدام: استخدامات متعددة",
    "Application: Drawers, Wardrobes, Sliding doors": "الاستخدام: أدراج، خزائن ملابس، أبواب منزلقة",
    "Application: Interior/Exterior doors": "الاستخدام: أبواب داخلية/خارجية",
    "Application: Structural Reinforcement / Load-bearing Embedded": "الاستخدام: تقوية هيكلية / دفين محمل",
    "Application: Wall & Floor Tiling": "الاستخدام: بلاط الجدران والأرضيات",
    "Application: Interior Decoration": "الاستخدام: ديكور داخلي",
    "Application: Roof & Wall Waterproofing": "الاستخدام: عزل أسقف وجدران",
    "Application: Wall Smoothing": "الاستخدام: تنعيم الجدران",
    "Application: Multi-surface Bonding": "الاستخدام: لصق متعدد الأسطح",
    "Application: Ceiling Decoration": "الاستخدام: ديكور السقف",
    "Application: Floor Mount": "الاستخدام: تثبيت أرضي",
    "Application: Commercial Doors": "الاستخدام: أبواب تجارية",
    "Application: Security Viewing": "الاستخدام: عرض أمني",
    "Application: Additional Security": "الاستخدام: أمان إضافي",
    "Application: Sliding/Bi-fold Doors": "الاستخدام: أبواب منزلقة/مطوية",
    "Application: Door Safety": "الاستخدام: أمان الباب",
    "Application: Construction / Furniture Connection": "الاستخدام: توصيل البناء/الأثاث",
    "Application: Interior doors, Office doors": "الاستخدام: أبواب داخلية، أبواب مكاتب",
    "Application: Kitchen Cabinet": "الاستخدام: خزانة مطبخ",
    "Application: Panel Connection": "الاستخدام: توصيل الألواح",
    "Application: Sofa / Bed / Table": "الاستخدام: أريكة / سرير / طاولة",
    "Application: Cabinet Door": "الاستخدام: باب خزانة",
    "Application: Office Desk / Cabinet": "الاستخدام: مكتب / خزانة",
    "Application: Cabinet Door Closing": "الاستخدام: إغلاق باب الخزانة",
    "Application: Building Embedded Pipe / Conduit": "الاستخدام: أنبوب مدفون / قناة",
    "Application: Building Embedded Pipe / Large Conduit": "الاستخدام: أنبوب مدفون / قناة كبيرة",
    "Application: Heavy-load Structure / Foundation Reinforcement": "الاستخدام: هيكل ثقيل / تقوية أساسات",
    "Application: Pipe Connection / Joining": "الاستخدام: توصيل/ربط الأنابيب",
    
    "MOQ: 400 pcs": "الحد الأدنى للطلب: 400 قطعة",
    "MOQ: 500 pcs": "الحد الأدنى للطلب: 500 قطعة",
    "MOQ: 1000 pcs": "الحد الأدنى للطلب: 1000 قطعة",
    "MOQ: 100 sets": "الحد الأدنى للطلب: 100 مجموعة",
    "MOQ: 500 meters": "الحد الأدنى للطلب: 500 متر",
    "MOQ: 2000 pcs": "الحد الأدنى للطلب: 2000 قطعة",
    
    "Lead Time: 15-25 days": "المهلة: 15-25 يوم",
    "Lead Time: 12-18 days": "المهلة: 12-18 يوم",
    "Lead Time: 12-20 days": "المهلة: 12-20 يوم",
    "Lead Time: Samples: 5-7 days, Bulk: 15-25 days": "المهلة: عينات 5-7 أيام، بالجملة 15-25 يوم",
    "Lead Time: 15-20 days": "المهلة: 15-20 يوم",
    
    "Standard Lengths: 3m / 6m": "الأطوال القياسية: 3م / 6م",
    "Outer Diameter: 25mm": "القطر الخارجي: 25 مم",
    "Outer Diameter: 16mm": "القطر الخارجي: 16 مم",
    "Wall Thickness: 1.5mm": "سماكة الجدار: 1.5 مم",
    "Wall Thickness: 2.0mm": "سماكة الجدار: 2.0 مم",
    "Wall Thickness: 2.5mm": "سماكة الجدار: 2.5 مم",
    "Compatible Sizes: 16mm and 25mm casing pipes": "الأحجام المتوافقة: أنابيب تغليف 16 مم و 25 مم",
}

TAGS_ZH = {
    "SOLA Hardware": "SOLA Hardware",
    "door lock": "门锁",
    "door lock wholesale": "门锁批发",
    "iron plate door lock": "铁面板门锁",
    "door lock Nigeria": "尼日利亚门锁",
    "door lock Africa": "非洲门锁",
    "wholesale padlock": "挂锁批发",
    "padlock Nigeria": "尼日利亚挂锁",
    "padlock Africa": "非洲挂锁",
    "China padlock factory": "中国挂锁工厂",
    "door accessory": "门配件",
    "door stopper": "门吸",
    "door closer": "闭门器",
    "door viewer": "猫眼",
    "door hardware": "门五金",
    "building material": "建筑材料",
    "tile adhesive": "瓷砖胶",
    "wallpaper": "墙纸",
    "waterproof coating": "防水涂料",
    "construction chemical": "建筑化工",
    "cabinet hardware": "橱柜五金",
    "cabinet handle": "橱柜拉手",
    "cabinet knob": "橱柜旋钮",
    "cabinet hardware wholesale": "橱柜五金批发",
    "kitchen hardware": "厨房五金",
    "door handle": "门把手",
    "door handle wholesale": "门把手批发",
    "stainless steel door handle": "不锈钢门把手",
    "door handle Nigeria": "尼日利亚门把手",
    "door hardware Africa": "非洲门五金",
    "door hinge": "门铰链",
    "door hinge wholesale": "门铰链批发",
    "stainless steel hinge": "不锈钢铰链",
    "door hinge Nigeria": "尼日利亚门铰链",
    "hinge Africa": "非洲铰链",
    "furniture fitting": "家具配件",
    "furniture handle": "家具拉手",
    "furniture connector": "家具连接件",
    "furniture hardware": "家具五金",
    "sliding track": "推拉轨道",
    "drawer slide": "抽屉导轨",
    "sliding track wholesale": "推拉轨道批发",
    "wardrobe track": "衣柜轨道",
    "sliding door hardware": "推拉门五金",
    "sofa leg": "沙发脚",
    "furniture leg": "家具脚",
    "sofa leg wholesale": "沙发脚批发",
    "furniture foot": "家具脚垫",
    "sofa leg Nigeria": "尼日利亚沙发脚",
    "iron casing pipe": "铁预埋管",
    "iron pipe wholesale": "铁管批发",
    "iron padlock": "铁挂锁",
    "building embedded pipe": "建筑预埋管",
    "structural reinforcement": "结构加固",
    "load-bearing pipe": "承重管",
    "waterproof padlock": "防水挂锁",
    "casing pipe 16mm": "16mm预埋管",
    "conduit pipe": "线管",
    "casing pipe 16mm heavy": "16mm重型预埋管",
    "casing pipe 25mm": "25mm预埋管",
    "large conduit": "大型线管",
    "casing pipe 25mm heavy": "25mm重型预埋管",
    "casing pipe 25mm extra heavy": "25mm超重型预埋管",
    "foundation reinforcement": "基础加固",
    "heavy structural pipe": "重型结构管",
    "iron casing pipe connector": "铁预埋管接头",
    "pipe connector wholesale": "管接头批发",
    "casing pipe fitting": "预埋管配件",
    "pipe joint": "管接头",
    "galvanized connector": "镀锌接头",
    "GTK padlock": "GTK挂锁",
    "heavy duty padlock": "重型挂锁",
    "HHL padlock": "HHL挂锁",
    "HLV padlock": "HLV挂锁",
    "LTN padlock": "LTN挂锁",
    "solid brass padlock": "全铜挂锁",
    "SF padlock": "SF挂锁",
    "SFN padlock": "SFN挂锁",
    "YGTK padlock": "YGTK挂锁",
    "YJN padlock": "YJN挂锁",
}

TAGS_AR = {
    "SOLA Hardware": "SOLA Hardware",
    "door lock": "قفل باب",
    "door lock wholesale": "قفل باب جملة",
    "iron plate door lock": "قفل باب لوحة حديد",
    "door lock Nigeria": "قفل باب نيجيريا",
    "door lock Africa": "قفل باب أفريقيا",
    "wholesale padlock": "قفل جملة",
    "padlock Nigeria": "قفل نيجيريا",
    "padlock Africa": "قفل أفريقيا",
    "China padlock factory": "مصنع أقفال الصين",
    "door accessory": "اكسسوارات باب",
    "door stopper": "مصد باب",
    "door closer": "غالق باب",
    "door viewer": "عين باب",
    "door hardware": "مستلزمات باب",
    "building material": "مواد بناء",
    "tile adhesive": "لاصق بلاط",
    "wallpaper": "ورق جدران",
    "waterproof coating": "طلاء عازل للماء",
    "construction chemical": "كيماويات بناء",
    "cabinet hardware": "مستلزمات خزائن",
    "cabinet handle": "مقبض خزانة",
    "cabinet knob": "مقبض خزانة دائري",
    "cabinet hardware wholesale": "مستلزمات خزائن جملة",
    "kitchen hardware": "مستلزمات مطبخ",
    "door handle": "مقبض باب",
    "door handle wholesale": "مقبض باب جملة",
    "stainless steel door handle": "مقبض باب ستانلس ستيل",
    "door handle Nigeria": "مقبض باب نيجيريا",
    "door hardware Africa": "مستلزمات باب أفريقيا",
    "door hinge": "مفصل باب",
    "door hinge wholesale": "مفصل باب جملة",
    "stainless steel hinge": "مفصل ستانلس ستيل",
    "door hinge Nigeria": "مفصل باب نيجيريا",
    "hinge Africa": "مفصل أفريقيا",
    "furniture fitting": "تجهيزات أثاث",
    "furniture handle": "مقبض أثاث",
    "furniture connector": "موصل أثاث",
    "furniture hardware": "مستلزمات أثاث",
    "sliding track": "مسار منزلق",
    "drawer slide": "منزلق درج",
    "sliding track wholesale": "مسار منزلق جملة",
    "wardrobe track": "مسار خزانة ملابس",
    "sliding door hardware": "مستلزمات باب منزلق",
    "sofa leg": "رجل أريكة",
    "furniture leg": "رجل أثاث",
    "sofa leg wholesale": "رجل أريكة جملة",
    "furniture foot": "قدم أثاث",
    "sofa leg Nigeria": "رجل أريكة نيجيريا",
    "iron casing pipe": "أنبوب تغليف حديد",
    "iron pipe wholesale": "أنبوب حديد جملة",
    "iron padlock": "قفل حديد",
    "building embedded pipe": "أنبوب مدفون في البناء",
    "structural reinforcement": "تقوية هيكلية",
    "load-bearing pipe": "أنبوب تحميل",
    "waterproof padlock": "قفل مقاوم للماء",
    "casing pipe 16mm": "أنبوب تغليف 16 مم",
    "conduit pipe": "أنبوب قناة",
    "casing pipe 16mm heavy": "أنبوب تغليف 16 مم ثقيل",
    "casing pipe 25mm": "أنبوب تغليف 25 مم",
    "large conduit": "قناة كبيرة",
    "casing pipe 25mm heavy": "أنبوب تغليف 25 مم ثقيل",
    "casing pipe 25mm extra heavy": "أنبوب تغليف 25 مم ثقيل جداً",
    "foundation reinforcement": "تقوية أساسات",
    "heavy structural pipe": "أنبوب هيكلي ثقيل",
    "iron casing pipe connector": "موصل أنبوب تغليف حديد",
    "pipe connector wholesale": "موصل أنابيب جملة",
    "casing pipe fitting": "تركيبات أنبوب تغليف",
    "pipe joint": "وصلة أنابيب",
    "galvanized connector": "موصل مجلفن",
    "GTK padlock": "قفل GTK",
    "heavy duty padlock": "قفل ثقيل",
    "HHL padlock": "قفل HHL",
    "HLV padlock": "قفل HLV",
    "LTN padlock": "قفل LTN",
    "solid brass padlock": "قفل نحاس صلب",
    "SF padlock": "قفل SF",
    "SFN padlock": "قفل SFN",
    "YGTK padlock": "قفل YGTK",
    "YJN padlock": "قفل YJN",
}


def parse_frontmatter(filepath):
    """Parse YAML frontmatter and body from a Hugo .md file."""
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    
    # Find frontmatter boundaries
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content
    
    fm_text = parts[1]
    body = parts[2]
    
    # Parse YAML-like lines (simple parser for this format)
    fm = {}
    current_key = None
    current_list = []
    in_list = False
    
    for line in fm_text.strip().split('\n'):
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            continue
        
        # New key-value
        if ': ' in stripped and not stripped.startswith('- '):
            # Save previous list if any
            if in_list and current_key:
                fm[current_key] = current_list
                in_list = False
                current_list = []
            
            key, val = stripped.split(': ', 1)
            current_key = key.strip()
            
            # Check if next lines are a list
            if val.strip() == '':
                in_list = False
                current_list = []
            else:
                fm[current_key] = val.strip().strip("'\"")
        
        # List item (continuation of a YAML array)
        elif stripped.startswith('- '):
            in_list = True
            val = stripped[2:].strip().strip("'\"")
            current_list.append(val)
        
        # Key with no value (next lines might be a list)
        elif stripped.endswith(':') and not stripped.startswith('- '):
            if in_list and current_key:
                fm[current_key] = current_list
                in_list = False
                current_list = []
            current_key = stripped[:-1].strip()
            fm[current_key] = None  # placeholder for list
            in_list = False
    
    # Save last list
    if in_list and current_key:
        fm[current_key] = current_list
    
    return fm, body


def write_frontmatter(filepath, fm, body, original_content):
    """Write back frontmatter + body to file."""
    lines = ['---']
    for key, val in fm.items():
        if isinstance(val, list):
            lines.append(f'{key}:')
            for item in val:
                lines.append(f"  - '{item}'")
        elif val is None:
            # Skip None values (they mean the key was empty/unset)
            continue
        else:
            lines.append(f"{key}: {val}")
    lines.append('---')
    lines.append(body.lstrip('\n'))
    
    new_content = '\n'.join(lines) + '\n'
    
    # Only write if different
    if new_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def translate_list(items, translation_map):
    """Translate a list of items using a map. Returns None if all items are already in map."""
    result = []
    for item in items:
        if item in translation_map:
            result.append(translation_map[item])
        else:
            result.append(item)  # keep original as fallback
    return result if result else None


def is_missing_list(fm, key):
    """Check if a key is missing from frontmatter."""
    if key not in fm:
        return True
    if fm[key] is None:
        return True
    if isinstance(fm[key], list) and len(fm[key]) == 0:
        return True
    return False


def main():
    en_files = sorted(glob.glob(os.path.join(BASE, 'content/en/products/*/*.md')))
    en_files = [f for f in en_files if '_index.md' not in f]
    
    total = len(en_files)
    updated_zh = 0
    updated_ar = 0
    skipped_zh = 0
    skipped_ar = 0
    
    for i, en_path in enumerate(en_files, 1):
        # Get relative path
        rel = os.path.relpath(en_path, os.path.join(BASE, 'content/en'))
        
        # Corresponding ZH and AR paths
        zh_path = os.path.join(BASE, 'content/zh', rel)
        ar_path = os.path.join(BASE, 'content/ar', rel)
        
        if not os.path.exists(zh_path):
            print(f"  WARN: ZH file missing: {rel}")
            continue
        if not os.path.exists(ar_path):
            print(f"  WARN: AR file missing: {rel}")
            continue
        
        # Parse EN
        en_fm, _ = parse_frontmatter(en_path)
        if en_fm is None:
            print(f"  WARN: Cannot parse EN: {rel}")
            continue
        
        # Check what to add
        en_features = en_fm.get('features', [])
        en_specs = en_fm.get('specifications', [])
        en_tags = en_fm.get('tags', [])
        
        if not isinstance(en_features, list):
            en_features = []
        if not isinstance(en_specs, list):
            en_specs = []
        if not isinstance(en_tags, list):
            en_tags = []
        
        if not (en_features or en_specs or en_tags):
            continue  # EN also has nothing, skip
        
        # --- Process ZH ---
        with open(zh_path, encoding='utf-8') as f:
            zh_content = f.read()
        zh_fm, zh_body = parse_frontmatter(zh_path)
        
        if zh_fm is not None:
            changed = False
            
            if is_missing_list(zh_fm, 'features') and en_features:
                translated = translate_list(en_features, FEATURES_ZH)
                if translated:
                    zh_fm['features'] = translated
                    changed = True
            
            if is_missing_list(zh_fm, 'specifications') and en_specs:
                translated = translate_list(en_specs, SPECS_ZH)
                if translated:
                    zh_fm['specifications'] = translated
                    changed = True
            
            if is_missing_list(zh_fm, 'tags') and en_tags:
                translated = translate_list(en_tags, TAGS_ZH)
                if translated:
                    zh_fm['tags'] = translated
                    changed = True
            
            if changed:
                if write_frontmatter(zh_path, zh_fm, zh_body, zh_content):
                    updated_zh += 1
                else:
                    skipped_zh += 1
            else:
                skipped_zh += 1
        else:
            skipped_zh += 1
        
        # --- Process AR ---
        with open(ar_path, encoding='utf-8') as f:
            ar_content = f.read()
        ar_fm, ar_body = parse_frontmatter(ar_path)
        
        if ar_fm is not None:
            changed = False
            
            # Fix wrong field values in AR by replacing from EN
            # Check and fix basic fields if they look wrong
            for field in ['material', 'finish', 'application', 'moq', 'lead_time']:
                if field in en_fm and field in ar_fm:
                    en_val = str(en_fm[field]).strip()
                    ar_val = str(ar_fm[field]).strip()
                    # If AR has a generic/wrong value that doesn't match EN, flag.
                    # We'll rely on the specs being added instead, since they contain
                    # the detailed Material/Finish/Application info.
            
            if is_missing_list(ar_fm, 'features') and en_features:
                translated = translate_list(en_features, FEATURES_AR)
                if translated:
                    ar_fm['features'] = translated
                    changed = True
            
            if is_missing_list(ar_fm, 'specifications') and en_specs:
                translated = translate_list(en_specs, SPECS_AR)
                if translated:
                    ar_fm['specifications'] = translated
                    changed = True
            
            if is_missing_list(ar_fm, 'tags') and en_tags:
                translated = translate_list(en_tags, TAGS_AR)
                if translated:
                    ar_fm['tags'] = translated
                    changed = True
            
            if changed:
                if write_frontmatter(ar_path, ar_fm, ar_body, ar_content):
                    updated_ar += 1
                else:
                    skipped_ar += 1
            else:
                skipped_ar += 1
        else:
            skipped_ar += 1
        
        # Progress
        if i % 20 == 0 or i == total:
            print(f"  Progress: {i}/{total} products...")
    
    print(f"\n=== RESULTS ===")
    print(f"Total products: {total}")
    print(f"ZH: {updated_zh} updated, {skipped_zh} skipped (already had data)")
    print(f"AR: {updated_ar} updated, {skipped_ar} skipped (already had data)")


if __name__ == '__main__':
    main()
