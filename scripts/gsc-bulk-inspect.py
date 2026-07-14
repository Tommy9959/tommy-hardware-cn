#!/usr/bin/env python3
"""
GSC 批量 URL 索引状态检查
用 HTTPRequest 方式（google-api-python-client 原生）
"""
import os, json, time, sys
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest
from dotenv import load_dotenv

PROXY = 'http://127.0.0.1:7890'
os.environ.setdefault('HTTP_PROXY', PROXY)
os.environ.setdefault('HTTPS_PROXY', PROXY)
os.environ.setdefault('http_proxy', PROXY)
os.environ.setdefault('https_proxy', PROXY)
os.environ.setdefault('ALL_PROXY', 'socks5://127.0.0.1:7890')

load_dotenv(os.path.expanduser('~/.gsc.env'))

SITE_URL = 'sc-domain:jh-hardware.com'
TOKEN_FILE = os.path.expanduser('~/.openclaw/service-env/gsc-oauth-token.json')
SCOPES = ['https://www.googleapis.com/auth/webmasters']
OUTPUT = os.path.expanduser('~/.openclaw/workspace/logs/gsc-inspect-results.json')

with open(TOKEN_FILE) as f:
    data = json.load(f)
if 'client_id' not in data:
    data['client_id'] = os.environ.get('GSC_INSTALLED_CLIENT_ID', '')
    data['client_secret'] = os.environ.get('GSC_INSTALLED_CLIENT_SECRET', '')
    data['token_uri'] = 'https://oauth2.googleapis.com/token'

creds = Credentials.from_authorized_user_info(data, SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build('searchconsole', 'v1', credentials=creds)

def inspect_url(url):
    """检查单个 URL"""
    req = HttpRequest(
        http=service._http,
        postproc=lambda resp, content: (resp, json.loads(content)),
        uri='https://searchconsole.googleapis.com/v1/urlInspection/index:inspect',
        method='POST',
        body=json.dumps({'inspectionUrl': url, 'siteUrl': SITE_URL}),
        headers={'Content-Type': 'application/json'}
    )
    resp, data = req.execute()
    result = data.get('inspectionResult', {}).get('indexStatusResult', {})
    return {
        'url': url,
        'verdict': result.get('verdict', 'UNKNOWN'),
        'coverage': result.get('coverageState', 'UNKNOWN'),
        'crawled_as': result.get('crawledAs', 'UNKNOWN'),
        'page_fetch': result.get('pageFetchState', 'UNKNOWN'),
        'robots_txt': result.get('robotsTxtState', 'UNKNOWN'),
        'last_crawl': result.get('lastCrawlTime', 'N/A'),
    }


# === 获取所有 sitemap URL ===
import xml.etree.ElementTree as ET
import urllib.request

print("🔍 获取 sitemap URL...")
req = urllib.request.Request(
    'https://jh-hardware.com/sitemap.xml',
    headers={'User-Agent': 'Mozilla/5.0'}
)
resp = urllib.request.urlopen(req, timeout=15, context=None)
tree = ET.parse(resp)
root = tree.getroot()

ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
sub_sitemaps = [loc.text for loc in root.findall('.//s:loc', ns)]

all_urls = []
for ss in sub_sitemaps:
    time.sleep(0.3)
    try:
        sreq = urllib.request.Request(ss, headers={'User-Agent': 'Mozilla/5.0'})
        sresp = urllib.request.urlopen(sreq, timeout=15, context=None)
        stree = ET.parse(sresp)
        sroot = stree.getroot()
        urls = [u.text for u in sroot.findall('.//s:loc', ns)]
        lang = ss.split('/')[-2] if '/' in ss else '?'
        print(f"  {lang}: {len(urls)} URLs")
        all_urls.extend(urls)
    except Exception as e:
        print(f"  ❌ {ss}: {e}")

print(f"\n📊 总计 {len(all_urls)} 个 URL")

# === 按类型分组 ===
pages = {}
for u in all_urls:
    if '/blog/' in u:
        key = 'blog'
    elif '/products/' in u:
        # 检查是分类页还是产品页
        path = u.replace('https://jh-hardware.com', '')
        segments = [s for s in path.split('/') if s]
        if len(segments) >= 3:  # en/products/category/product
            key = 'product_detail'
        else:
            key = 'product_category'
    elif u == 'https://jh-hardware.com/' or u.endswith('/en/') or u.endswith('/zh/') or u.endswith('/ar/'):
        key = 'home'
    elif '/clients/' in u or '/about/' in u or '/contact/' in u:
        key = 'page'
    else:
        key = 'other'
    pages.setdefault(key, []).append(u)

for k, v in sorted(pages.items()):
    print(f"  {k}: {len(v)}")

# === 抽样检查 ===
results = {}
print("\n🔎 开始检查 URL 索引状态...")

# 全部检查所有页面
inspect_all = urls_to_check = []
for k in ['home', 'page', 'blog', 'product_category']:
    urls_to_check.extend(pages.get(k, []))

# 产品详情页只检查一部分（每种语言前10个和后5个）
products = pages.get('product_detail', [])
en_products = [u for u in products if '/en/' in u]
zh_products = [u for u in products if '/zh/' in u]
ar_products = [u for u in products if '/ar/' in u]

for plist in [en_products, zh_products, ar_products]:
    urls_to_check.extend(plist[:15])
    if len(plist) > 20:
        urls_to_check.extend(plist[-10:])

# 去重
urls_to_check = list(dict.fromkeys(urls_to_check))
print(f"  将要检查: {len(urls_to_check)} 个 URL\n")

passed = 0
failed = 0
for i, url in enumerate(urls_to_check):
    try:
        result = inspect_url(url)
        icon = '✅' if result['verdict'] == 'PASS' else '❌'
        print(f"  [{i+1}/{len(urls_to_check)}] {icon} {url[:65]}")
        print(f"      {result['verdict']} | {result['coverage']} | 爬取:{result['last_crawl'][:10]}")
        if result['verdict'] == 'PASS':
            passed += 1
        else:
            failed += 1
        results[url] = result
    except Exception as e:
        print(f"  [{i+1}/{len(urls_to_check)}] ⚠️ {url[:55]}: {e}")
        results[url] = {'url': url, 'error': str(e)}
    time.sleep(0.25)

# === 输出报告 ===
print("\n" + "=" * 60)
print("📊 检查结果汇总")
print("=" * 60)
print(f"  总计检查: {len(urls_to_check)}")
print(f"  已索引(✅): {passed}")
print(f"  未索引(❌): {failed}")
if failed > 0:
    print(f"  索引率: {passed/(passed+failed)*100:.1f}%")

# 列出未索引的页面
not_indexed = {k: v for k, v in results.items() if v.get('verdict') and v['verdict'] != 'PASS'}
if not_indexed:
    print(f"\n❌ 未编入索引的页面 ({len(not_indexed)}):")
    for url, info in sorted(not_indexed.items()):
        print(f"  ❌ {url}")
        print(f"     原因: {info.get('coverage', info.get('error', '未知'))}")

# 保存结果
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, 'w') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'total_urls': len(all_urls),
        'inspected': len(urls_to_check),
        'passed': passed,
        'failed': failed,
        'results': results
    }, f, indent=2, ensure_ascii=False)
print(f"\n💾 详细结果已保存: {OUTPUT}")
