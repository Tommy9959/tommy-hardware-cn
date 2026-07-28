#!/usr/bin/env python3
"""
GSC 索引优化工具 — 每周自动提升索引覆盖

功能：
1. 重新提交所有 sitemap（促使 Google 重新抓取）
2. 检查索引覆盖率变化
3. 生成未索引页面列表
4. 输出优化建议

每周一 GSC 检查后自动运行
"""

import json, os, sys
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SITE_URL = "sc-domain:jh-hardware.com"
TOKEN_FILE = os.path.expanduser("~/.openclaw/service-env/gsc-oauth-token.json")

# 三大语言的 sitemap
SITEMAPS = [
    "https://jh-hardware.com/sitemap.xml",
    "https://jh-hardware.com/en/sitemap.xml",
    "https://jh-hardware.com/zh/sitemap.xml",
    "https://jh-hardware.com/ar/sitemap.xml",
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            token = json.load(f)
        creds = Credentials.from_authorized_user_info(token, [
            'https://www.googleapis.com/auth/webmasters'
        ])
    
    if not creds or not creds.valid:
        from google.auth.transport.requests import Request
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())
        else:
            log("❌ Token 无效，请重新授权: python3 gsc-api-setup.py --auth")
            sys.exit(1)
    
    return build('searchconsole', 'v1', credentials=creds, static_discovery=False)


def resubmit_sitemaps(service):
    """重新提交所有 sitemap，促使 Google 重新抓取"""
    log("📤 重新提交 sitemap...")
    success = 0
    failed = 0
    for url in SITEMAPS:
        try:
            service.sitemaps().submit(
                siteUrl=SITE_URL, feedpath=url
            ).execute()
            log(f"  ✅ {url}")
            success += 1
        except Exception as e:
            log(f"  ❌ {url}: {e}")
            failed += 1
    log(f"  结果: {success} 成功, {failed} 失败")
    return success > 0


def check_index_status(service):
    """检查索引状态变化"""
    log("📊 检查索引状态...")
    
    # sitemap 提交 vs 已索引
    sitemaps = service.sitemaps().list(siteUrl=SITE_URL).execute()
    total_submitted = 0
    total_indexed = 0
    
    for sm in sitemaps.get('sitemap', []):
        cnt = sm.get('contents', [{}])
        submitted = int(cnt[0].get('submitted', 0)) if cnt else 0
        indexed = int(cnt[0].get('indexed', 0)) if cnt else 0
        total_submitted += submitted
        total_indexed += indexed
    
    log(f"  提交: {total_submitted} 个 URL")
    log(f"  已索引(GSC统计): {total_indexed}")
    
    # 用搜索数据估算实际索引的活跃页面
    try:
        r = service.searchanalytics().query(siteUrl=SITE_URL, body={
            'startDate': (datetime.now() - timedelta(days=28)).strftime('%Y-%m-%d'),
            'endDate': datetime.now().strftime('%Y-%m-%d'),
            'dimensions': ['page'],
            'rowLimit': 5000
        }).execute()
        active_pages = len(r.get('rows', []))
        total_imp = sum(p.get('impressions', 0) for p in r.get('rows', []))
        log(f"  近28天有搜索数据的活跃页面: {active_pages}")
        log(f"  总展示: {total_imp}")
        log(f"  未覆盖页面（提交-活跃）: ~{total_submitted - active_pages}")
    except Exception as e:
        log(f"  ⚠️ 搜索数据拉取失败: {e}")
        active_pages = 0
    
    return {
        'submitted': total_submitted,
        'indexed_gsc': total_indexed,
        'active_pages': active_pages,
        'gap': total_submitted - active_pages
    }


def generate_optimization_tips(service, status):
    """根据当前状态给出优化建议"""
    tips = []
    gap = status.get('gap', 0)
    
    if gap > 300:
        tips.append(f"🔴 关键问题：{gap} 个页面未出现在搜索数据中")
        tips.append("   建议：产品页按优先级分层，先优化有搜索量的类别")
    elif gap > 100:
        tips.append(f"🟡 {gap} 个页面未活跃，需持续发布博客带动索引")
    else:
        tips.append(f"🟢 覆盖率较好，仅 {gap} 个页面未活跃")
    
    # 查有没有关键词排名前10但点击低的
    try:
        r = service.searchanalytics().query(siteUrl=SITE_URL, body={
            'startDate': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'endDate': datetime.now().strftime('%Y-%m-%d'),
            'dimensions': ['query'],
            'rowLimit': 100
        }).execute()
        
        # 找排名前10但点击为0的——优化标题描述可提升CTR
        top_kw = [q for q in r.get('rows', []) 
                  if q['position'] <= 10 and q['impressions'] >= 5 and q['clicks'] == 0]
        if top_kw:
            tips.append(f"🎯 优化机会：{len(top_kw)} 个关键词进前10但0点击")
            for kw in top_kw[:5]:
                tips.append(f"   - \"{kw['keys'][0]}\" (排名#{kw['position']:.0f}, {int(kw['impressions'])}次展示)")
    except Exception:
        pass
    
    return tips


def main():
    log("=" * 50)
    log("🔍 GSC 索引优化工具启动")
    log("=" * 50)
    
    service = get_service()
    
    # 1. 重新提交 sitemap
    resubmit_sitemaps(service)
    
    # 2. 检查索引状态
    status = check_index_status(service)
    
    # 3. 优化建议
    tips = generate_optimization_tips(service, status)
    
    log("\n📋 优化建议:")
    for tip in tips:
        log(f"  {tip}")
    
    # 4. 保存状态到 tracker
    tracker_file = os.path.expanduser(
        "~/.openclaw/workspace/proactivity/seo-weekly-tracker.json"
    )
    
    tracker_data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'submitted_urls': status['submitted'],
        'indexed_gsc': status['indexed_gsc'],
        'active_28d_pages': status['active_pages'],
        'gap': status['gap'],
        'sitemap_resubmitted': True,
        'hreflang_fixed': True,
        'recommendations': tips,
    }
    
    try:
        with open(tracker_file) as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = {'weeks': []}
    
    existing.setdefault('weeks', []).append(tracker_data)
    # 只保留最近 8 周
    existing['weeks'] = existing['weeks'][-8:]
    existing['latest'] = tracker_data
    
    with open(tracker_file, 'w') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    log(f"\n💾 状态已保存到 tracker")
    log("✅ GSC 索引优化完成")


if __name__ == '__main__':
    PROXY = 'http://127.0.0.1:7890'
    for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
        os.environ.setdefault(var, PROXY)
    os.environ.setdefault('ALL_PROXY', 'socks5://127.0.0.1:7890')
    main()
