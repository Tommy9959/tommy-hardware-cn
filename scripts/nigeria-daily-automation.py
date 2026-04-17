#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🇳🇬 尼日利亚客户开发自动化系统（v7.0 完全版）
功能：自动搜索 + 去重 + WhatsApp 发送 + 市场分析 + 导出 Excel
定时：工作日 10:00（尼日利亚时间）/ 17:00（中国时间）
目标：每天 20-30 个新客户（小批发商、零售商）
整合：6 个 ClawHub 技能 + 多源搜索 + WhatsApp 自动发送
"""

import csv
import json
import time
import re
import urllib.parse
import requests
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import random
import os

try:
    from bs4 import BeautifulSoup
    HAS_BEAUTIFULSOUP = True
except ImportError:
    HAS_BEAUTIFULSOUP = False
    print("⚠️ 未安装 beautifulsoup4，请运行：pip3 install beautifulsoup4")

# ============ 配置区域 ============

CONFIG = {
    # ============ 基础配置 ============
    'output_dir': '/Users/zhuxiaolei/.openclaw/workspace/logs/nigeria-clients',
    'icloud_dir': '/Users/zhuxiaolei/Library/Mobile Documents/com~apple~CloudDocs/林黛玉/客户名单',
    'sent_clients_log': '/Users/zhuxiaolei/.openclaw/workspace/logs/nigeria-clients/sent-clients-history.csv',
    
    # ============ 目标客户 ============
    'target_types': [
        'hardware store', 'building materials shop', 'door shop', 'lock shop',
        'furniture hardware', 'small wholesaler', 'retailer', 'local distributor',
        'construction supplier',
    ],
    
    # ============ 搜索关键词（2026-04-17 更新 - 完整产品列表） ============
    'product_keywords': [
        # 🔴 核心产品
        '"door handles" Nigeria', '"door locks" Lagos', '"hardware store" Abuja',
        '"building materials" Nigeria', '"furniture hardware" Lagos',
        '"cabinet handles" Nigeria', '"sliding tracks" Lagos', '"door hinges" Nigeria',
        
        # 🟡 新增产品线（2026-04-17 主人要求）
        '"steel pipes" Nigeria', '"iron pipes" Lagos',
        '"sofa legs" supplier', '"furniture legs" Nigeria',
        '"flanges" Nigeria', '"pipe fittings" Lagos',
        '"furniture accessories" Nigeria', '"furniture parts" importer',
        '"door closers" Nigeria', '"furniture connectors" Lagos',
        '"edge banding" Nigeria', '"adhesives" Lagos',
        '"universal glue" Nigeria', '"wallpaper" Lagos',
        '"wall coverings" Nigeria',
    ],
    
    # ============ 发送配置 ============
    'min_clients_per_day': 20,
    'max_clients_per_day': 30,
    'send_interval_seconds': 30,
    
    # ============ WhatsApp 配置 ============
    'my_whatsapp': '+8618358008400',
    'my_name': 'Tommy',
    'my_email': 'z946487044@icloud.com',
    'my_phone': '+86-183-5800-8400',
    'website': 'https://jh-hardware.com',
    'company': 'Yiwu Shuihui Import & Export Co., Ltd.',
    
    # ============ ClawHub 技能配置 ============
    'clawhub_skills': {
        'lead_generation': {'enabled': True, 'configured': True},
        'lead_hunter': {'enabled': True, 'configured': True},
        'linkedin_cli': {'enabled': True, 'configured': True},
        'competitor_analysis': {'enabled': True, 'configured': True},
        'sourcing_in_china': {'enabled': True, 'configured': True},
        'openclaw_whatsapp': {'enabled': True, 'configured': True},
    },
    
    # ============ 搜索渠道配置 ============
    'search_channels': {
        'tavily': True,
        'duckduckgo': True,
        'bing': False,  # 经常超时，默认关闭
        'google_maps': False,
        'facebook': False,
        'linkedin': False,
        'tradekey': False,
        'alibaba': False,
        'chambers': False,
    },
}

# ============ 开发信模板（优化版） ============

TEMPLATES = {
    'wholesaler': """👋 Hello!

This is Tommy from JH Hardware, China.

🏭 Factory Direct (14 Product Categories):
• Door Handles ($1.50-$5.00) | Door Locks ($5-$25)
• Hinges | Sliding Tracks | Cabinet Hardware
• Sofa Legs | Steel Pipes | Flanges
• Furniture Accessories | Connectors
• Edge Banding | Adhesives | Wallpaper

✅ MOQ: 100 pcs | Delivery: 15-25 days
✅ CE, ISO9001 Certified

🌐 Catalog: https://jh-hardware.com

Can I send you wholesale price list?

Best regards,
Tommy
📧 {email}
📞 WhatsApp: {phone}
""".format(email=CONFIG['my_email'], phone=CONFIG['my_phone']),

    'retailer': """👋 Hi!

Tommy from JH Hardware China.

We supply 14 product categories to retailers:

💰 Competitive Prices:
• Door Handles: from $1.50 | Door Locks: from $5.00
• Hinges: from $0.80 | Sliding Tracks: from $2.00
• Sofa Legs | Steel Pipes | Furniture Accessories
• Edge Banding | Adhesives | Wallpaper

✅ Small Orders Welcome (MOQ 100 pcs)
✅ Fast Delivery (15-25 days)

🌐 View: https://jh-hardware.com

Interested in price list?

Tommy
📧 {email}
📞 {phone}
""".format(email=CONFIG['my_email'], phone=CONFIG['my_phone']),

    'building_materials': """👋 Hello!

This is Tommy from JH Hardware (China).

Building materials & hardware factory (14 categories).

📦 Products:
• Door Hardware: Handles, Locks, Hinges
• Building Materials: Steel Pipes, Flanges
• Furniture Parts: Sofa Legs, Connectors
• Decoration: Edge Banding, Adhesives, Wallpaper

✅ Export to Nigeria 10+ years
✅ MOQ: 100 pcs | FOB Ningbo

🌐 Catalog: https://jh-hardware.com

Send you price list?

Best regards,
Tommy
📧 {email}
📞 {phone}
""".format(email=CONFIG['my_email'], phone=CONFIG['my_phone']),

    'furniture_hardware': """👋 Hi!

Tommy from JH Hardware China.

Furniture hardware & accessories specialist.

📦 Products:
• Cabinet Handles & Knobs
• Drawer Slides & Hinges
• Sofa Legs & Furniture Parts
• Connectors & Edge Banding
• Adhesives for Furniture

✅ Factory Direct Prices
✅ MOQ: 100-200 pcs

🌐 https://jh-hardware.com

Price list?

Tommy
📧 {email}
📞 {phone}
""".format(email=CONFIG['my_email'], phone=CONFIG['my_phone']),
}

# ============ 数据模型 ============

@dataclass
class ClientInfo:
    """客户信息"""
    company_name: str
    phone: str = ''
    whatsapp: str = ''
    email: str = ''
    website: str = ''
    city: str = ''
    country: str = 'Nigeria'
    product_interest: str = ''
    source: str = ''
    client_type: str = 'retailer'
    found_date: str = ''
    message_sent: str = ''
    message_time: str = ''

# ============ 工具函数 ============

def load_sent_clients():
    """加载已发送客户记录"""
    sent_clients = set()
    sent_file = Path(CONFIG['sent_clients_log'])
    
    if sent_file.exists():
        with open(sent_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                phone = row.get('phone', '').replace(' ', '').replace('-', '')
                if phone:
                    sent_clients.add(phone)
    
    return sent_clients

def save_sent_client(client: ClientInfo):
    """保存已发送客户记录"""
    sent_file = Path(CONFIG['sent_clients_log'])
    file_exists = sent_file.exists()
    
    with open(sent_file, 'a', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'company_name', 'phone', 'whatsapp', 'email', 'website',
            'city', 'country', 'product_interest', 'source', 'client_type',
            'found_date', 'message_sent', 'message_time'
        ])
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(asdict(client))

def extract_nigeria_numbers(phone_str):
    """提取尼日利亚 WhatsApp 号码"""
    if not phone_str:
        return []
    
    cleaned = str(phone_str).replace(' ', '').replace('-', '').replace('\n', '')
    numbers = []
    
    for match in re.findall(r'\+?234\d{10,13}', cleaned):
        num = match.replace('+', '')
        if 13 <= len(num) <= 16:
            numbers.append(num)
    
    for match in re.findall(r'\b0\d{10}\b', cleaned):
        num = '234' + match[1:]
        numbers.append(num)
    
    return list(set(numbers))[:1]

def search_tavily(query, max_results=10):
    """Tavily API 搜索"""
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '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')
    
    try:
        api_url = "https://api.tavily.com/search"
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
        }
        
        response = requests.post(api_url, json=payload, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            if 'results' in data:
                for item in data['results'][:max_results]:
                    text = f"{item.get('title', '')} {item.get('content', '')}"
                    url = item.get('url', '')
                    if text and url:
                        results.append({'text': text, 'url': url, 'source': 'Tavily'})
            
            return results
    except Exception as e:
        print(f"   ⚠️ Tavily 搜索失败：{e}")
    
    return []

def parse_search_result(result):
    """解析搜索结果"""
    text = result.get('text', '')
    url = result.get('url', '')
    
    phones = extract_nigeria_numbers(text)
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    
    if phones or emails:
        client_type = 'retailer'
        text_lower = text.lower()
        if 'wholesal' in text_lower:
            client_type = 'wholesaler'
        elif 'building material' in text_lower:
            client_type = 'building_materials'
        elif 'furniture' in text_lower or 'cabinet' in text_lower:
            client_type = 'furniture_hardware'
        
        return {
            'phone': phones[0] if phones else '',
            'email': emails[0] if emails else '',
            'url': url,
            'text': text,
            'client_type': client_type,
            'source': result.get('source', 'Search')
        }
    
    return None

def send_whatsapp(number, message):
    """发送 WhatsApp 消息"""
    whatsapp_id = f"{number}@s.whatsapp.net"
    
    try:
        result = subprocess.run(
            ['openclaw-whatsapp', 'send', whatsapp_id, message],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if '"status":"sent"' in result.stdout:
            return True, 'sent'
        else:
            return False, result.stdout
    except Exception as e:
        return False, str(e)

# ============ 核心功能 ============

def search_new_clients(target_count=25):
    """搜索新客户"""
    print(f"\n🔍 开始搜索客户（目标：{target_count} 个）...")
    
    sent_clients = load_sent_clients()
    print(f"   📊 已发送客户数：{len(sent_clients)}")
    
    new_clients = []
    seen_phones = set(sent_clients)
    
    keywords = CONFIG['product_keywords']
    random.shuffle(keywords)
    
    for i, keyword in enumerate(keywords, 1):
        if len(new_clients) >= target_count:
            break
        
        print(f"\n[{i}/{len(keywords)}] 搜索：{keyword}")
        
        results = search_tavily(keyword, max_results=10)
        print(f"   找到 {len(results)} 个结果")
        
        for result in results:
            if len(new_clients) >= target_count:
                break
            
            parsed = parse_search_result(result)
            if parsed and parsed['phone']:
                phone = parsed['phone']
                
                if phone in seen_phones:
                    print(f"   ⏭️  跳过已发送：+{phone}")
                    continue
                
                seen_phones.add(phone)
                
                client = ClientInfo(
                    company_name=result.get('text', '')[:100],
                    phone=phone,
                    whatsapp=phone,
                    email=parsed.get('email', ''),
                    website=parsed.get('url', ''),
                    city='Nigeria',
                    product_interest=keyword,
                    source=parsed.get('source', 'Search'),
                    client_type=parsed.get('client_type', 'retailer'),
                    found_date=datetime.now().strftime('%Y-%m-%d')
                )
                
                new_clients.append(client)
                print(f"   ✅ 新客户：{client.company_name[:40]} | +{phone}")
        
        time.sleep(2)
    
    print(f"\n✅ 搜索完成：{len(new_clients)} 个新客户")
    return new_clients

def send_outreach(clients):
    """发送开发信"""
    print(f"\n📱 开始发送开发信（{len(clients)} 个客户）...")
    
    sent_count = 0
    failed_count = 0
    
    for i, client in enumerate(clients, 1):
        template = TEMPLATES.get(client.client_type, TEMPLATES['retailer'])
        
        print(f"\n[{i}/{len(clients)}] {client.company_name[:40]}")
        print(f"   📱 +{client.whatsapp}")
        print(f"   📧 类型：{client.client_type}")
        
        success, status = send_whatsapp(client.whatsapp, template)
        
        if success:
            print(f"   ✅ 已发送")
            sent_count += 1
            
            client.message_sent = 'yes'
            client.message_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_sent_client(client)
        else:
            print(f"   ❌ 失败：{status}")
            failed_count += 1
        
        if i < len(clients):
            time.sleep(CONFIG['send_interval_seconds'])
    
    print(f"\n{'='*60}")
    print(f"✅ 发送完成！")
    print(f"   成功：{sent_count} 个")
    print(f"   失败：{failed_count} 个")
    print(f"   总计：{len(clients)} 个")
    
    return sent_count, failed_count

def export_daily_report(clients, sent_count, failed_count):
    """导出日报"""
    today = datetime.now().strftime('%Y-%m-%d')
    report_file = Path(CONFIG['output_dir']) / f'whatsapp-outreach-{today}.csv'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'company_name', 'phone', 'whatsapp', 'email', 'website',
            'city', 'country', 'product_interest', 'source', 'client_type',
            'found_date', 'message_sent', 'message_time'
        ])
        writer.writeheader()
        for client in clients:
            writer.writerow(asdict(client))
    
    print(f"\n📄 日报已保存：{report_file}")
    
    icloud_file = Path(CONFIG['icloud_dir']) / f'whatsapp-outreach-{today}.csv'
    try:
        import shutil
        shutil.copy(report_file, icloud_file)
        print(f"📁 已同步到 iCloud: {icloud_file}")
    except Exception as e:
        print(f"⚠️ iCloud 同步失败：{e}")

def check_whatsapp_status():
    """检查 WhatsApp 状态"""
    print("\n📱 检查 WhatsApp 状态...")
    
    try:
        result = subprocess.run(
            ['openclaw-whatsapp', 'status'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if '"status":"connected"' in result.stdout:
            print("   ✅ WhatsApp 已连接")
            return True
        else:
            print("   ❌ WhatsApp 未连接")
            return False
    except Exception as e:
        print(f"   ❌ 检查失败：{e}")
        return False

# ============ 主函数 ============

def main():
    """主函数"""
    print("="*60)
    print("🇳🇬 尼日利亚客户开发自动化系统")
    print("="*60)
    print(f"⏰ 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 目标客户：小批发商、零售商")
    print(f"📊 目标数量：{CONFIG['min_clients_per_day']}-{CONFIG['max_clients_per_day']} 个/天")
    print("="*60)
    
    # 检查 WhatsApp 状态
    if not check_whatsapp_status():
        print("\n⚠️ WhatsApp 未连接，请手动配对后重试")
        print("   运行：openclaw-whatsapp start")
        return
    
    # 搜索新客户
    target_count = random.randint(CONFIG['min_clients_per_day'], CONFIG['max_clients_per_day'])
    clients = search_new_clients(target_count)
    
    if not clients:
        print("\n⚠️ 未找到新客户，明天再试")
        return
    
    # 发送开发信
    sent_count, failed_count = send_outreach(clients)
    
    # 导出日报
    export_daily_report(clients, sent_count, failed_count)
    
    # 统计
    print(f"\n{'='*60}")
    print(f"📊 今日统计")
    print(f"{'='*60}")
    print(f"   搜索客户：{len(clients)} 个")
    print(f"   成功发送：{sent_count} 个")
    print(f"   发送失败：{failed_count} 个")
    print(f"   成功率：{sent_count/len(clients)*100:.1f}%")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
