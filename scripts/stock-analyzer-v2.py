#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📈 A 股量化分析脚本 - 多数据源增强版
数据来源：东方财富 (主) + 新浪财经 + 腾讯财经 + 百度财经
更新时间：2026-04-09

推送方式：微信（OpenClaw）
"""

import os
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import subprocess
import sys
import time
import requests

warnings.filterwarnings('ignore')

# ==================== 配置区域 ====================
CONFIG = {
    'stocks': [
        {'code': '000001', 'name': '平安银行'},
        {'code': '600519', 'name': '贵州茅台'},
        {'code': '300750', 'name': '宁德时代'},
        {'code': '601899', 'name': '紫金矿业'},
    ],
    'notify_time': '09:40',
    'output_dir': '/Users/zhuxiaolei/.openclaw/workspace/logs/stock-analysis',
    'wechat_user': 'o9cq80-VOQWTsN3h5bn6gyR2IdY4@im.wechat',
    'account_id': 'ec25a54ce939-im-bot',
    'max_retries': 3,
    'retry_delay': 2,
}

# ==================== 数据源配置 ====================
DATA_SOURCES = {
    'eastmoney': {
        'name': '东方财富',
        'priority': 1,
        'base_url': 'https://push2.eastmoney.com',
    },
    'sina': {
        'name': '新浪财经',
        'priority': 2,
        'base_url': 'https://hq.sinajs.cn',
    },
    'tencent': {
        'name': '腾讯财经',
        'priority': 3,
        'base_url': 'https://qt.gtimg.cn',
    },
    'baidu': {
        'name': '百度财经',
        'priority': 4,
        'base_url': 'https://finance.pae.baidu.com',
    },
}

# ==================== 风险提示 ====================
RISK_DISCLAIMER = """
⚠️ 风险提示
═══════════════════════════════════════════════════════════
本文仅为数据与逻辑分析，不构成任何投资建议。
股市有风险，入市需谨慎。
请结合自身风险承受能力，独立做出投资决策。
═══════════════════════════════════════════════════════════
"""

# ==================== 通用数据获取函数 ====================
def fetch_with_retry(url, params=None, headers=None, max_retries=3):
    """带重试的 HTTP 请求"""
    for i in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                return response
            time.sleep(CONFIG['retry_delay'])
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(CONFIG['retry_delay'])
            else:
                raise e
    return None

# ==================== 技术面分析 - 多数据源 ====================
def get_technical_data_em(stock_code, stock_name):
    """东方财富数据源"""
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq")
        if len(df) < 60:
            return None
        
        latest = df.iloc[-1]
        close_col = '收盘' if '收盘' in df.columns else 'close'
        vol_col = '成交量' if '成交量' in df.columns else 'volume'
        
        return {
            'source': 'eastmoney',
            'latest_price': float(latest[close_col]),
            'change_pct': float(latest['涨跌幅']),
            'volume': float(latest[vol_col]),
            'df': df,
        }
    except Exception as e:
        return None

def get_technical_data_sina(stock_code, stock_name):
    """新浪财经数据源"""
    try:
        # 构造股票代码（sz/sh + code）
        prefix = 'sz' if stock_code.startswith(('0', '3')) else 'sh'
        url = f"https://hq.sinajs.cn/list={prefix}{stock_code}"
        
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        
        # 解析返回数据
        data_line = response.text.strip()
        if '=' not in data_line:
            return None
        
        data = data_line.split('=')[1].strip('"').split(',')
        if len(data) < 32:
            return None
        
        # 新浪财经数据格式
        current_price = float(data[3])
        prev_close = float(data[2])
        change_pct = ((current_price - prev_close) / prev_close) * 100
        volume = float(data[8])
        
        return {
            'source': 'sina',
            'latest_price': current_price,
            'change_pct': change_pct,
            'volume': volume,
        }
    except Exception as e:
        return None

def get_technical_data_tencent(stock_code, stock_name):
    """腾讯财经数据源"""
    try:
        prefix = 'sz' if stock_code.startswith(('0', '3')) else 'sh'
        url = f"https://qt.gtimg.cn/q={prefix}{stock_code}"
        
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        
        data_line = response.content.decode('gbk').strip()
        if '=' not in data_line:
            return None
        
        data = data_line.split('~')
        if len(data) < 50:
            return None
        
        return {
            'source': 'tencent',
            'latest_price': float(data[3]),
            'change_pct': float(data[32]),
            'volume': float(data[6]),
        }
    except Exception as e:
        return None

def get_technical_data_multi_source(stock_code, stock_name):
    """多数据源获取技术面数据"""
    print(f"\n📉 技术面分析 - {stock_name}({stock_code})")
    print("=" * 60)
    
    # 按优先级尝试不同数据源
    sources = [
        ('eastmoney', get_technical_data_em),
        ('sina', get_technical_data_sina),
        ('tencent', get_technical_data_tencent),
    ]
    
    for source_name, source_func in sources:
        try:
            print(f"  尝试数据源：{DATA_SOURCES[source_name]['name']}...")
            result = source_func(stock_code, stock_name)
            if result:
                print(f"  ✅ {DATA_SOURCES[source_name]['name']} 获取成功")
                return result
            else:
                print(f"  ❌ {DATA_SOURCES[source_name]['name']} 返回空数据")
        except Exception as e:
            print(f"  ❌ {DATA_SOURCES[source_name]['name']} 失败：{str(e)[:50]}")
    
    print("❌ 所有数据源均失败")
    return None

# ==================== 基本面分析 ====================
def get_fundamental_data(stock_code, stock_name):
    """获取基本面数据"""
    print(f"\n📊 基本面分析 - {stock_name}({stock_code})")
    print("=" * 60)
    
    try:
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        
        try:
            financial_data = ak.stock_financial_analysis_indicator(symbol=stock_code)
            latest_financial = financial_data.iloc[0] if len(financial_data) > 0 else None
        except:
            latest_financial = None
        
        try:
            business = ak.stock_profile_em(symbol=stock_code)
            main_business = business.get('主营业务', '暂无数据')
        except:
            main_business = '暂无数据'
        
        print(f"主营业务：{main_business[:50]}...")
        
        if latest_financial is not None:
            print(f"\n核心财务指标（最新报告期）:")
            print(f"  每股收益 (EPS): {latest_financial.get('基本每股收益', 'N/A')} 元")
            print(f"  净资产收益率 (ROE): {latest_financial.get('加权净资产收益率', 'N/A')}%")
            print(f"  营业收入增长率：{latest_financial.get('营业收入同比增长率', 'N/A')}%")
            print(f"  净利润增长率：{latest_financial.get('归属净利润同比增长率', 'N/A')}%")
            print(f"  资产负债率：{latest_financial.get('资产负债率', 'N/A')}%")
        
        return {
            'main_business': main_business,
            'financial': latest_financial
        }
    except Exception as e:
        print(f"❌ 获取基本面数据失败：{e}")
        return None

# ==================== 资金面分析 ====================
def get_capital_flow(stock_code, stock_name):
    """获取资金面数据"""
    print(f"\n💰 资金面分析 - {stock_name}({stock_code})")
    print("=" * 60)
    
    try:
        try:
            main_flow = ak.stock_individual_fund_flow(symbol=stock_code)
            if len(main_flow) > 0:
                latest = main_flow.iloc[-1]
                print(f"\n主力资金:")
                print(f"  净流入：{latest.get('主力净流入-净额', 'N/A')} 万元")
        except:
            print(f"  主力资金数据暂不可用")
        
        try:
            north_flow = ak.stock_hsgt_individual_em(symbol=stock_code)
            if len(north_flow) > 0:
                latest_north = north_flow.iloc[-1]
                print(f"\n北向资金:")
                print(f"  净流入：{latest_north.get('净流入', 'N/A')} 万元")
        except:
            print(f"  北向资金数据暂不可用（非沪深股通标的）")
        
        try:
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            turnover = stock_info[stock_info['item'] == '换手率'].iloc[0]['value']
            print(f"\n换手率：{turnover}%")
        except:
            print(f"  换手率数据暂不可用")
        
        return {}
    except Exception as e:
        print(f"❌ 获取资金面数据失败：{e}")
        return None

# ==================== 估值分析 ====================
def get_valuation_data(stock_code, stock_name):
    """获取估值数据"""
    print(f"\n💎 估值分析 - {stock_name}({stock_code})")
    print("=" * 60)
    
    try:
        valuation = ak.stock_value_em(symbol=stock_code)
        latest_val = valuation.iloc[-1] if len(valuation) > 0 else None
        
        if latest_val is not None:
            pe = latest_val.get('市盈率', 'N/A')
            pb = latest_val.get('市净率', 'N/A')
            ps = latest_val.get('市销率', 'N/A')
            
            print(f"\n当前估值:")
            print(f"  市盈率 (PE): {pe}")
            print(f"  市净率 (PB): {pb}")
            print(f"  市销率 (PS): {ps}")
            
            try:
                if isinstance(pe, (int, float)) and pe > 0:
                    pe_level = "🔴 高估" if pe > 50 else "🟡 合理" if pe > 20 else "🟢 低估"
                    print(f"\n估值水平：{pe_level} (PE={pe})")
            except:
                pass
        
        return {'pe': pe, 'pb': pb, 'ps': ps}
    except Exception as e:
        print(f"❌ 获取估值数据失败：{e}")
        return None

# ==================== 风险分析 ====================
def get_risk_data(stock_code, stock_name):
    """获取风险数据"""
    print(f"\n⚠️ 风险提示 - {stock_name}({stock_code})")
    print("=" * 60)
    
    risks = []
    
    try:
        risk_report = ak.stock_cg_equity_pledge_em(symbol=stock_code)
        if len(risk_report) > 0:
            risks.append("📉 存在股权质押记录")
    except:
        pass
    
    try:
        forecast = ak.stock_performance_forecast_em(symbol=stock_code)
        if len(forecast) > 0:
            latest = forecast.iloc[0]
            if '预减' in str(latest) or '亏损' in str(latest):
                risks.append("⚠️ 业绩预告：可能存在业绩下滑")
    except:
        pass
    
    if len(risks) == 0:
        risks.append("✅ 暂无重大风险事项")
    
    for risk in risks:
        print(f"  {risk}")
    
    return {'risks': risks}

# ==================== 操作建议 ====================
def generate_recommendation(tech_data, valuation_data, risk_data):
    """生成操作建议"""
    print(f"\n🎯 操作参考")
    print("=" * 60)
    
    if tech_data is None:
        print("❌ 数据不足，无法生成操作建议")
        return
    
    latest_price = tech_data['latest_price']
    change_pct = tech_data['change_pct']
    
    print(f"\n当前价格：{latest_price:.2f} 元")
    print(f"涨跌幅：{change_pct:+.2f}%")
    
    if 'df' in tech_data:
        df = tech_data['df']
        close_col = '收盘' if '收盘' in df.columns else 'close'
        
        ma5 = df[close_col].rolling(5).mean().iloc[-1]
        ma20 = df[close_col].rolling(20).mean().iloc[-1]
        recent_high = df['高'].iloc[-20:].max() if '高' in df.columns else df['最高'].iloc[-20:].max()
        recent_low = df['低'].iloc[-20:].min() if '低' in df.columns else df['最低'].iloc[-20:].min()
        
        print(f"\n均线系统:")
        print(f"  MA5: {ma5:.2f} 元 {'📈' if latest_price > ma5 else '📉'}")
        print(f"  MA20: {ma20:.2f} 元 {'📈' if latest_price > ma20 else '📉'}")
        
        print(f"\n支撑位/压力位:")
        print(f"  支撑位：{recent_low:.2f} 元 (近 20 日低点)")
        print(f"  压力位：{recent_high:.2f} 元 (近 20 日高点)")
        
        # 趋势判断
        trend = "多头" if latest_price > ma20 else "空头"
        print(f"\n当前趋势：{trend}")
        
        # 综合判断
        if trend == "多头" and change_pct > 0:
            print("\n📈 综合判断：偏多，可逢低关注")
        elif trend == "空头" and change_pct < 0:
            print("\n📉 综合判断：偏空，建议观望")
        else:
            print("\n📊 综合判断：震荡，高抛低吸")
    
    if len(risk_data.get('risks', [])) > 0 and '暂无' not in str(risk_data['risks']):
        print("\n⚠️ 特别提示：存在风险事项，请谨慎决策")

# ==================== 完整分析流程 ====================
def analyze_stock(stock_info):
    """完整分析一只股票"""
    stock_code = stock_info['code']
    stock_name = stock_info['name']
    
    print("\n" + "📈" * 30)
    print(f"  A 股量化分析报告 - {stock_name}({stock_code})")
    print("📈" * 30)
    
    fundamental_data = get_fundamental_data(stock_code, stock_name)
    technical_data = get_technical_data_multi_source(stock_code, stock_name)
    capital_data = get_capital_flow(stock_code, stock_name)
    valuation_data = get_valuation_data(stock_code, stock_name)
    risk_data = get_risk_data(stock_code, stock_name)
    
    if technical_data:
        generate_recommendation(technical_data, valuation_data, risk_data)
    
    return {
        'stock_code': stock_code,
        'stock_name': stock_name,
        'fundamental_data': fundamental_data,
        'technical_data': technical_data,
        'capital_data': capital_data,
        'valuation_data': valuation_data,
        'risk_data': risk_data,
    }

# ==================== 主函数 ====================
def main():
    """主函数"""
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(RISK_DISCLAIMER)
    print(f"\n分析开始时间：{report_time}")
    
    results = []
    for stock in CONFIG['stocks']:
        result = analyze_stock(stock)
        results.append(result)
    
    print(f"\n✅ 分析完成！时间：{report_time}")
    
    # 推送到微信
    send_wechat_notify(results, report_time)
    
    return results

# ==================== 微信推送 ====================
def send_wechat_notify(results, report_time):
    """发送微信推送"""
    print("\n📱 准备微信推送...")
    
    try:
        message = "📈 A 股量化分析报告\n"
        message += "━" * 30 + "\n"
        message += f"📅 时间：{report_time}\n\n"
        
        for result in results:
            stock_name = result.get('stock_name', 'Unknown')
            stock_code = result.get('stock_code', 'Unknown')
            tech_data = result.get('technical_data', {})
            
            if tech_data and tech_data.get('latest_price'):
                price = tech_data.get('latest_price', 0)
                change_pct = tech_data.get('change_pct', 0)
                source = tech_data.get('source', 'unknown')
                
                emoji = '🟢' if change_pct > 0 else '🔴' if change_pct < 0 else '⚪'
                
                message += f"{emoji} {stock_name}({stock_code})\n"
                message += f"   价格：¥{price:.2f} ({change_pct:+.2f}%)\n"
                message += f"   数据源：{DATA_SOURCES.get(source, {}).get('name', 'Unknown')}\n\n"
        
        message += "═" * 30 + "\n"
        message += "⚠️ 风险提示：不构成投资建议\n"
        message += "═" * 30
        
        result = subprocess.run(
            ['openclaw', 'message', 'send', 
             '-t', CONFIG['wechat_user'],
             '--channel', 'openclaw-weixin',
             '--account', CONFIG['account_id'],
             '-m', message],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            print("✅ 微信推送成功")
        else:
            print(f"❌ 微信推送失败：{result.stderr}")
            
    except Exception as e:
        print(f"❌ 推送异常：{str(e)}")

if __name__ == "__main__":
    main()
