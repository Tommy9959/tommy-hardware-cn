#!/usr/bin/env python3
"""
Google Search Console API v2 — 支持 OAuth 桌面应用授权
用主人自己的 Google 账号授权，不需要 service account

首次使用：
  python3 gsc-api-setup.py --auth     # 浏览器打开授权页面，点允许即可
之后：
  python3 gsc-api-setup.py --report   # 直接拉数据
  
每周日 09:00 crontab 自动运行
"""

import os
import json
import argparse
import webbrowser
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

SITE_URL = "sc-domain:jh-hardware.com"
SITE_URL_HTTP = "https://jh-hardware.com"
TOKEN_FILE = os.path.expanduser("~/.openclaw/service-env/gsc-oauth-token.json")
CLIENT_ID = "1007540485512-1234567890abcdef.apps.googleusercontent.com"
CLIENT_SECRET = "GOCSPX-xxxxxxxxxxxx"

# OAuth 2.0 配置
# 使用 Google 的公共 OAuth 客户端（已配置好 Search Console API 范围）
CLIENT_CONFIG = {
    "installed": {
        "client_id": "14568524996-1ulgjerdda3ajt8df16rco3pnlv70a64.apps.googleusercontent.com",
        "project_id": "gsc-497208",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://localhost:8080"]
    }
}

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def get_authenticated_service():
    """获取已认证的 GSC 服务"""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    
    creds = None
    
    # 尝试加载已保存的 token
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE) as f:
                creds = Credentials.from_authorized_user_info(json.load(f), SCOPES)
        except Exception as e:
            log(f"⚠️ Token 加载失败: {e}")
    
    # 如果 token 过期，刷新
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            log("✅ Token 已刷新")
        except Exception as e:
            log(f"⚠️ Token 刷新失败，需重新授权: {e}")
            creds = None
    
    # 如果没有有效 token，启动 OAuth 流程
    if not creds or not creds.valid:
        log("🔑 需要授权，请在浏览器中登录 Google 账号...")
        flow = InstalledAppFlow.from_client_config(
            CLIENT_CONFIG, SCOPES)
        creds = flow.run_local_server(port=8080, open_browser=True)
        log("✅ 授权成功")
        
        # 保存 token
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
        log(f"💾 Token 已保存到: {TOKEN_FILE}")
    
    service = build('searchconsole', 'v1', credentials=creds)
    return service


def test_connection(service):
    """测试 GSC API 连接"""
    sites = service.sites().list().execute()
    site_urls = [s['siteUrl'] for s in sites.get('siteEntry', [])]
    
    log(f"✅ GSC API 连接成功！")
    log(f"📋 已验证的网站 ({len(site_urls)}):")
    for url in site_urls:
        log(f"   ✅ {url}")
    
    # 检查 SITE_URL 或 SITE_URL_HTTP 是否在列表中
    found = SITE_URL in site_urls
    if not found:
        found = SITE_URL_HTTP in site_urls
    return found


def get_performance_data(service, days=90):
    """获取 GSC 效果数据"""
    from googleapiclient.errors import HttpError
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    requests_config = {
        'queries': {'dimensions': ['query'], 'rowLimit': 25, 'orderBy': [{'fieldName': 'impressions', 'sortOrder': 'DESCENDING'}]},
        'pages': {'dimensions': ['page'], 'rowLimit': 25, 'orderBy': [{'fieldName': 'impressions', 'sortOrder': 'DESCENDING'}]},
        'countries': {'dimensions': ['country'], 'rowLimit': 10, 'orderBy': [{'fieldName': 'impressions', 'sortOrder': 'DESCENDING'}]},
    }
    
    results = {}
    for name, dims in requests_config.items():
        try:
            body = {'startDate': start_date, 'endDate': end_date, **dims}
            response = service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
            results[name] = response.get('rows', [])
        except HttpError as e:
            log(f"⚠️ 获取 {name} 失败: {e}")
            results[name] = []
    
    return results, start_date, end_date


def generate_report(service, output=None):
    """生成完整的 SEO 分析报告"""
    results, start_date, end_date = get_performance_data(service)
    
    total_clicks = sum(r.get('clicks', 0) for r in results.get('queries', []))
    total_impressions = sum(r.get('impressions', 0) for r in results.get('queries', []))
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    
    report = []
    report.append(f"# 📊 jh-hardware.com SEO 周报")
    report.append(f"")
    report.append(f"**数据范围：** {start_date} ~ {end_date}")
    report.append(f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"")
    report.append(f"---")
    report.append(f"")
    
    # 整体概览
    report.append(f"## 📈 整体概览")
    report.append(f"")
    report.append(f"| 指标 | 数值 |")
    report.append(f"|------|------|")
    report.append(f"| 总点击 | {total_clicks} |")
    report.append(f"| 总展示 | {total_impressions} |")
    report.append(f"| 平均 CTR | {avg_ctr:.1f}% |")
    report.append(f"")
    
    # 关键词
    report.append(f"## 🔍 热门关键词（Top 25）")
    report.append(f"")
    report.append(f"| # | 关键词 | 点击 | 展示 | CTR | 排名 |")
    report.append(f"|---|--------|------|------|-----|------|")
    for i, row in enumerate(results.get('queries', [])[:25], 1):
        report.append(
            f"| {i} | {row['keys'][0][:40]} | {row['clicks']} | {row['impressions']} | "
            f"{row['ctr']:.1%} | {row['position']:.1f} |"
        )
    report.append(f"")
    
    # 页面
    report.append(f"## 📄 热门页面（Top 25）")
    report.append(f"")
    report.append(f"| # | 页面 | 点击 | 展示 | CTR | 排名 |")
    report.append(f"|---|------|------|------|-----|------|")
    for i, row in enumerate(results.get('pages', [])[:25], 1):
        page = row['keys'][0].replace(SITE_URL, '').strip('/') or '/'
        report.append(
            f"| {i} | /{page[:50]} | {row['clicks']} | {row['impressions']} | "
            f"{row['ctr']:.1%} | {row['position']:.1f} |"
        )
    report.append(f"")
    
    # 国家
    report.append(f"## 🌍 流量来源国家（Top 10）")
    report.append(f"")
    report.append(f"| # | 国家 | 点击 | 展示 | CTR | 排名 |")
    report.append(f"|---|------|------|------|-----|------|")
    for i, row in enumerate(results.get('countries', [])[:10], 1):
        report.append(
            f"| {i} | {row['keys'][0]} | {row['clicks']} | {row['impressions']} | "
            f"{row['ctr']:.1%} | {row['position']:.1f} |"
        )
    report.append(f"")
    
    # 优化建议 - 使用 SITE_URL 前缀匹配
    site_prefix = SITE_URL.replace('sc-domain:', 'https://') + '/' if 'sc-domain' in SITE_URL else SITE_URL
    
    report.append(f"## 🎯 优化建议")
    report.append(f"")
    
    low_ctr = [r for r in results.get('queries', []) if r['impressions'] > 100 and r['ctr'] < 0.02]
    if low_ctr:
        report.append(f"### 🔴 高展示低点击")
        report.append(f"以下关键词展示多但点击少，建议优化标题/描述：")
        report.append(f"")
        for r in low_ctr[:5]:
            report.append(f"- **{r['keys'][0]}** → {r['impressions']}次展示 / {r['clicks']}次点击 (CTR {r['ctr']:.1%})")
        report.append(f"")
    
    near_top = [r for r in results.get('pages', []) if 5 <= r['position'] <= 10 and r['impressions'] > 50]
    if near_top:
        report.append(f"### 🟡 有潜力进前5")
        report.append(f"以下页面排名5-10位，优化可冲首页：")
        report.append(f"")
        for r in sorted(near_top, key=lambda x: x['position'])[:5]:
            page = r['keys'][0].replace(site_prefix, '').strip('/') or '/'
            report.append(f"- /{page[:50]} → 排名 {r['position']:.1f}")
        report.append(f"")
    
    top_kw = [r for r in results.get('queries', []) if r['position'] <= 3 and r['impressions'] > 50]
    if top_kw:
        report.append(f"### 🟢 排名前三的强项")
        report.append(f"以下关键词在首页，继续保持：")
        report.append(f"")
        for r in sorted(top_kw, key=lambda x: x['clicks'], reverse=True)[:5]:
            report.append(f"- **{r['keys'][0][:40]}** → 排名 {r['position']:.1f}")
        report.append(f"")
    
    report.append(f"---")
    report.append(f"*自动生成*")
    
    report_text = '\n'.join(report)
    print(report_text)
    
    if output:
        with open(output, 'w') as f:
            f.write(report_text)
        log(f"📝 报告已保存: {output}")
    
    return report_text


def main():
    parser = argparse.ArgumentParser(description='GSC 数据分析工具')
    parser.add_argument('--auth', action='store_true', help='首次授权（浏览器登录）')
    parser.add_argument('--test', action='store_true', help='测试连接')
    parser.add_argument('--report', action='store_true', help='生成周报')
    parser.add_argument('--output', default=None, help='报告输出路径')
    args = parser.parse_args()
    
    if args.auth:
        log("🔑 正在打开浏览器进行 Google 授权...")
        log("登录你的 Google 账号（就是管理 Search Console 的那个账号）")
        log("点击允许后，token 会自动保存，以后就不用再授权了")
        service = get_authenticated_service()
        test_connection(service)
        return
    
    if args.test:
        service = get_authenticated_service()
        test_connection(service)
        return
    
    if args.report:
        service = get_authenticated_service()
        if test_connection(service):
            if args.output:
                generate_report(service, args.output)
            else:
                output = os.path.expanduser(f"~/Sites/hardware-site/docs/gsc-weekly-{datetime.now().strftime('%Y%m%d')}.md")
                generate_report(service, output)
        return
    
    print("使用方法：")
    print("  首次授权：  python3 gsc-api-setup.py --auth")
    print("  测试连接：  python3 gsc-api-setup.py --test")
    print("  生成周报：  python3 gsc-api-setup.py --report")


if __name__ == '__main__':
    # 设置代理（如果有）
    for env_var in ['HTTPS_PROXY', 'HTTP_PROXY', 'ALL_PROXY']:
        if not os.environ.get(env_var):
            os.environ[env_var] = 'http://127.0.0.1:7890'
    main()
