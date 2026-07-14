#!/usr/bin/env python3
"""
GSC 索引问题全面诊断工具
拉取未编入索引页面列表、原因、以及每个产品的索引状态
"""

import os
import json
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 代理
PROXY = 'http://127.0.0.1:7890'
os.environ.setdefault('HTTP_PROXY', PROXY)
os.environ.setdefault('HTTPS_PROXY', PROXY)
os.environ.setdefault('http_proxy', PROXY)
os.environ.setdefault('https_proxy', PROXY)
os.environ.setdefault('ALL_PROXY', 'socks5://127.0.0.1:7890')

# 加载凭据
gsc_env = os.path.expanduser("~/.gsc.env")
if os.path.exists(gsc_env):
    load_dotenv(gsc_env)

SITE_URL = "sc-domain:jh-hardware.com"
TOKEN_FILE = os.path.expanduser("~/.openclaw/service-env/gsc-oauth-token.json")

SCOPES = ['https://www.googleapis.com/auth/webmasters']

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.environ.get("GSC_INSTALLED_CLIENT_ID", ""),
        "project_id": os.environ.get("GSC_PROJECT_ID", "gsc-497208"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ.get("GSC_INSTALLED_CLIENT_SECRET", ""),
        "redirect_uris": ["http://localhost:8080"]
    }
}


def get_service():
    """获取已认证的 GSC 服务"""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE) as f:
                data = json.load(f)
            # 补充缺失的字段
            if 'client_id' not in data:
                data['client_id'] = CLIENT_CONFIG['installed']['client_id']
            if 'client_secret' not in data:
                data['client_secret'] = CLIENT_CONFIG['installed']['client_secret']
            if 'token_uri' not in data:
                data['token_uri'] = 'https://oauth2.googleapis.com/token'
            creds = Credentials.from_authorized_user_info(data, SCOPES)
            print(f"✅ Token 加载成功")
        except Exception as e:
            print(f"⚠️ Token 加载失败: {e}")

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            print("✅ Token 已刷新")
            # 保存刷新后的 token
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())
            print("💾 Token 已保存")
        except Exception as e:
            print(f"⚠️ Token 刷新失败: {e}")
            creds = None

    if not creds or not creds.valid:
        print("🔑 需要重新授权，请在浏览器中登录 Google 账号...")
        flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
        creds = flow.run_local_server(port=8082, open_browser=True)
        print("✅ 授权成功")
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
        print("💾 Token 已保存")

    service = build('searchconsole', 'v1', credentials=creds)
    return service


def get_index_coverage(service):
    """
    使用 GSC API 获取索引覆盖率
    """
    print("\n" + "=" * 60)
    print("📊 1. 索引覆盖率概览")
    print("=" * 60)
    
    from googleapiclient.errors import HttpError
    
    # 用 sitemaps.list 看 sitemap 提交情况
    print("\n📄 Sitemap 提交状态:")
    try:
        sitemaps = service.sitemaps().list(siteUrl=SITE_URL).execute()
        for s in sitemaps.get('sitemap', []):
            path = s['path'].replace('https://jh-hardware.com/', '/')[:60]
            errors = s.get('errors', 0)
            warnings = s.get('warnings', 0)
            contents = s.get('contents', [])
            submitted_raw = contents[0].get('submitted', 0) if contents else 0
            indexed_raw = contents[0].get('indexed', 0) if contents else 0
            submitted = int(submitted_raw) if isinstance(submitted_raw, str) and submitted_raw.isdigit() else submitted_raw
            indexed = int(indexed_raw) if isinstance(indexed_raw, str) and indexed_raw.isdigit() else indexed_raw
            pct = f"{indexed/submitted*100:.1f}%" if isinstance(submitted, int) and submitted > 0 and isinstance(indexed, int) else '?'
            status = '✅' if errors == 0 else '❌'
            print(f"  {status} {path}")
            print(f"     提交: {submitted}, 已索引: {indexed} ({pct}), 错误: {errors}, 警告: {warnings}")
            for c in contents:
                print(f"     类型: {c.get('type', '?')}, 提交: {c.get('submitted', '?')}, 已索引: {c.get('indexed', '?')}")
    except HttpError as e:
        print(f"  ❌ 查询失败: {e}")
        if 'notFound' in str(e):
            # 可能是 siteUrl 格式问题，试试带协议的
            try:
                site_url_http = "https://jh-hardware.com"
                sitemaps = service.sitemaps().list(siteUrl=site_url_http).execute()
                print(f"  ✅ 用 {site_url_http} 查询成功")
                for s in sitemaps.get('sitemap', []):
                    print(f"    {s['path'][:70]}: 错误={s.get('errors',0)}, 提交={s.get('contents',[{}])[0].get('submitted','?') if s.get('contents') else '?'}")
            except Exception as e2:
                print(f"  ❌ 也失败了: {e2}")


def check_url_inspection(service, urls, batch_size=5):
    """
    批量检查 URL 索引状态
    """
    from googleapiclient.errors import HttpError
    
    print("\n" + "=" * 60)
    print("🔍 2. 样本 URL 索引检查")
    print("=" * 60)
    
    results = {'indexed': [], 'not_indexed': [], 'error': []}
    
    for i, url in enumerate(urls):
        if i >= batch_size:
            break
        try:
            body = {'inspectionUrl': url, 'siteUrl': SITE_URL}
            resp = service.urlInspection().index(body=body).execute()
            status = resp.get('inspectionResult', {}).get('indexStatusResult', {})
            verdict = status.get('verdict', 'UNKNOWN')
            coverage = status.get('coverageState', 'UNKNOWN')
            print(f"  {'✅' if verdict == 'PASS' else '❌'} {url[:70]}")
            print(f"     定论: {verdict}, 覆盖状态: {coverage}")
            if verdict != 'PASS':
                results['not_indexed'].append({'url': url, 'verdict': verdict, 'coverage': coverage})
            else:
                results['indexed'].append(url)
        except HttpError as e:
            print(f"  ⚠️ {url[:70]}: {e}")
            results['error'].append({'url': url, 'error': str(e)})
        time.sleep(0.3)  # 避免限流
    
    print(f"\n  检查 {batch_size} 个 URL:")
    print(f"    已索引: {len(results['indexed'])}")
    print(f"    未索引: {len(results['not_indexed'])}")
    print(f"    出错: {len(results['error'])}")
    
    return results


def get_all_sitemap_urls():
    """从服务器获取 sitemap 中的所有 URL"""
    import urllib.request
    import xml.etree.ElementTree as ET
    
    print("\n" + "=" * 60)
    print("🗺️ 3. Sitemap URL 统计")
    print("=" * 60)
    
    all_urls = []
    
    try:
        # 获取主 sitemap
        req = urllib.request.Request('https://jh-hardware.com/sitemap.xml', 
                                     headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        tree = ET.parse(resp)
        root = tree.getroot()
        
        # 处理命名空间
        ns = None
        for _, v in root.tag:
            if 'sitemap' in v:
                ns = v
                break
        if ns:
            ns = '{' + ns + '}'
            loc_tag = ns + 'loc'
        else:
            loc_tag = 'loc'
        
        # 检查是 sitemapindex 还是 urlset
        is_index = root.tag.endswith('sitemapindex')
        
        if is_index:
            # sitemapindex -> 子 sitemap
            sub_sitemaps = [loc.text for loc in root.findall(f'.//{loc_tag}')]
            print(f"  主 sitemap 包含 {len(sub_sitemaps)} 个子 sitemap:")
            
            for ss in sub_sitemaps:
                print(f"    获取: {ss[:70]}...")
                time.sleep(0.5)
                try:
                    sreq = urllib.request.Request(ss, headers={'User-Agent': 'Mozilla/5.0'})
                    sresp = urllib.request.urlopen(sreq, timeout=15)
                    stree = ET.parse(sresp)
                    sroot = stree.getroot()
                    
                    # 提取 url
                    u_tag = loc_tag  # urlset 的 namespace 一样
                    urls_in_ss = [u.text for u in sroot.findall(f'.//{u_tag}')]
                    all_urls.extend(urls_in_ss)
                    print(f"      → {len(urls_in_ss)} 个 URL")
                except Exception as e:
                    print(f"      ❌ 读取失败: {e}")
        else:
            # 直接 urlset
            urls = [loc.text for loc in root.findall(f'.//{loc_tag}')]
            all_urls.extend(urls)
            print(f"  直接包含 {len(urls)} 个 URL")
        
        print(f"\n  📊 总计: {len(all_urls)} 个 URL")
        
        # 按语言统计
        en = [u for u in all_urls if '/en/' in u]
        zh = [u for u in all_urls if '/zh/' in u]
        ar = [u for u in all_urls if '/ar/' in u]
        other = [u for u in all_urls if u not in en and u not in zh and u not in ar]
        print(f"    英文: {len(en)}")
        print(f"    中文: {len(zh)}")
        print(f"    阿拉伯语: {len(ar)}")
        print(f"    其他: {len(other)}")
        
    except Exception as e:
        print(f"  ❌ 读取 sitemap 失败: {e}")
        import traceback
        traceback.print_exc()
    
    return all_urls


def get_gsc_performance_summary(service):
    """获取性能数据摘要"""
    from googleapiclient.errors import HttpError
    
    print("\n" + "=" * 60)
    print("📈 4. GSC 效果数据（近90天）")
    print("=" * 60)
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    body = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['query'],
        'rowLimit': 10,
        'orderBy': [{'fieldName': 'impressions', 'sortOrder': 'DESCENDING'}]
    }
    
    try:
        response = service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
        rows = response.get('rows', [])
        total_clicks = sum(r.get('clicks', 0) for r in rows)
        total_imps = sum(r.get('impressions', 0) for r in rows)
        print(f"  数据范围: {start_date} ~ {end_date}")
        print(f"  总展示: {total_imps}")
        print(f"  总点击: {total_clicks}")
        if total_imps:
            print(f"  平均 CTR: {total_clicks/total_imps*100:.2f}%")
        print()
        print("  Top 10 查询:")
        print(f"  {'#':>3} {'关键词':<35} {'点击':>5} {'展示':>7} {'CTR':>7} {'排名':>5}")
        print(f"  {'-'*65}")
        for i, row in enumerate(rows[:10], 1):
            kw = row['keys'][0][:34]
            print(f"  {i:3} {kw:<35} {row['clicks']:5} {row['impressions']:7} {row['ctr']*100:6.1f}% {row['position']:5.1f}")
    except HttpError as e:
        print(f"  ❌ 查询失败: {e}")


def check_product_indexing(service, product_urls):
    """专门检查产品页面的索引情况"""
    from googleapiclient.errors import HttpError
    
    print("\n" + "=" * 60)
    print("🏷️ 5. 产品页面抽样索引检查")
    print("=" * 60)
    
    # 抽样：每种语言选几个产品检查
    samples = []
    en_products = [u for u in product_urls if '/en/products/' in u]
    zh_products = [u for u in product_urls if '/zh/products/' in u]
    ar_products = [u for u in product_urls if '/ar/products/' in u]
    
    samples.extend(en_products[:3])
    if len(en_products) > 5:
        samples.extend(en_products[-2:])  # 最后两个
    
    if zh_products:
        samples.append(zh_products[0])
    if ar_products:
        samples.append(ar_products[0])
    
    results = {'passed': 0, 'failed': 0}
    
    for url in samples:
        try:
            body = {'inspectionUrl': url, 'siteUrl': SITE_URL}
            resp = service.urlInspection().index(body=body).execute()
            result = resp.get('inspectionResult', {}).get('indexStatusResult', {})
            verdict = result.get('verdict', 'UNKNOWN')
            coverage = result.get('coverageState', 'UNKNOWN')
            status = '✅' if verdict == 'PASS' else '❌'
            print(f"  {status} {url[:65]}")
            print(f"     定论={verdict}, 覆盖={coverage}, 用户判定={result.get('userState', '?')}")
            if verdict == 'PASS':
                results['passed'] += 1
            else:
                results['failed'] += 1
        except HttpError as e:
            print(f"  ⚠️ {url[:65]}: {e}")
        time.sleep(0.3)
    
    print(f"\n  抽样结果: {results['passed']} 已索引, {results['failed']} 未索引")
    return results


def main():
    print("=" * 60)
    print("🔎 jh-hardware.com GSC 索引问题全面诊断")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 获取服务
    service = get_service()
    
    # 2. 索引覆盖率概览
    get_index_coverage(service)
    
    # 3. 获取所有 sitemap URL
    all_urls = get_all_sitemap_urls()
    
    # 4. 性能数据摘要
    get_gsc_performance_summary(service)
    
    # 5. 抽样检查 URL 索引状态
    if all_urls:
        # 检查首页和几种类型
        sample_urls = [
            'https://jh-hardware.com/',
            'https://jh-hardware.com/en/',
            'https://jh-hardware.com/zh/',
            'https://jh-hardware.com/ar/',
        ]
        # 加上 sitemap 里前几个
        sample_urls.extend(all_urls[:5])
        
        check_url_inspection(service, sample_urls, batch_size=10)
        
        # 6. 产品页面专门检查
        check_product_indexing(service, all_urls)
    
    print("\n" + "=" * 60)
    print("✅ 诊断完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
