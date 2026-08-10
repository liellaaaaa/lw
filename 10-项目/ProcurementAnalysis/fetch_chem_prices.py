# -*- coding: utf-8 -*-
"""
化工原料固定品类价格抓取脚本（多源 + 记录来源 URL）
- 主源：盖德化工网单品价格页 price/en/{cas}.html（49 项，纯 HTTP 可抓、每日更新）
- 缺口项（12 项，无稳定可构造 URL）：锚定上次检索值 + 记录来源链接 + 标"需复核"
  - 生意社(TDI/DMC/环氧树脂/聚合MDI/二丙二醇) 为 JS 渲染页，裸 HTTP 抓不到
  - 新浪/CBC/金投 的 URL 含日期+随机 ID，无法程序构造，需检索定位
- 输出：Markdown 行情表(每行带来源链接) + CSV
用法：python fetch_chem_prices.py
"""
import urllib.request, re, os, datetime, ssl

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
BASE = 'https://www.guidechem.com/price/en/{cas}.html'
OUT_DIR = os.path.join(os.path.dirname(__file__), '行情日报')

# (名称, 类别, CAS)  —— CAS=None 表示无单一化学品（聚合物/大宗商品/基准）
ITEMS = [
    ('AES 脂肪醇聚氧乙烯醚硫酸钠', '化工', '9004-82-4'),
    ('DMF', '化工', '68-12-2'),
    ('EGDA 乙二醇二乙酸酯', '化工', '111-55-7'),
    ('TDI 甲苯二异氰酸酯', '化工', '584-84-9'),
    ('苯酚', '化工', '108-95-2'),
    ('丙二醇甲醚醋酸酯 PMA', '化工', '108-65-6'),
    ('丙酮', '化工', '67-64-1'),
    ('丙烯', '化工', '115-07-1'),
    ('丙烯酸', '化工', '79-10-7'),
    ('丙烯酰胺', '化工', '79-06-1'),
    ('纯苯', '化工', '71-43-2'),
    ('醋酸', '化工', '64-19-7'),
    ('电石 碳化钙', '化工', '75-20-7'),
    ('丁酮肟 MEKO', '化工', '96-29-7'),
    ('二丙二醇', '化工', '25265-71-8'),
    ('二甘醇 二乙二醇', '化工', '111-46-6'),
    ('二甲胺水溶液', '化工', '124-40-3'),
    ('二乙醇胺', '化工', '111-42-2'),
    ('富马酸', '化工', '110-17-8'),
    ('过硫酸铵', '化工', '7727-54-0'),
    ('过硫酸钾', '化工', '7727-21-1'),
    ('过硫酸钠', '化工', '7775-27-1'),
    ('环氧丙烷', '化工', '75-56-9'),
    ('环氧氯丙烷', '化工', '106-89-8'),
    ('环氧树脂', '化工', None),
    ('环氧乙烷', '化工', '75-21-8'),
    ('黄磷', '化工', '7723-14-0'),
    ('甲醇', '化工', '67-56-1'),
    ('甲醛', '化工', '50-00-0'),
    ('焦亚硫酸钠', '化工', '7681-57-4'),
    ('聚丙烯酰胺', '化工', '9003-05-8'),
    ('聚合MDI', '化工', None),
    ('磷酸', '化工', '7664-38-2'),
    ('硫磺', '化工', '7704-34-9'),
    ('硫脲', '化工', '62-56-6'),
    ('硫酸', '化工', '7664-93-9'),
    ('硫酸二甲酯', '化工', '77-78-1'),
    ('硫酸二乙酯', '化工', '64-67-5'),
    ('尿素', '化工', '57-13-6'),
    ('轻质纯碱 碳酸钠', '化工', '497-19-8'),
    ('三乙醇胺', '化工', '102-71-6'),
    ('双氰胺', '化工', '461-58-5'),
    ('双氧水 过氧化氢', '化工', '7722-84-1'),
    ('顺酐 马来酸酐', '化工', '108-31-6'),
    ('盐酸', '化工', '7647-01-0'),
    ('一水柠檬酸', '化工', '5949-29-1'),
    ('衣康酸', '化工', '97-65-4'),
    ('乙二醇丁醚 EGBE', '化工', '111-76-2'),
    ('异丙醇', '化工', '67-63-0'),
    ('异辛醇 2-乙基己醇', '化工', '104-76-7'),
    ('油酸', '化工', '112-80-1'),
    ('有机硅DMC', '化工', '70131-67-8'),
    ('元明粉 无水硫酸钠', '化工', '7757-82-6'),
    ('精萘', '化工', '91-20-3'),
    ('液化天然气', '能源', None),
    ('Brent原油', '能源', None),
    ('WTI原油', '能源', None),
    ('玉米', '农副', None),
    ('棕榈油', '农副', None),
    ('金属硅', '有色', '7440-21-3'),
    ('黄金', '有色', '7440-57-5'),
]

# 缺口项锚定值（上次检索结果，需人工/检索刷新）：name -> (price, unit, date, url, note)
# 这些项无稳定可构造 URL 或源站 JS 渲染，脚本无法自动刷新，标"需复核"
MANUAL = {
    'TDI 甲苯二异氰酸酯': ('16500', '元/吨', '2026-08-10', 'https://stock.100ppi.com/detail_chance-97078.html', '生意社(JS页,需检索刷新)'),
    '二丙二醇': ('~10000', '元/吨', '2026-08-07', 'https://chem.100ppi.com/price/plist-1582--2.html', '生意社(JS页,需检索刷新)'),
    '环氧树脂': ('~14800-15400', '元/吨', '2026-08-07', 'https://pdata.100ppi.com/?dir=hghy&f=basket_cap&id=1304', '生意社(JS页,需检索刷新)'),
    '聚合MDI': ('~17600-18000', '元/吨', '2026-08-07', 'https://pdata.100ppi.com?dir=hghy&f=basket&id=975', '生意社(JS页,需检索刷新)'),
    '有机硅DMC': ('12000', '元/吨', '2026-08-10', 'https://stock.100ppi.com/detail_chance-97082.html', '生意社(JS页,需检索刷新)'),
    '黄磷': ('27000', '元/吨', '2026-08-07', 'https://www.cbcie.com/102573/12/list.html', 'CBC(需SSL绕过+解析)'),
    '液化天然气': ('5410', '元/吨', '2026-08-10', 'https://finance.sina.com.cn/money/future/nyzx/2026-08-10/doc-inimuvrt2881458.shtml', '新浪(URL含随机ID,需检索定位)'),
    'Brent原油': ('82.49', '美元/桶', '2026-08-10', 'https://www.100ppi.com/news/detail-20260810-6042703.html', '新浪/生意社(URL含随机ID,需检索定位)'),
    'WTI原油': ('77.29', '美元/桶', '2026-08-10', 'https://finance.sina.com.cn/money/future/nyzx/2026-08-10/doc-inimuvrt8216660.shtml', '新浪(URL含随机ID,需检索定位)'),
    '玉米': ('2238.57', '元/吨', '2026-08-10', 'https://www.100ppi.com/news/detail-20260810-6042708.html', '新浪/生意社(URL含随机ID,需检索定位)'),
    '棕榈油': ('9312', '元/吨', '2026-08-10', 'https://finance.sina.com.cn/money/future/agri/2026-08-10/doc-inimuvrv4966029.shtml', '新浪(URL含随机ID,需检索定位)'),
    '黄金': ('937.58', '元/克', '2026-08-10', 'https://www.cngold.org/c/2026-08-10/c10678565.html', '金投网(需针对性解析)'),
}


def fetch(url, ssl_ctx=None):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    return urllib.request.urlopen(req, timeout=25, context=ssl_ctx).read().decode('utf-8', 'ignore')


def parse_guidechem(html):
    m = re.search(r'Updated:\s*([\d-]+)', html)
    updated = m.group(1) if m else ''
    m = re.search(r'<em>([\d,]+(?:\.\d+)?)</em>\s*([A-Za-z/]+)', html)
    if m:
        price = m.group(1).replace(',', '')
        unit = m.group(2)
    else:
        m2 = re.search(r'([\d,]+(?:\.\d+)?)\s*CNY/TON', html)
        price = m2.group(1).replace(',', '') if m2 else ''
        unit = 'CNY/TON'
    m = re.search(r'Price change \(DoD\):\s*([-\d.]+)', html)
    dod = m.group(1) if m else ''
    return price, unit, updated, dod


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []  # (cat, name, price, unit, date, url, status)
    errs = []
    for name, cat, cas in ITEMS:
        if cas:
            url = BASE.format(cas=cas)
            try:
                html = fetch(url)
                price, unit, updated, dod = parse_guidechem(html)
                if not price:
                    rows.append((cat, name, '未解析到', unit, updated, url, '检查页面'))
                    errs.append((name, '未解析到', '检查页面'))
                else:
                    rows.append((cat, name, price, '元/吨' if unit == 'CNY/TON' else unit, updated, url, f'盖德自动·DoD {dod}' if dod else '盖德自动'))
            except Exception as e:
                rows.append((cat, name, 'ERR', '-', '-', url, str(e)[:40]))
                errs.append((name, 'ERR', str(e)[:40]))
        else:
            # 无 CAS：查锚定表
            if name in MANUAL:
                price, unit, date, url, note = MANUAL[name]
                rows.append((cat, name, price, unit, date, url, f'需复核·{note}'))
            else:
                rows.append((cat, name, '待补', '-', '-', '-', '无源'))

    today = datetime.date.today().isoformat()
    dates = [r[4] for r in rows if r[4] and r[4] != '-']
    data_date = max(dates) if dates else today
    auto = sum(1 for r in rows if '自动' in r[6])
    review = sum(1 for r in rows if '需复核' in r[6])

    md = []
    md.append(f'---\ncreated: {today}\nupdated: {today}\ntags: [采购分析, 行情日报, 自动抓取]\nsource: 盖德化工网单品页(自动) + 缺口项锚定检索值(需复核)\n---\n')
    md.append(f'# 化工原料固定品类行情 · {data_date}\n')
    md.append(f'> 抓取时间：{today} ｜ 自动抓取(盖德) {auto} 项 ｜ 需复核锚定 {review} 项')
    md.append(f'> 数据日期：各品类取抓到的最新可用日期，不统一')
    md.append(f'> 来源：每行附来源链接可追溯；标"需复核"项为上次检索值，源站无稳定可构造接口\n')
    md.append('| 类别 | 名称 | 最新价 | 单位 | 数据日期 | 来源 | 状态 |')
    md.append('|---|---|---|---|---|---|---|')
    for r in rows:
        md.append(f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | [{r[5][:24]}]({r[5]}) | {r[6]} |' if r[5] != '-' else f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | - | {r[6]} |')

    md_path = os.path.join(OUT_DIR, f'{data_date}.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')

    csv_path = os.path.join(OUT_DIR, f'{data_date}.csv')
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        f.write('类别,名称,最新价,单位,数据日期,来源URL,状态\n')
        for r in rows:
            f.write(','.join([r[0], r[1], r[2], r[3], r[4], r[5], r[6]]) + '\n')

    print('OK rows=', len(rows), 'auto=', auto, 'review=', review)
    print('data_date=', data_date)
    print('md=', md_path)
    print('pending/err=', len(errs))
    for e in errs:
        print('  ', e)


if __name__ == '__main__':
    main()
