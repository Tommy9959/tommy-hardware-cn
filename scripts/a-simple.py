#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📈 A 股简易推送 - 仅大盘指数
数据来源：AkShare
更新时间：2026-04-09

推送方式：微信（OpenClaw）
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import subprocess
import warnings
warnings.filterwarnings('ignore')

# ==================== 配置 ====================
CONFIG = {
    'wechat_user': 'o9cq80-VOQWTsN3h5bn6gyR2IdY4@im.wechat',
    'account_id': 'ec25a54ce939-im-bot',
}

# ==================== 获取大盘数据 ====================
def get_index_data():
    """获取大盘指数数据"""
    indices = [
        {'code': 'sh000001', 'name': '上证指数'},
        {'code': 'sz399006', 'name': '创业板指'},
        {'code': 'sh000300', 'name': '沪深 300'},
    ]
    
    results = []
    for idx in indices:
        try:
            code = idx['code']
            name = idx['name']
            
            # 获取实时行情
            df = ak.stock_zh_index_spot(symbol=code)
            if df is not None and len(df) > 0:
                row = df.iloc[0]
                results.append({
                    'name': name,
                    'code': code,
                    'price': float(row.get('最新价', 0)),
                    'change_pct': float(row.get('涨跌幅', 0)),
                    'change': float(row.get('涨跌额', 0)),
                })
        except Exception as e:
            print(f"❌ {name} 数据获取失败：{e}")
    
    return results

# ==================== 微信推送 ====================
def send_wechat_notify(data):
    """发送微信推送"""
    print("\n📱 准备微信推送...")
    
    try:
        message = "📈 A 股大盘速递\n" + "━" * 30 + "\n\n"
        
        for idx in data:
            name = idx['name']
            price = idx['price']
            change_pct = idx['change_pct']
            
            emoji = '🟢' if change_pct > 0 else '🔴' if change_pct < 0 else '⚪'
            arrow = '↑' if change_pct > 0 else '↓' if change_pct < 0 else '─'
            
            message += f"{emoji} {name}\n"
            message += f"   {price:.2f} 点 {arrow} {abs(change_pct):.2f}%\n\n"
        
        message += "═" * 30 + "\n"
        message += f"⏰ 更新时间：{datetime.now().strftime('%H:%M')}\n"
        message += "⚠️ 数据仅供参考\n"
        
        # 执行推送
        result = subprocess.run(
            ['openclaw', 'message', 'send', '--target', CONFIG['wechat_user'],
             '--message', message, '--channel', 'openclaw-weixin', '--account', CONFIG['account_id']],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            print("✅ 微信推送成功")
        else:
            print(f"❌ 推送失败：{result.stderr}")
            
    except Exception as e:
        print(f"❌ 推送异常：{e}")

# ==================== 主函数 ====================
def main():
    print("📈 A 股大盘速递")
    print("=" * 60)
    
    data = get_index_data()
    
    if data:
        print(f"✅ 成功获取 {len(data)} 个指数数据")
        for idx in data:
            print(f"  {idx['name']}: {idx['price']:.2f} ({idx['change_pct']:+.2f}%)")
        
        send_wechat_notify(data)
    else:
        print("❌ 数据获取失败")

if __name__ == "__main__":
    main()
