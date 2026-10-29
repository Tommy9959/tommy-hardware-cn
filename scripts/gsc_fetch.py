#!/usr/bin/env python3
"""
gsc_fetch.py — 用 requests 直连 Search Console REST API 拉数据
（不用 googleapiclient/httplib2：httplib2 不认 HTTP_PROXY，在代理环境下会超时）

用法:
  python gsc_fetch.py --days 90
  python gsc_fetch.py --days 28 --raw          # 输出 JSON（给周报脚本用）
  python gsc_fetch.py --sites                  # 只列出已验证站点
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta

PROXY = 'http://127.0.0.1:7890'
os.environ.setdefault('HTTP_PROXY', PROXY)
os.environ.setdefault('HTTPS_PROXY', PROXY)
os.environ.setdefault('http_proxy', PROXY)
os.environ.setdefault('https_proxy', PROXY)

TOKEN_FILE = os.path.expanduser('~/.openclaw/service-env/gsc-oauth-token.json')
SCOPES = ['https://www.googleapis.com/auth/webmasters']
API = 'https://searchconsole.googleapis.com/webmasters/v3'
DEFAULT_SITE = 'sc-domain:jh-hardware.com'


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", file=sys.stderr)


def session():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import AuthorizedSession
    if not os.path.exists(TOKEN_FILE):
        log(f"❌ 找不到 token: {TOKEN_FILE}")
        sys.exit(2)
    creds = Credentials.from_authorized_user_info(json.load(open(TOKEN_FILE)), SCOPES)
    return AuthorizedSession(creds)


def list_sites(sess):
    r = sess.get(f'{API}/sites', timeout=60)
    r.raise_for_status()
    return [s['siteUrl'] for s in r.json().get('siteEntry', [])]


def query(sess, site, start, end, dims=None, limit=25):
    body = {'startDate': start, 'endDate': end, 'rowLimit': limit}
    if dims:
        body['dimensions'] = dims
    url = f'{API}/sites/{site.replace("/", "%2F")}/searchAnalytics/query'
    r = sess.post(url, json=body, timeout=90)
    r.raise_for_status()
    return r.json().get('rows', [])


def build(days):
    sess = session()
    sites = list_sites(sess)
    if DEFAULT_SITE in sites:
        site = DEFAULT_SITE
    else:
        pref = [x for x in sites if x.startswith('sc-domain:')] or \
               [x for x in sites if 'jh-hardware' in x]
        site = (pref or sites or [None])[0]
    if not site:
        log("❌ 该授权账号下没有任何已验证的 Search Console 站点")
        sys.exit(3)

    end = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=days + 1)).strftime('%Y-%m-%d')

    overall = query(sess, site, start, end, dims=None, limit=1)
    q = overall[0] if overall else {}
    total_imp = int(q.get('impressions', 0))
    total_clicks = int(q.get('clicks', 0))

    queries = query(sess, site, start, end, ['query'], 25)
    pages = query(sess, site, start, end, ['page'], 25)
    countries = query(sess, site, start, end, ['country'], 15)
    dates = query(sess, site, start, end, ['date'], 200)

    result = {
        'site': site,
        'period': f'{days}天',
        'range': f'{start} ~ {end}',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total_impressions': total_imp,
        'total_clicks': total_clicks,
        'avg_ctr_percent': round(total_clicks / total_imp * 100, 1) if total_imp else 0,
        'avg_position': round(q.get('position', 0), 1),
        'top_queries': [
            {'keyword': r['keys'][0], 'impressions': int(r.get('impressions', 0)),
             'clicks': int(r.get('clicks', 0)), 'ctr': round(r.get('ctr', 0) * 100, 1),
             'position': round(r.get('position', 0), 1)} for r in queries
        ],
        'top_pages': [
            {'page': r['keys'][0].replace('https://jh-hardware.com', '').strip('/') or '/',
             'impressions': int(r.get('impressions', 0)), 'clicks': int(r.get('clicks', 0)),
             'ctr': round(r.get('ctr', 0) * 100, 1),
             'position': round(r.get('position', 0), 1)} for r in pages
        ],
        'top_countries': [
            {'country': r['keys'][0], 'impressions': int(r.get('impressions', 0)),
             'clicks': int(r.get('clicks', 0)),
             'position': round(r.get('position', 0), 1)} for r in countries
        ],
        'daily': [
            {'date': r['keys'][0], 'impressions': int(r.get('impressions', 0)),
             'clicks': int(r.get('clicks', 0))} for r in sorted(dates, key=lambda x: x['keys'][0])
        ],
    }
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=int, default=28)
    ap.add_argument('--raw', action='store_true', help='输出 JSON')
    ap.add_argument('--sites', action='store_true', help='只列出站点')
    a = ap.parse_args()

    if a.sites:
        for s in list_sites(session()):
            print('✅', s)
        return

    data = build(a.days)

    if a.raw:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print(f"\n📊 {data['site']}  {data['range']}（{data['period']}）")
    print(f"   点击 {data['total_clicks']}  展示 {data['total_impressions']}  "
          f"CTR {data['avg_ctr_percent']}%  平均排名 {data['avg_position']}")
    if data['top_queries']:
        print("\n🔍 关键词 Top15:")
        for r in data['top_queries'][:15]:
            print(f"   {r['impressions']:>5}展示 {r['clicks']:>3}点击  排名{r['position']:>5}  {r['keyword']}")
    if data['top_pages']:
        print("\n📄 页面 Top10:")
        for r in data['top_pages'][:10]:
            print(f"   {r['impressions']:>5}展示 {r['clicks']:>3}点击  排名{r['position']:>5}  {r['page']}")
    if data['top_countries']:
        print("\n🌍 国家 Top10:")
        for r in data['top_countries'][:10]:
            print(f"   {r['impressions']:>5}展示 {r['clicks']:>3}点击  {r['country']}")


if __name__ == '__main__':
    main()
