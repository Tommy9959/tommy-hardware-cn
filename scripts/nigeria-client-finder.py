#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌍 尼日利亚客户开发自动化脚本（邮件版）
功能：搜索客户 + 收集信息 + 导出 Excel
更新时间：2026-04-10

定时任务：工作日 16:00 自动运行
"""

import csv
import json
import time
import re
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# ============ 配置区域 ============

CONFIG = {
    # 行业关键词（中英文）
    'product_keywords': [
        'door lock', 'door handle', 'cabinet hinge', 'drawer slide', 'furniture hardware',
        'edge banding', 'furniture glue', 'cabinet pull', 'hinge', 'furniture accessories',
        '门锁', '门把手', '铰链', '导轨', '家具五金', '封边条', '家具配件'
    ],
    
    # 客户类型关键词
    'buyer_types': [
        'importer', 'wholesaler', 'distributor', 'dealer', 'trading company',
        'building materials', 'hardware store', 'construction supplier',
        '进口商', '批发商', '经销商'
    ],
    
    # 目标市场
    'target_country': 'Nigeria',
    'target_cities': ['Lagos', 'Abuja', 'Kano', 'Port Harcourt', 'Ibadan'],
    
    # 输出目录（同时保存到 workspace 和 iCloud 林黛玉文件夹）
    'output_dir': '/Users/zhuxiaolei/.openclaw/workspace/logs/nigeria-clients',
    'icloud_dir': '/Users/zhuxiaolei/Library/Mobile Documents/com~apple~CloudDocs/林黛玉/客户名单',
    'output_csv': 'nigeria_clients.csv',
    'output_excel': 'nigeria_clients_{}.xlsx'.format(datetime.now().strftime('%Y%m%d_%H%M%S')),
    'output_links': 'nigeria_search_links.json',
    
    # 发件人配置
    'my_name': 'Tommy',
    'email': 'z946487044@icloud.com',
    'whatsapp': '+86-183-5800-8400',
    'website': 'https://jh-hardware.com',
}

# ============ 数据模型 ============

@dataclass
class ClientInfo:
    """客户信息"""
    company_name: str
    contact_person: str = ''
    phone: str = ''
    whatsapp: str = ''
    email: str = ''
    website: str = ''
    address: str = ''
    city: str = ''
    country: str = 'Nigeria'
    product_interest: str = ''
    source: str = ''
    notes: str = ''
    found_date: str = ''

# ============ 核心功能 ============

def generate_search_links() -> List[Dict]:
    """生成 Google 搜索链接"""
    links = []
    
    for product in CONFIG['product_keywords'][:5]:  # 只用英文关键词
        for buyer_type in CONFIG['buyer_types'][:3]:  # importer, wholesaler, distributor
            for city in CONFIG['target_cities']:
                query = f"{product} {buyer_type} {city}"
                search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                
                links.append({
                    'query': query,
                    'url': search_url,
                    'city': city,
                    'product': product,
                    'buyer_type': buyer_type
                })
    
    return links

def create_client_template():
    """创建客户信息模板 CSV"""
    template_path = Path(CONFIG['output_dir']) / 'client_template.csv'
    
    headers = [
        'company_name', 'contact_person', 'phone', 'whatsapp', 'email',
        'website', 'address', 'city', 'country', 'product_interest',
        'source', 'notes', 'found_date'
    ]
    
    with open(template_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        # 添加一个示例行
        writer.writerow([
            '公司名称', '联系人', '电话', 'WhatsApp', '邮箱',
            '网站', '地址', '城市', '尼日利亚', '产品需求',
            '来源', '备注', datetime.now().strftime('%Y-%m-%d')
        ])
    
    print(f"✅ 模板已保存至：{template_path}")

def export_to_excel(clients: List[ClientInfo], save_to_icloud=True):
    """导出为 Excel 文件"""
    try:
        import pandas as pd
        
        # 保存到 workspace
        output_path = Path(CONFIG['output_dir']) / CONFIG['output_excel']
        df = pd.DataFrame([asdict(c) for c in clients])
        df.to_excel(output_path, index=False)
        
        print(f"✅ 导出 {len(clients)} 个客户到 Excel")
        print(f"📁 保存至：{output_path}")
        
        # 保存到 iCloud 林黛玉文件夹
        if save_to_icloud:
            icloud_path = Path(CONFIG['icloud_dir']) / CONFIG['output_excel']
            df.to_excel(icloud_path, index=False)
            print(f"✅ 同步到 iCloud 林黛玉/客户名单")
            print(f"📁 iCloud 路径：{icloud_path}")
        
    except ImportError:
        print("⚠️ 需要安装 pandas: pip3 install pandas")

# ============ 主流程 ============

def main():
    """主函数"""
    print("=" * 60)
    print("🌍 尼日利亚客户开发自动化脚本")
    print("=" * 60)
    print(f"⏰ 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🇳🇬 目标市场：{CONFIG['target_country']}")
    print(f"🏙️  目标城市：{', '.join(CONFIG['target_cities'])}")
    print("=" * 60)
    
    # 确保输出目录存在
    Path(CONFIG['output_dir']).mkdir(parents=True, exist_ok=True)
    Path(CONFIG['icloud_dir']).mkdir(parents=True, exist_ok=True)
    
    # 步骤 1: 生成搜索链接
    search_links = generate_search_links()
    links_path = Path(CONFIG['output_dir']) / CONFIG['output_links']
    with open(links_path, 'w', encoding='utf-8') as f:
        json.dump(search_links, f, ensure_ascii=False, indent=2)
    
    print(f"🔍 生成搜索链接：{len(search_links)} 个")
    print(f"📁 保存至：{links_path}")
    
    # 步骤 2: 创建客户模板
    create_client_template()
    
    # 步骤 3: 导出示例 Excel（同时保存到 iCloud）
    sample_client = ClientInfo(
        company_name='示例公司',
        contact_person='联系人姓名',
        phone='+234 XXX XXX XXXX',
        whatsapp='+234 XXX XXX XXXX',
        email='example@email.com',
        website='https://example.com',
        address='示例地址',
        city='Lagos',
        product_interest='Door Handles',
        source='Google Search',
        notes='示例客户',
        found_date=datetime.now().strftime('%Y-%m-%d')
    )
    export_to_excel([sample_client])
    
    print("=" * 60)
    print("✅ 脚本执行完成！")
    print("=" * 60)
    print("\n📝 使用说明：")
    print("1. 打开 nigeria_search_links.json 中的链接搜索客户")
    print("2. 将找到的客户信息填入 client_template.csv")
    print("3. 使用邮件模板联系客户（参考 nigeria-outreach-email-v3.md）")
    print("\n💡 提示：已配置每日 16:00 自动运行")
    print("⚠️ 注意：WhatsApp 功能已移除，改为手动发送")
    print("=" * 60)

if __name__ == '__main__':
    main()
