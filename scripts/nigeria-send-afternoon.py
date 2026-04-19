#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🇳🇬 尼日利亚客户下午开发信发送脚本

用途：手动发送今日的 17 个客户开发信
时间：2026-04-18 12:57
"""

import csv
import time
import random
import subprocess
from pathlib import Path

# 客户文件路径
CLIENTS_FILE = "/Users/zhuxiaolei/.openclaw/workspace/logs/nigeria-clients/nigeria_verified_clients.csv"

# 开发信模板配置（优化版）
# A/B测试 - 使用不同模板进行效果对比
MESSAGE_TEMPLATES = {
    'template_a': """Hi {company_name} team!

I'm Tommy, foreign trade manager at Yiwu Shuihui Import & Export. I noticed your company is very active in Nigeria's hardware market.

We specifically provide for importers like you:
✅ Door locks/door handles factory direct - 30-50% lower than market price
✅ SONCAP certification complete - ensure smooth customs clearance  
✅ Monthly shipment volume 5000+ sets - stable supply guarantee
✅ Direct to Lagos port - 15-25 days to port

12 Nigerian customers have chosen us as their long-term supplier.

Could you share your specific requirements? I can provide targeted quotation.

Best regards,
Tommy 📞 +86-183-5800-8400
🌐 https://jh-hardware.com""",
    'template_b': """Hello {contact_person}!

I saw your store selling hardware products, I have good news!

We are a Chinese factory, specially helping Nigerian retailers:
💰 Small batches can enjoy wholesale prices (MOQ 400 pcs)
📦 Free product catalog and samples
🚚 Includes shipping to Lagos (15-25 days)
📱 WhatsApp communication anytime, Chinese/English both ok

Many Abuja and Lagos store owners are using our products with great feedback!

Want to see products suitable for your store?

Best,
Tommy 📞 +86-183-5800-8400""",
    'template_c': """Hi there! 👋

This is Tommy from JH Hardware China.

I noticed you're in the hardware business in Nigeria. We specialize in door handles, door locks, hinges, and other hardware products:

🚪 Our Products:
• Door Handles & Knobs
• Door Locks & Security
• Door Hinges & Accessories  
• Sliding Tracks & Drawer Slides
• Furniture Legs & Cabinet Hardware
• Steel Pipes & Building Materials

✅ Factory Direct Prices (30-50% lower)
✅ MOQ: Flexible (from 400 pcs)
✅ Delivery: 15-25 days to Nigeria
✅ ISO 9001 & CE Certified

🌐 Catalog: https://jh-hardware.com

Want to see our price list?

Best regards,
Tommy
📧 z946487044@icloud.com
📞 WhatsApp: +86-183-5800-8400
"""
}

# 当前使用的模板（仅工作日测试）
# CURRENT_TEMPLATE = 'template_a'  # 已注释：周末不发送

# 发送效果追踪配置
TRACKING_ENABLED = True
TRACKING_FILE = "/Users/zhuxiaolei/.openclaw/workspace/logs/nigeria-clients/send_tracking.json"


def extract_whatsapp_numbers(phone_field):
    """从电话字段提取 WhatsApp 号码"""
    if not phone_field:
        return []
    
    numbers = []
    # 清理字符串
    cleaned = str(phone_field).replace(' ', '').replace('-', '').replace('\n', '')
    
    # 提取尼日利亚号码 (+234 或 0 开头)
    import re
    
    # +234 格式
    for match in re.findall(r'\+?234\d{10,13}', cleaned):
        num = match.replace('+', '')
        if len(num) >= 13:
            numbers.append(num[:13])
    
    # 0 开头格式
    for match in re.findall(r'\b0\d{10}\b', cleaned):
        num = '234' + match[1:]
        numbers.append(num)
    
    # 去重并返回前3个
    return list(dict.fromkeys(numbers))[:3]


def send_whatsapp_message(whatsapp_number, message, template_name='template_a', client_info=None):
    """发送 WhatsApp 消息（带追踪功能和个性化）"""
    try:
        # 格式化号码
        number = whatsapp_number.replace('+', '')
        
        # 个性化消息内容
        if client_info:
            personalized_message = message.format(
                company_name=client_info.get('company_name', 'there'),
                contact_person=client_info.get('contact_person', 'there')
            )
        else:
            personalized_message = message
        
        # 发送命令
        cmd = [
            'openclaw-whatsapp',
            'send',
            f"{number}@s.whatsapp.net",
            personalized_message
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ 发送成功: {whatsapp_number}")
            
            # 记录发送追踪数据
            if TRACKING_ENABLED:
                record_send_tracking(whatsapp_number, template_name)
            
            return True
        else:
            print(f"❌ 发送失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 发送错误: {e}")
        return False

def record_send_tracking(phone_number, template_name):
    """记录发送追踪数据"""
    import json
    from datetime import datetime
    
    tracking_path = Path(TRACKING_FILE)
    tracking_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 加载现有数据
    if tracking_path.exists():
        with open(tracking_path, 'r', encoding='utf-8') as f:
            tracking_data = json.load(f)
    else:
        tracking_data = {}
    
    # 添加新记录
    tracking_data[phone_number] = {
        'template': template_name,
        'send_time': datetime.now().isoformat(),
        'status': 'sent',
        'replies': []
    }
    
    # 保存数据
    with open(tracking_path, 'w', encoding='utf-8') as f:
        json.dump(tracking_data, f, indent=2, ensure_ascii=False)
    
    print(f"📊 追踪记录已保存: {phone_number}")


def main():
    print("=" * 60)
    print("🇳🇬 尼日利亚客户下午开发信发送")
    print("=" * 60)
    
    # 检查是否为工作日（周一到周五）
    from datetime import datetime
    current_day = datetime.now().weekday()  # 0=Monday, 6=Sunday
    if current_day >= 5:  # 周六(5)或周日(6)
        print("📅 今天是周末，跳过发送测试")
        return
    
    # 读取客户文件
    clients = []
    try:
        with open(CLIENTS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('whatsapp') or row.get('phone'):
                    clients.append(row)
    except Exception as e:
        print(f"❌ 读取客户文件失败: {e}")
        return
    
    print(f"👥 找到 {len(clients)} 个客户")
    
    if not clients:
        print("❌ 没有客户可发送")
        return
    
    # 发送消息
    sent_count = 0
    success_count = 0
    
    for i, client in enumerate(clients, 1):
        print(f"\n[{i}/{len(clients)}] 处理客户: {client.get('company_name', 'Unknown')[:50]}...")
        
        # 提取 WhatsApp 号码
        whatsapp_numbers = []
        if client.get('whatsapp'):
            whatsapp_numbers.extend(extract_whatsapp_numbers(client['whatsapp']))
        if client.get('phone'):
            whatsapp_numbers.extend(extract_whatsapp_numbers(client['phone']))
        
        # 去重
        whatsapp_numbers = list(dict.fromkeys(whatsapp_numbers))
        
        if not whatsapp_numbers:
            print("   ⏭️ 跳过: 无有效 WhatsApp 号码")
            continue
        
        # 发送给第一个号码
        whatsapp_number = whatsapp_numbers[0]
        print(f"   📱 WhatsApp: {whatsapp_number}")
        
        # 选择消息模板（A/B测试）
        message_template = MESSAGE_TEMPLATES[CURRENT_TEMPLATE]
        
        # 发送消息
        success = send_whatsapp_message(whatsapp_number, message_template, CURRENT_TEMPLATE)
        
        if success:
            success_count += 1
            sent_count += 1
            
            # 随机间隔 (25-35秒)
            interval = random.randint(25, 35)
            print(f"   ⏳ 等待 {interval} 秒...")
            time.sleep(interval)
            
            # 检查是否达到每日限制
            if sent_count >= 50:
                print("⚠️ 已达到每日发送上限 (50条)")
                break
        else:
            print("   ❌ 发送失败")
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 发送总结")
    print("=" * 60)
    print(f"✅ 成功发送: {success_count} 条")
    print(f"📈 总计处理: {len(clients)} 个客户")
    print("=" * 60)
    
    # 💓 运行完成汇报
    report_completion('nigeria-send-afternoon', success_count)


if __name__ == "__main__":
    main()
def report_completion(task_name, client_count=0):
    """运行完成汇报"""
    import subprocess
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if task_name == 'nigeria-client-finder':
        message = f"""🇳🇬 尼日利亚客户开发任务完成！✅

⏰ 时间：{timestamp}
📊 客户数：{client_count} 个
🎯 产品：五金产品（门把手、门锁、铰链等）
🔗 网站：https://jh-hardware.com

任务正常完成，客户文件已生成。"""
    elif task_name == 'nigeria-send-afternoon':
        message = f"""📧 尼日利亚 WhatsApp 发送任务完成！✅

⏰ 时间：{timestamp}
📊 发送数：{client_count} 条
🎯 客户：五金产品精准客户
📱 状态：自动发送成功

开发信已成功发送给客户。"""
    else:
        message = f"✅ {task_name} 任务完成！\n⏰ {timestamp}"
    
    try:
        # 使用 openclaw message send 发送汇报消息
        result = subprocess.run([
            'openclaw', 'message', 'send',
            '--target', 'o9cq80-VOQWTsN3h5bn6gyR2IdY4@im.wechat',
            '--message', message
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ 汇报消息已发送")
        else:
            print(f"⚠️ 汇报消息发送失败: {result.stderr}")
    except Exception as e:
        print(f"⚠️ 汇报消息发送异常: {e}")

