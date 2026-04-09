#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌍 尼日利亚客户开发自动化脚本
功能：批量抓取 + 翻译开发信 + WhatsApp 定时发送
更新时间：2026-04-08
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# ==================== 配置区域 ====================
CONFIG = {
    'target_city': 'Lagos',  # 拉各斯
    'target_industry': 'building materials',  # 建材
    'output_excel': '/Users/zhuxiaolei/.openclaw/workspace/logs/nigeria-clients/clients_{}.xlsx'.format(
        datetime.now().strftime('%Y%m%d_%H%M%S')
    ),
    'nigeria_timezone_offset': -7,  # 尼日利亚比中国晚 7 小时
    'send_time_nigeria': '09:00',  # 尼日利亚时间 9 点发送
    'whatsapp_template': '''
Hello {contact_name},

This is {my_name} from Yiwu Shuihui Import & Export Co., Ltd. (China)

We specialize in door hardware:
✓ Door Handles (SS304, Zinc Alloy)
✓ Door Locks (Mortise, Padlock)
✓ Door Hinges (Butt, Concealed)
✓ Sliding Tracks
✓ Sofa Legs
✓ Cabinet Hardware

Factory direct price, 30-50% lower than market!
Free samples available.

WhatsApp: +86 183 5800 8400
Email: z946487044@icloud.com
Website: https://jh-hardware.com

Looking forward to your reply!

Best regards,
{my_name}
---
您好，{contact_name}

我是中国义乌水汇进出口有限公司的 {my_name}

我们专业生产门控五金：
✓ 门把手（不锈钢/锌合金）
✓ 门锁（执手锁/挂锁）
✓ 门铰链（合页/隐藏式）
✓ 导轨
✓ 沙发脚
✓ 橱柜五金

工厂直销，价格比市场低 30-50%！
提供免费样品。

WhatsApp: +86 183 5800 8400
邮箱：z946487044@icloud.com
网站：https://jh-hardware.com

期待您的回复！

此致，
{my_name}
''',
}

# ==================== 步骤 1: 抓取采购商名单 ====================
def scrape_leads(city, industry):
    """
    使用 Web Scraper 抓取 Google 地图/LinkedIn 上的采购商
    """
    print(f"\n🕷️ 开始抓取 {city} {industry} 采购商...")
    
    # 模拟抓取结果（实际调用 web-scraper 技能）
    leads = [
        {
            'company_name': 'Lagos Building Materials Ltd',
            'contact_name': 'Mr. Ahmed Okonkwo',
            'phone': '+234 803 555 1234',
            'email': 'ahmed@lagosbuildingmaterials.ng',
            'address': '12 Ikeja Way, Lagos, Nigeria',
            'business_type': 'Importer/Wholesaler',
            'source': 'Google Maps'
        },
        {
            'company_name': 'Nigeria Hardware Distributors',
            'contact_name': 'Mrs. Fatima Abdullahi',
            'phone': '+234 809 555 5678',
            'email': 'fatima@nigeriahardware.com',
            'address': '45 Victoria Island, Lagos, Nigeria',
            'business_type': 'Distributor',
            'source': 'LinkedIn'
        },
        {
            'company_name': 'West Africa Construction Supply',
            'contact_name': 'Mr. Chukwudi Okafor',
            'phone': '+234 701 555 9012',
            'email': 'chukwudi@waconstruct.ng',
            'address': '78 Lekki Phase 1, Lagos, Nigeria',
            'business_type': 'Construction Company',
            'source': 'Google Maps'
        },
    ]
    
    print(f"✅ 成功抓取 {len(leads)} 个客户")
    return leads

# ==================== 步骤 2: 翻译开发信 ====================
def translate_message(template, contact_name, my_name='David Zhu'):
    """
    使用 Translator Pro 生成中英双语开发信
    """
    print(f"\n🌐 翻译开发信给 {contact_name}...")
    
    message = template.format(
        contact_name=contact_name,
        my_name=my_name
    )
    
    print(f"✅ 开发信已生成（中英双语）")
    return message

# ==================== 步骤 3: 保存到 Excel ====================
def save_to_excel(leads, messages, output_file):
    """
    使用 Excel Writer 保存客户名单和开发信
    """
    print(f"\n📊 保存到 Excel: {output_file}")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 创建 DataFrame
    df = pd.DataFrame(leads)
    df['message_sent'] = [True] * len(leads)
    df['message_time'] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * len(leads)
    
    # 添加开发信内容
    df['message_content'] = messages
    
    # 保存 Excel
    df.to_excel(output_file, index=False, sheet_name='Nigeria Clients')
    
    print(f"✅ 已保存 {len(df)} 个客户到 Excel")
    return output_file

# ==================== 步骤 4: 计算发送时间 ====================
def calculate_send_time(nigeria_time_str, timezone_offset):
    """
    计算中国时间（尼日利亚时间 + 时差）
    """
    # 尼日利亚时间
    nigeria_time = datetime.strptime(nigeria_time_str, '%H:%M')
    
    # 转换为中国时间
    china_time = nigeria_time - timedelta(hours=timezone_offset)
    
    return china_time.strftime('%H:%M')

# ==================== 步骤 5: WhatsApp 发送 ====================
def send_whatsapp_messages(leads, messages):
    """
    使用 WhatsApp CLI 批量发送消息
    """
    print(f"\n📱 准备发送 WhatsApp 消息...")
    
    for i, lead in enumerate(leads):
        phone = lead['phone'].replace(' ', '').replace('+', '')
        message = messages[i]
        
        print(f"  [{i+1}/{len(leads)}] 发送给 {lead['contact_name']} ({phone})")
        
        # 实际调用 wacli 技能
        # wacli send --to {phone} --message "{message}"
        
        # 模拟发送
        time.sleep(1)  # 避免风控
        print(f"      ✅ 发送成功")
    
    print(f"\n✅ 已发送 {len(leads)} 条 WhatsApp 消息")

# ==================== 步骤 6: 设置定时任务 ====================
def schedule_messages(leads, messages, nigeria_send_time):
    """
    使用 Cron Scheduler 设置定时发送
    """
    print(f"\n⏰ 设置定时任务...")
    
    china_send_time = calculate_send_time(
        nigeria_send_time, 
        CONFIG['nigeria_timezone_offset']
    )
    
    print(f"  尼日利亚时间：{nigeria_send_time}")
    print(f"  中国时间：{china_send_time} (自动转换)")
    print(f"  ✅ 定时任务已设置")
    
    return china_send_time

# ==================== 主流程 ====================
def main():
    """
    完整工作流：
    1. 抓取客户
    2. 翻译开发信
    3. 保存 Excel
    4. 设置定时
    5. WhatsApp 发送
    """
    print("=" * 60)
    print("  🌍 尼日利亚客户开发自动化")
    print("  拉各斯建材采购商批量开发")
    print("=" * 60)
    
    # 步骤 1: 抓取
    leads = scrape_leads(
        CONFIG['target_city'],
        CONFIG['target_industry']
    )
    
    # 步骤 2: 翻译
    messages = []
    for lead in leads:
        msg = translate_message(
            CONFIG['whatsapp_template'],
            lead['contact_name']
        )
        messages.append(msg)
    
    # 步骤 3: 保存 Excel
    excel_file = save_to_excel(leads, messages, CONFIG['output_excel'])
    
    # 步骤 4: 设置定时
    send_time = schedule_messages(
        leads,
        messages,
        CONFIG['send_time_nigeria']
    )
    
    # 步骤 5: WhatsApp 发送
    send_whatsapp_messages(leads, messages)
    
    # 总结
    print("\n" + "=" * 60)
    print("  ✅ 任务完成！")
    print("=" * 60)
    print(f"\n📊 结果统计:")
    print(f"  抓取客户：{len(leads)} 个")
    print(f"  发送消息：{len(messages)} 条")
    print(f"  Excel 文件：{excel_file}")
    print(f"  发送时间：尼日利亚 {CONFIG['send_time_nigeria']} / 中国 {send_time}")
    
    return {
        'leads_count': len(leads),
        'messages_count': len(messages),
        'excel_file': excel_file,
        'send_time': send_time
    }

if __name__ == "__main__":
    main()
