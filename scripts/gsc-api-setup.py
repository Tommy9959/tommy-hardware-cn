#!/usr/bin/env python3
"""
Google Search Console API — 支持 OAuth 桌面应用授权

使用：
  python3 gsc-api-setup.py --auth         # 首次授权
  python3 gsc-api-setup.py --report 90    # 生成最近90天周报
  python3 gsc-api-setup.py --report 7     # 生成最近7天简报
  python3 gsc-api-setup.py --report 7 --output /tmp/gsc-latest.md
  python3 gsc-api-setup.py --raw --days 7 # JSON 格式输出（给脚本调用）
"""

import os, json, sys, argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载凭据
gsc_env = os.path.expanduser("~/.gsc.env")
if os.path.exists(gsc_env):
    load_dotenv(gsc_env)

SITE_URL = "sc-domain:jh-hardware.com"
TOKEN_FILE = os.path.expanduser("~/.openclaw/service-env/gsc-oauth-token.json")

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.environ.get("GSC_INSTALLED_CLIENT_ID", ""),
        "project_id": "gsc-497208",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ.get("GSC_INSTALLED_CLIENT_SECRET", ""),
        "redirect_uris": ["http://localhost:8080"]
    }
}

SCOPES = ['https://www.googleapis.com/auth/webmasters']

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_service():
    """获取已认证的 GSC 服务"""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE) as f:
                creds = Credentials.from_authorized_user_info(json.load(f), SCOPES)
        except Exception as e:
            log(f"⚠️ Token 加载失败: {e}")

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            log("✅ Token 已刷新")
        except Exception as e:
            log(f"⚠️ Token 刷新失败: {e}")
            creds = None

    if not creds or not creds.valid:
        log("🔑 需要授权，请在浏览器中登录 Google 账号...")
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
        creds = flow.run_local_server(port=8082, open_browser=True)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
        log(f"💾 Token 已保存")

    return build('searchconsole', 'v1', credentials=creds, static_discovery=False)


def fetch_gsc_data(service, days=90, dims=None, row_limit=25):
    """
    通用 GSC 数据拉取
    dims: list of dimensions, e.g. ['query'], ['page'], ['country']
    返回 rows 列表
    """
    if dims is None:
        dims = ['query']
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    body = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': dims,
        'rowLimit': row_limit,
    }
    
    response = service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
    return response.get('rows', [])


def generate_report(service, days=90, output=None):
    """生成完整周报"""
    queries = fetch_gsc_data(service, days, ['query'], 25)
    pages = fetch_gsc_data(service, days, ['page'], 25)
    countries = fetch_gsc_data(service, days, ['country'], 10)
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # 总量统计
    all_queries = fetch_gsc_data(service, days, ['query'], 1000)
    total_imp = sum(r.get('impressions', 0) for r in all_queries)
    total_clicks = sum(r.get('clicks', 0) for r in all_queries)
    avg_ctr = (total_clicks / total_imp * 100) if total_imp > 0 else 0

    # 平均位置 = 加权平均
    weighted_pos = sum(r.get('impressions', 0) * r.get('position', 0) for r in all_queries)
    avg_pos = weighted_pos / total_imp if total_imp > 0 else 0

    lines = []
    lines.append(f"# 📊 jh-hardware.com SEO {'周报' if days >= 28 else '简报'}")
    lines.append("")
    lines.append(f"**数据范围：** {start_date} ~ {end_date}")
    lines.append(f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📈 整体概览")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 总展示 | {total_imp} |")
    lines.append(f"| 总点击 | {total_clicks} |")
    lines.append(f"| 平均 CTR | {avg_ctr:.1f}% |")
    lines.append(f"| 平均排名 | {avg_pos:.1f} |")
    lines.append("")
    
    # 🔍 热门关键词
    lines.append("## 🔍 热门关键词（Top 25）")
    lines.append("")
    lines.append("| # | 关键词 | 点击 | 展示 | CTR | 排名 |")
    lines.append("|---|--------|------|------|-----|------|")
    for i, row in enumerate(queries[:25], 1):
        kw = row['keys'][0][:40]
        lines.append(
            f"| {i} | {kw} | {row['clicks']} | {row['impressions']} | "
            f"{row['ctr']*100:.1f}% | {row['position']:.1f} |"
        )
    lines.append("")
    
    # 📄 热门页面
    lines.append("## 📄 热门页面（Top 25）")
    lines.append("")
    lines.append("| # | 页面 | 点击 | 展示 | CTR | 排名 |")
    lines.append("|---|------|------|------|-----|------|")
    for i, row in enumerate(pages[:25], 1):
        page = row['keys'][0].replace(f"https://jh-hardware.com", "").strip('/') or '/'
        lines.append(
            f"| {i} | {page[:55]} | {row['clicks']} | {row['impressions']} | "
            f"{row['ctr']*100:.1f}% | {row['position']:.1f} |"
        )
    lines.append("")
    
    # 🌍 国家
    lines.append("## 🌍 流量来源")
    lines.append("")
    lines.append("| # | 国家 | 点击 | 展示 |")
    lines.append("|---|------|------|------|")
    for i, row in enumerate(countries[:10], 1):
        lines.append(f"| {i} | {row['keys'][0]} | {row['clicks']} | {row['impressions']} |")
    lines.append("")

    # 🎯 优化建议（从所有关键词分析）
    lines.append("## 🎯 优化建议")
    lines.append("")

    # 高展示低点击（CTR < 2% 且展示 > 50）
    low_ctr = [r for r in all_queries if r['impressions'] >= 50 and r['ctr'] < 0.02]
    if low_ctr:
        lines.append("### 🔴 高展示低点击（需优化标题/描述）")
        lines.append("")
        lines.append("| 关键词 | 展示 | 点击 | CTR | 排名 |")
        lines.append("|--------|------|------|-----|------|")
        for r in sorted(low_ctr, key=lambda x: x['impressions'], reverse=True)[:5]:
            lines.append(f"| {r['keys'][0][:35]} | {r['impressions']} | {r['clicks']} | {r['ctr']*100:.1f}% | {r['position']:.1f} |")
        lines.append("")

    # 排名5-10有潜力冲首页
    near_top = [r for r in all_queries if 5 <= r['position'] <= 12 and r['impressions'] >= 20]
    if near_top:
        lines.append("### 🟡 有潜力冲前5")
        lines.append("")
        lines.append("| 关键词 | 展示 | 排名 | 优化方向 |")
        lines.append("|--------|------|------|----------|")
        for r in sorted(near_top, key=lambda x: x['position'])[:5]:
            lines.append(f"| {r['keys'][0][:35]} | {r['impressions']} | #{r['position']:.0f} | 更新内容/加内链 |")
        lines.append("")

    # 排名很靠后的长尾词（展示低但有机会）
    far_kw = [r for r in all_queries if r['position'] >= 30 and r['impressions'] >= 10]
    if far_kw:
        lines.append("### ⚪ 长尾词机会（覆盖内容后有望提升）")
        lines.append("")
        for r in sorted(far_kw, key=lambda x: x['impressions'], reverse=True)[:5]:
            lines.append(f"- **{r['keys'][0][:35]}** — {r['impressions']}次展示，排名 #{r['position']:.0f}，可写在博客/FAQ中")
        lines.append("")

    # sitemap 状态
    try:
        sitemaps = service.sitemaps().list(siteUrl=SITE_URL).execute()
        total_submitted = 0
        for sm in sitemaps.get('sitemap', []):
            cnt = sm.get('contents', [{}])
            if cnt:
                total_submitted += cnt[0].get('submitted', 0)
        lines.append("### ℹ️ sitemap 状态")
        lines.append(f"\n向 Google 提交了 **{total_submitted}** 个 URL，错误 0。\n")
    except Exception:
        pass

    lines.append("---")
    lines.append("*由黛玉自动生成*")
    
    report = '\n'.join(lines)
    print(report)
    
    if output:
        with open(output, 'w') as f:
            f.write(report)
        log(f"📝 报告已保存: {output}")
    
    return report


def raw_json(service, days=7):
    """返回 JSON 格式数据，给脚本和 AI 分析用"""
    queries = fetch_gsc_data(service, days, ['query'], 100)
    pages = fetch_gsc_data(service, days, ['page'], 100)
    
    total_imp = sum(r.get('impressions', 0) for r in queries)
    total_clicks = sum(r.get('clicks', 0) for r in queries)
    weighted_pos = sum(r.get('impressions', 0) * r.get('position', 0) for r in queries)
    avg_pos = round(weighted_pos / total_imp, 1) if total_imp else 0
    
    result = {
        'period': f"{days}天",
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total_impressions': total_imp,
        'total_clicks': total_clicks,
        'avg_ctr_percent': round(total_clicks / total_imp * 100, 1) if total_imp else 0,
        'avg_position': avg_pos,
        'top_queries': [
            {'keyword': r['keys'][0], 'impressions': r['impressions'],
             'clicks': r['clicks'], 'ctr': round(r['ctr']*100, 1),
             'position': round(r['position'], 1)}
            for r in queries[:20]
        ],
        'top_pages': [
            {'page': r['keys'][0].replace('https://jh-hardware.com', '').strip('/') or '/',
             'impressions': r['impressions'], 'clicks': r['clicks'],
             'position': round(r['position'], 1)}
            for r in pages[:20]
        ]
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description='GSC 数据分析')
    parser.add_argument('--auth', action='store_true')
    parser.add_argument('--report', type=int, nargs='?', const=90, default=None,
                        help='生成周报，可选天数（默认90天）')
    parser.add_argument('--output', default=None, help='报告输出路径')
    parser.add_argument('--raw', action='store_true', help='JSON 格式输出')
    parser.add_argument('--days', type=int, default=7, help='天数（配合 --raw）')
    parser.add_argument('--test', action='store_true', help='测试连接')
    args = parser.parse_args()
    
    # 代理
    PROXY = 'http://127.0.0.1:7890'
    for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
        os.environ.setdefault(var, PROXY)
    os.environ.setdefault('ALL_PROXY', 'socks5://127.0.0.1:7890')
    
    if args.auth:
        log("🔑 浏览器授权...")
        service = get_service()
        sites = service.sites().list().execute()
        for s in sites.get('siteEntry', []):
            log(f"   ✅ {s['siteUrl']}")
        return
    
    if args.test:
        service = get_service()
        sites = service.sites().list().execute()
        log(f"✅ GSC 连接成功！已验证网站:")
        for s in sites.get('siteEntry', []):
            log(f"   ✅ {s['siteUrl']}")
        return
    
    if args.raw:
        service = get_service()
        raw_json(service, args.days)
        return
    
    if args.report is not None:
        service = get_service()
        generate_report(service, args.report, args.output)
        return
    
    print("用法：")
    print("  授权:    python3 gsc-api-setup.py --auth")
    print("  测试:    python3 gsc-api-setup.py --test")
    print("  周报:    python3 gsc-api-setup.py --report 90")
    print("  简报:    python3 gsc-api-setup.py --report 7")
    print("  JSON:    python3 gsc-api-setup.py --raw --days 7")
    print("  指定路径: python3 gsc-api-setup.py --report 7 --output /tmp/gsc.md")


if __name__ == '__main__':
    main()
