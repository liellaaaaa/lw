---
type: 叶子
status: 已完成
domain: 技术归档
created: 2026-07-29
modified: 2026-07-29
tags: [type/原子, domain/技术归档, priority/高]
related: []
---

# shippiing_helper 认证安全债

> 💡 一句话总结：当前 `auth_middleware` 白名单几乎放行全部 `/api/v1/*`，JWT 形同虚设；且 `get_current_user` 依赖机制与之并存、职责重叠——这是收尾前必须修的 P0 债。

## 为什么重要
一个"认证等于没认证"的对内系统，一旦暴露到办公网就有数据泄露风险；也违背最小权限原则。

## 核心内容
- `main.py` 的 `auth_middleware` 白名单几乎全放行（仅 `orders` 受保护）。
- 与 `auth.py` 的 `get_current_user` 依赖机制重复，职责不清。
- `User` 仅 Pydantic schema + `data/users.json`，无数据库表，无法多用户 / 权限。
- `JWT_SECRET` 硬编码默认值，生产需改。

## 对我有什么用（编译环必答）
这是我的收口 P0 待办清单第一条；修法应统一到 `get_current_user` 依赖、收紧白名单、把用户落库。下次动手前先看这条，避免重复分析。

## 🔗 关键链接
- parent:: [[shippiing_helper 项目总览]]
- related:: [[shippiing_helper 数据层运维债]]

## ❓ 待探索
- [ ] 是否引入 RBAC 简单角色？

## 📎 参考
- 原始资料：[[00-原始资料/项目/shippiing_helper]]
