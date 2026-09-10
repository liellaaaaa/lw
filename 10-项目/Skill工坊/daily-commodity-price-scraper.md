---
created: 2026-09-10
updated: 2026-09-10
period: 入职后
status: ✅ 已交付，automation 工作日 9:30 常态化运行
tags:
  - 项目
  - Skill
  - 爬虫
  - WorkBuddy
  - 采购/成本
department: 采购部（成本情报）
requester: 采购部/报价场景
skill_path: ~/.workbuddy/skills/daily-commodity-price-scraper/
---

# daily-commodity-price-scraper（化工原料当日价格抓取）

**日期**：2026-09-10 归档

> **一句话**：61 个固定品种（化工53+能源3+农副2+有色3）当日现货价一键抓取，6 类数据源交叉佐证，输出每个价格可点链接核对的 HTML 日报。automation 工作日 9:30 自动跑。

## 需求背景与价值

- 采购部跟踪原料行情、报价需要成本依据，人工逐品种查价耗时且无留痕。
- 核心价值在**多源佐证**：单一来源价格可能失真，报表里每个品种给出原始链接，收到报价单随时可核对。
- 扩展方向：卓创/隆众/SMM 付费源（需账号 API key，暂未接入，见 references/pitfalls.md）。

## 架构

```
run_daily.py ──► chem_price_spider.py ──► make_report.py
 (入口/调度)        (并发抓 6 类源)         (生成 HTML)
```

6 类数据源：A 生意社基准价（主源，08:30 发布，59/61）· B 生意社企业报价（53/61）· C 新浪期货（稳定第二数值源）· D 东方财富期货（best-effort）· E 搜狗微信佐证链接（61/61）· F 板块站（长江有色/粮油网）。
**原则**：只取当日价，当天没数据就跳过，不回填历史；期货盘面价 ≠ 现货价，仅作趋势验证。

## 业务与实现要点（可复用踩坑）

1. **生意社 HW_CHECK 反爬**：页面注入 `_0x2` 十六进制串要求回设 cookie，`fetch()` 已处理，不能用裸 `requests.get`；先访问首页预热 cookie。
2. **基准价按品种名精确匹配**：一个 vane 页列多个品种，靠 `ALIAS` 别名表精确匹配，否则误抓同页其他品种价格。加品种必须同步补 ALIAS。
3. **新浪期货**：必须带 `Referer: finance.sina.com.cn`、GBK 编码、内外盘字段下标不同；`sina_code` 支持列表兜底。
4. **东财 API 不稳定**（间歇 0 条）：3 次重试后放弃，新浪补位，不阻塞。
5. **stdout 只能重包装一次**：多文件重复 `TextIOWrapper` 会在 GC 时关 buffer 报 `I/O operation on closed file`——只在入口包一次 + `_Tee` 写日志。
6. **调度用 WorkBuddy automation**：沙箱禁 `schtasks`；工作日 9:30（生意社 08:30 发价留缓冲）。
7. **临时文件清理**：不用 `rm`/`Remove-Item`（安全包装会改坏路径），用 venv Python `os.remove` 白名单删除。

## 进度时间线

| 日期 | 进展 |
|---|---|
| 2026-08-10 前 | 开发完成：6 类源接入 + 反爬绕过 + HTML 报表（涨红跌绿） |
| 2026-08-10 | SKILL.md 定稿（含 8 条踩坑沉淀），交付 |
| 至今 | automation 工作日 9:30 常态化运行，产出 `化工原料价格_YYYY-MM-DD.html` + prices json + run.log |

## 维护口径

- `ITEMS` 在 `chem_price_spider.py` 顶部：`(显示名, 板块, vane_id, pid, sina_code)`；加品种三步——补 ALIAS → 补 EM_MAP → 补 sina_code。
- 依赖 managed venv 的 requests；脚本用 `__file__` 相对路径，整体可拷贝迁移。
- ⚠️ 编辑教训：`replace_all` 曾把 `ALIAS.get` 改成 `ALIAsession.get` 导致线程崩溃——改私有变量用精确替换。

## 下一步

- [ ] 观察自动化运行稳定性（漏跑/反爬升级时补丁）
- [ ] 评估付费源（卓创/隆众/SMM）接入价值，需先申请凭据
- [ ] 考虑与报价单/采购分析工具联动（价格信号 → 报价依据）
