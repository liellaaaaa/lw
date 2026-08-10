# -*- coding: utf-8 -*-
import urllib.request, re, sys
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        html = urllib.request.urlopen(req, timeout=25).read().decode('utf-8','ignore')
        return html
    except Exception as e:
        return f"__ERR__ {e}"

urls = {
 '生意社_detail_chance_TDI': 'https://stock.100ppi.com/detail_chance-97078.html',
 '生意社_detail_chance_DMC': 'https://stock.100ppi.com/detail_chance-97082.html',
 '生意社_pdata_环氧树脂': 'https://pdata.100ppi.com/?dir=hghy&f=basket_cap&id=1304',
 '生意社_pdata_聚合MDI': 'https://pdata.100ppi.com?dir=hghy&f=basket&id=975',
 '金投网_黄金': 'https://www.cngold.org/c/2026-08-10/c10678565.html',
 'CBC_黄磷': 'https://www.cbcie.com/102573/12/list.html',
 '新浪_液化天然气': 'https://finance.sina.com.cn/money/future/nyzx/2026-08-10/doc-inimuvrt2881458.shtml',
 '生意社_玉米': 'https://www.100ppi.com/news/detail-20260810-6042708.html',
}
for k, u in urls.items():
    html = fetch(u)
    if html.startswith('__ERR__'):
        print(f"[{k}] FETCH FAIL: {html}")
        continue
    print(f"[{k}] len={len(html)}")
    # look for number-ish price tokens
    nums = re.findall(r'(?:价格|报价|均价|元/吨|美元/桶|元/克)[^<]{0,40}', html)
    print('  价格片段:', nums[:3])
    # crude: first big number near 元/吨
    m = re.search(r'([\d,]+(?:\.\d+)?)\s*元/吨', html)
    print('  元/吨匹配:', m.group(0) if m else '无')
