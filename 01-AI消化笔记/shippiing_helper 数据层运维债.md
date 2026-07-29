---
type: 叶子
status: 已完成
domain: 技术归档
created: 2026-07-29
modified: 2026-07-29
tags: [type/原子, domain/技术归档, priority/中]
related: []
---

# shippiing_helper 数据层运维债

> 💡 一句话总结：SQLite + 手写顺序迁移（migrations/001–016，无 Alembic）+ `users.json` 缺失，是当前最易在部署 / 多环境出事的债。

## 为什么重要
手写迁移在多环境易不一致；`users.json` 缺失会导致 `load_users()` 返回 `[]`、登录必失败——属于"本地能跑、部署就挂"的典型坑。

## 核心内容
- SQLite 单机文件，多环境 / 并发弱；迁移靠 `database.py` 手写增量脚本，无版本管理。
- `auth_service.py` 指向 `data/users.json`，全仓无此文件，登录链路断。
- README 模型清单与代码漂移（漏列 msds_ledger / audit_log / template / order_item_transport_report）。

## 对我有什么用（编译环必答）
部署前必补的清单：生成 `users.json` 或改用户落库、评估换 Postgres。下次部署出错先查这条。

## 🔗 关键链接
- parent:: [[shippiing_helper 项目总览]]
- related:: [[shippiing_helper 认证安全债]]
- related:: [[OnlyOffice 单端口集成模式]]

## ❓ 待探索
- [ ] 是否用 Alembic 替代手写迁移？

## 📎 参考
- 原始资料：[[00-原始资料/项目/shippiing_helper]]
