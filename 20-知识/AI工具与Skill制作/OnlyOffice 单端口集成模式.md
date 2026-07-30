---
type: 种子
status: 已完成
domain: 技术归档
created: 2026-07-29
modified: 2026-07-29
tags: [type/原子, domain/技术归档]
related: []
---

# OnlyOffice 单端口集成模式

> 💡 一句话总结：用 JWT + 单端口代理 + 模板占位符填充，把 OnlyOffice Document Server 嵌进自有 Web 应用，实现 Booking / MSDS / 报关单的在线编辑与导出。

## 为什么重要
企业文档在线协作是大概率复用的需求。这套集成模式是 shippiing_helper 的亮点，也是我验证过的可搬运方案。

## 核心内容
- JWT 鉴权对接 Document Server。
- 单端口代理：前端 `frontend/dist` 由后端 `StaticFiles` 托管，OnlyOffice 回调也走同端口，省去跨域 / 多端口运维。
- 模板占位符填充：`DocumentTemplate.placeholders` JSON 驱动字段注入。
- 文档版本化：`ShipmentDoc.content_hash/version` + 编辑锁 `locked_by`。

## 对我有什么用（编译环必答）
未来任何"在线编辑 Word/Excel 模板并导出"的需求（别的项目、甚至内部工具）可直接复用这套模式，不必重新踩 OnlyOffice 的坑。

## 🔗 关键链接
- 项目：[[../../10-项目/shippiing_helper.md|shippiing_helper]]
- 数据层笔记：[[../../10-项目/shippiing_helper.md#需注意的已知问题|shippiing_helper 数据层运维债]]

## ❓ 待探索
- [ ] 高并发下 Document Server 资源占用？

## 📎 参考
- 原始资料：[[../../10-项目/shippiing_helper.md]]
