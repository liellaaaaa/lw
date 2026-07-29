---
type: 树干
status: 已完成
domain: 技术归档
created: 2026-07-29
modified: 2026-07-29
tags: [type/原子, domain/技术归档, priority/高]
related: []
---

# shippiing_helper 项目总览

> 💡 一句话总结：从 0 自研、临近收尾的船务部制单与文档一体化 Web 平台（FastAPI + Vue3），把分散在 Excel/Word/PDF 的船务操作集中成一套系统。

## 为什么重要
这是我 2026-06 起独立从 0 开发、已近两个月的真实项目，代表我从"用 AI 平台"到"自己造企业工具"的能力跃迁；收尾阶段需要清晰的架构与债务清单来指导收口。

## 核心内容
- 定位：面向船务部门，覆盖「销售订单 / PI / 产品知识」三源合并 → MSDS 生成 → 包装计算 → 运输鉴定 → 报关单证在线编辑导出的完整工作流。
- 三期演进：Phase1 基础台账 → Phase2 智能生成（OnlyOffice）→ Phase3 数据中心 / 审计 / 看板。
- 技术栈：Python + FastAPI + SQLAlchemy + Pydantic + SQLite；Vue3 + TS + Vite + Pinia；OnlyOffice Document Server 集成。
- ⚠️ 矛盾标记：README 模型清单漏列 4 个模型、仓库名 `shippiing_helper` 与 README 内 `shipping_helper` 拼写不一致——文档与代码已漂移。

## 对我有什么用（编译环必答）
收尾 / 交接 / 复盘时不必反复翻代码即可回看全局；其"已知债清单"直接变成我的收口待办；OnlyOffice 集成范式可迁移到后续项目。

## 🔗 关键链接
- child:: [[OnlyOffice 单端口集成模式]]
- related:: [[shippiing_helper 认证安全债]]
- related:: [[shippiing_helper 数据层运维债]]
- related:: [[00-原始资料/项目/ai-sales-coach]]

## ❓ 待探索
- [ ] 收尾优先级：先补认证还是先补用户体系？
- [ ] 是否要换 Postgres 替代 SQLite？
- [ ] 能否沉淀为"自研企业工具"通用模板？

## 📎 参考
- 原始资料：[[00-原始资料/项目/shippiing_helper]]
