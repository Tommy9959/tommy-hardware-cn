#!/usr/bin/env python3
"""
Google Search Console API 集成脚本
用于自动拉取 jh-hardware.com 的 GSC 数据

使用方式：
1. 按照下方指引创建 Google Cloud 服务账号
2. 下载 JSON 密钥放到 ~/.openclaw/service-env/gsc-credentials.json
3. 运行本脚本获取数据
"""

import os
import json
import argparse
from datetime import datetime, timedelta

SITE_URL = "https://jh-hardware.com"
CREDENTIALS_FILE = os.path.expanduser("~/.openclaw/service-env/gsc-credentials.json")
VENV_PYTHON = "/tmp/gsc-venv/bin/python3"

GUIDE = f"""
╔══════════════════════════════════════════════════════════════╗
║  🚀 GSC API 快速设置指南                                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1️⃣  打开 Google Cloud Console                              ║
║     → https://console.cloud.google.com/                      ║
║                                                              ║
║  2️⃣  新建项目（或选已有项目）                                ║
║     → 项目名称：jh-hardware-gsc（随意）                     ║
║                                                              ║
║  3️⃣  启用 Search Console API                                ║
║     → API 和服务 → 启用 API 和服务                           ║
║     → 搜索 "Search Console API" → 启用                       ║
║                                                              ║
║  4️⃣  创建服务账号                                           ║
║     → API 和服务 → 凭据 → 创建凭据 → 服务账号               ║
║     → 名称：gsc-reader                                       ║
║     → 角色：基本 > 查看者（或者跳过，不重要）                ║
║                                                              ║
║  5️⃣  下载密钥                                               ║
║     → 进入刚创建的服务账号 → 密钥 → 添加密钥 → JSON        ║
║     → 下载后将文件保存到：                                    ║
║       ~/.openclaw/service-env/gsc-credentials.json           ║
║                                                              ║
║  6️⃣  在 GSC 中添加服务账号                                   ║
║     → 打开 https://search.google.com/search-console          ║
║     → 选择 jh-hardware.com 网站                              ║
║     → 设置 → 用户和权限 → 添加用户                          ║
║     → 输入服务账号邮箱（格式：xxx@xxx.iam.gserviceaccount.com）║
║     → 权限：完整（或仅限查看）                               ║
║                                                              ║
║  7️⃣  运行脚本                                               ║
║     python3 ~/Sites/hardware-site/scripts/gsc-api-setup.py   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

def check_credentials():
    """检查凭据文件是否存在"""
    if not os.path.exists(CREDENTIALS_FILE):
        print("❌ 未找到 GSC 凭据文件")
        print(GUIDE)
        return False
    print(f"✅ 凭据文件已存在: {CREDENTIALS_FILE}")
    return True

def test_connection():
    """测试 GSC API 连接"""
    import google.auth
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    
    SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
        service = build('searchconsole', 'v1', credentials=credentials)
        
        # 测试：获取网站列表
        sites = service.sites().list().execute()
        site_urls = [s['siteUrl'] for s in sites.get('siteEntry', [])]
        
        print(f"\n✅ GSC API 连接成功！")
        print(f"📋 已验证的网站 ({len(site_urls)}):")
        for url in site_urls:
            status = "✅" if url == SITE_URL else "  "
            print(f"   {status} {url}")
        
        if SITE_URL not in site_urls:
            print(f"\n⚠️ {SITE_URL} 不在已验证列表，请检查 GSC 设置")
            return None
        
        return service
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        return None

def get_performance_data(service, days=90):
    """获取 GSC 效果数据"""
    from googleapiclient.errors import HttpError
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # 按查询（关键词）分组
    query_request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['query'],
        'rowLimit': 25,
        'orderBy': [{'fieldName': 'impressions', 'sortOrder': 'DESCENDING'}]
    }
    
    # 按页面分组
    page_request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['page'],
        'rowLimit': 25,
        'orderBy': [{'fieldName': 'impressions', 'sortOrder': 'DESCENDING'}]
    }
    
    # 按国家分组
    country_request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['country'],
        'rowLimit': 10,
        'orderBy': [{'fieldName': 'impressions', 'sortOrder': 'DESCENDING'}]
    }
    
    results = {}
    
    for name, req in [('queries', query_request), ('pages', page_request), ('countries', country_request)]:
        try:
            response = service.searchanalytics().query(
                siteUrl=SITE_URL, body=req).execute()
            results[name] = response.get('rows', [])
        except HttpError as e:
            print(f"  ⚠️ 获取 {name} 失败: {e}")
            results[name] = []
    
    return results, start_date, end_date

def generate_report(service):
    """生成完整的 SEO 分析报告"""
    results, start_date, end_date = get_performance_data(service)
    
    report = []
    report.append(f"# 📊 jh-hardware.com Google Search Console 分析报告")
    report.append(f"")
    report.append(f"**数据范围：** {start_date} ~ {end_date}")
    report.append(f"")
    
    # 汇总
    total_clicks = sum(r.get('clicks', 0) for r in results.get('queries', []))
    total_impressions = sum(r.get('impressions', 0) for r in results.get('queries', []))
    total_ctr = sum(r.get('ctr', 0) for r in results.get('queries', [])) / max(len(results.get('queries', [])), 1)
    
    report.append(f"## 📈 整体概览")
    report.append(f"")
    report.append(f"| 指标 | 数值 |")
    report.append(f"|------|------|")
    report.append(f"| 总点击 | {total_clicks} |")
    report.append(f"| 总展示 | {total_impressions} |")
    report.append(f"| 平均 CTR | {total_ctr:.2%} |")
    report.append(f"")
    
    # 关键词分析
    report.append(f"## 🔍 热门关键词（Top 25）")
    report.append(f"")
    report.append(f"| 关键词 | 点击 | 展示 | CTR | 平均排名 |")
    report.append(f"|--------|------|------|-----|---------|")
    for row in results.get('queries', []):
        report.append(
            f"| {row['keys'][0][:40]} | {row['clicks']} | {row['impressions']} | "
            f"{row['ctr']:.1%} | {row['position']:.1f} |"
        )
    report.append(f"")
    
    # 页面分析
    report.append(f"## 📄 热门页面（Top 25）")
    report.append(f"")
    report.append(f"| 页面 | 点击 | 展示 | CTR | 平均排名 |")
    report.append(f"|------|------|------|-----|---------|")
    for row in results.get('pages', []):
        page = row['keys'][0].replace(SITE_URL, '').strip('/')
        report.append(
            f"| /{page[:50]} | {row['clicks']} | {row['impressions']} | "
            f"{row['ctr']:.1%} | {row['position']:.1f} |"
        )
    report.append(f"")
    
    # 国家分析
    report.append(f"## 🌍 流量来源国家")
    report.append(f"")
    report.append(f"| 国家 | 点击 | 展示 | CTR | 平均排名 |")
    report.append(f"|------|------|------|-----|---------|")
    for row in results.get('countries', []):
        country = row['keys'][0]
        report.append(
            f"| {country} | {row['clicks']} | {row['impressions']} | "
            f"{row['ctr']:.1%} | {row['position']:.1f} |"
        )
    report.append(f"")
    
    # 建议
    report.append(f"## 🎯 优化建议")
    report.append(f"")
    
    # 找出低 CTR 的高展示关键词
    low_ctr = [r for r in results.get('queries', []) if r['impressions'] > 100 and r['ctr'] < 0.02]
    if low_ctr:
        report.append(f"### 🔴 高展示低点击关键词（待优化）")
        report.append(f"以下关键词展示量高但点击率低，建议优化对应的页面标题和描述：")
        report.append(f"")
        for r in low_ctr[:5]:
            report.append(f"- **{r['keys'][0]}** — {r['impressions']} 次展示，仅 {r['clicks']} 次点击（CTR {r['ctr']:.1%}）")
        report.append(f"")
    
    # 找出排名 5-10 的页面（离首页一步之遥）
    near_top = [r for r in results.get('pages', []) if 5 <= r['position'] <= 10 and r['impressions'] > 50]
    if near_top:
        report.append(f"### 🟡 有潜力进入前5的页面")
        report.append(f"以下页面排名在第5-10位，优化后有机会进入首页：")
        report.append(f"")
        for r in sorted(near_top, key=lambda x: x['position'])[:5]:
            page = r['keys'][0].replace(SITE_URL, '').strip('/')
            report.append(f"- /{page[:50]} — 排名 {r['position']:.1f}，{r['impressions']} 次展示")
        report.append(f"")
    
    # Top 关键词
    top_kw = [r for r in results.get('queries', []) if r['position'] <= 3 and r['impressions'] > 50]
    if top_kw:
        report.append(f"### 🟢 排名前三的强项关键词")
        report.append(f"以下关键词已在首页，继续保持：")
        report.append(f"")
        for r in sorted(top_kw, key=lambda x: x['clicks'], reverse=True)[:5]:
            report.append(f"- **{r['keys'][0][:40]}** — 排名 {r['position']:.1f}，{r['clicks']} 次点击")
        report.append(f"")
    
    report.append(f"---")
    report.append(f"*自动生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    return '\n'.join(report)

def main():
    parser = argparse.ArgumentParser(description='Google Search Console API 工具')
    parser.add_argument('--guide', action='store_true', help='显示设置指南')
    parser.add_argument('--test', action='store_true', help='测试 GSC 连接')
    parser.add_argument('--report', action='store_true', help='生成 GSC 分析报告')
    parser.add_argument('--output', default=None, help='报告输出路径')
    args = parser.parse_args()
    
    if args.guide or not (args.test or args.report):
        print(GUIDE)
        return
    
    if not check_credentials():
        return
    
    if args.test:
        service = test_connection()
        return
    
    if args.report:
        service = test_connection()
        if not service:
            return
        report = generate_report(service)
        print("\n" + report)
        
        if args.output:
            os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\n📝 报告已保存到: {args.output}")
        else:
            output_path = f"~/Sites/hardware-site/docs/gsc-report-{datetime.now().strftime('%Y%m%d')}.md"
            with open(os.path.expanduser(output_path), 'w') as f:
                f.write(report)
            print(f"\n📝 报告已保存到: {output_path}")

if __name__ == '__main__':
    main()
