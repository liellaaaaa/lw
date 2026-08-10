# -*- coding: utf-8 -*-
"""
化工原料固定品类价格抓取脚本（盖德化工网单品价格页）
- 按 CAS 定位每个品类的最新价格页
- 解析：最新价、单位、数据更新日期、日涨跌(DoD)
- 输出：Markdown 行情表 + CSV
用法：python fetch_chem_prices.py
"""
import urllib.request, re, os, datetime

UA = 'Mozilla/5.0'
BASE = 'https://www.guidechem.com/price/en/{cas}.html'
OUT_DIR = os.path.join(os.path.dirname(__file__), '行情日报')

# (名称, 类别, CAS)  —— CAS=None 表示无单一化学品（聚合物/大宗商品/基准），需其他源补充
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


def fetch(cas):
    url = BASE.format(cas=cas)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    return urllib.request.urlopen(req, timeout=25).read().decode('utf-8', 'ignore')


def parse(html):
    m = re.search(r'Updated:\s*([\d-]+)', html)
    updated = m.group(1) if m else ''
    # 主价格：<em>6213</em>CNY/TON（取第一个，即当日全国均价）
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
    rows = []
    for name, cat, cas in ITEMS:
        if not cas:
            rows.append((cat, name, '-', '待补(无单一CAS)', '-', '-', '需生意社/基准源'))
            continue
        try:
            html = fetch(cas)
            price, unit, updated, dod = parse(html)
            if not price:
                rows.append((cat, name, cas, '未解析到', unit, updated, '检查页面'))
            else:
                rows.append((cat, name, cas, price, unit, updated, dod))
        except Exception as e:
            rows.append((cat, name, cas, 'ERR', '-', '-', str(e)[:50]))

    today = datetime.date.today().isoformat()
    # 取出现最多的数据日期作为数据日期
    dates = [r[5] for r in rows if r[5] and r[5] != '-']
    data_date = max(dates) if dates else today

    md = []
    md.append(f'---\ncreated: {today}\nupdated: {today}\ntags: [采购分析, 行情日报, 自动抓取]\nsource: 盖德化工网单品价格页(price/en/{{cas}}.html)\n---\n')
    md.append(f'# 化工原料固定品类行情 · {data_date}\n')
    md.append(f'> 抓取时间：{today} ｜ 价格数据日期：{data_date}（站点当日未更新时取最近一期）')
    md.append(f'> 数据源：盖德化工网 GuideTrends 单品价格页 ｜ 共 {len(rows)} 个品类\n')
    md.append('| 类别 | 名称 | CAS | 最新价 | 单位 | 数据日期 | 日涨跌(DoD) |')
    md.append('|---|---|---|---|---|---|---|')
    for r in rows:
        md.append(f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} |')

    md_path = os.path.join(OUT_DIR, f'{data_date}.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')

    csv_path = os.path.join(OUT_DIR, f'{data_date}.csv')
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        f.write('类别,名称,CAS,最新价,单位,数据日期,日涨跌\n')
        for r in rows:
            f.write(','.join(r) + '\n')

    print('OK rows=', len(rows))
    print('data_date=', data_date)
    print('md=', md_path)
    print('csv=', csv_path)
    errs = [r for r in rows if r[3] in ('ERR', '未解析到', '待补(无单一CAS)')]
    print('pending/err=', len(errs))
    for r in errs:
        print('  ', r[1], r[3], r[6])


if __name__ == '__main__':
    main()
