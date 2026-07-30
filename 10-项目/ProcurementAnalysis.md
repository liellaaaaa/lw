---
created: 2026-07-30
updated: 2026-07-30
status: 维护模式
tags:
  - 项目
  - 原料/采购
  - Python
  - FastAPI
  - SQLAlchemy
  - 数据分析
repo: https://github.com/liellaaaaa/ProcurementAnalysis
---

# ProcurementAnalysis · 原料采购数据获取与展示平台

> **对接部门**：采购部
> **状态**：维护模式。功能已交付，采购部日常使用中，按需修 bug。
> **时间线**：2026-04-30 首次提交，为入职后（4/15）的第一个正式项目；截至 6/27 持续活跃约两个月。

## 项目简介

面向**原材料采购**的数据采集、监控与展示后端系统。核心是把分散在各数据源的原材料价格/品类信息**定时获取**入库，提供价格历史、品类管理、**预警**（价格异动提醒）、**数据分析**看板，并记录操作日志与用户反馈，供采购决策使用。定位偏「数据后台 + API 服务」，前端由独立消费方或简单页面调用。

## 技术栈

- **FastAPI** + **SQLAlchemy** + **Pydantic**（schemas 在 `backend/api/models/schemas.py`）
- **Alembic** 数据库迁移（`alembic/` 目录，规范版本管理，区别于 shippiing_helper 的手写迁移）
- **JWT** 鉴权（`backend/api/deps.py` 的 `get_current_user`）
- 数据获取：外部数据源抓取（httpx/requests）
- 文档：`README.md`、`AGENTS.md`
- 数据库默认 SQLite / 可切换 PostgreSQL

## 系统架构

分层：`backend/api/main.py`(入口) → `backend/api/routes/*`(路由) + `backend/api/deps.py`(DI/鉴权) → `services`/`core`(业务逻辑) → `backend/api/models`(schemas + ORM 模型) → 数据库（Alembic 迁移）。

- 鉴权：`auth` 路由签发 JWT，`deps.get_current_user` 保护其余接口
- 数据获取与预警：定时/手动拉取外部原料数据 → 入库 → 按规则触发 `alerts` → 通过 `analytics` 汇总

## 数据模型

- **products**（原料）：原料主数据
- **prices**（价格）：价格历史时序，关联 products
- **categories**（品类）：原料分类
- **alerts**（预警）：预警规则 / 触发记录（价格异动）
- **analytics**（分析）：聚合分析结果
- **feedback**（反馈）：用户反馈
- **operation_logs**（操作日志）：操作审计
- **users**：JWT 用户

## 核心功能模块

- **auth**：登录 / 当前用户（JWT 签发与校验）
- **products**：原料主数据 CRUD
- **prices**：原料价格录入 / 历史查询
- **categories**：品类管理
- **alerts**：预警规则配置与触发查询
- **analytics**：数据分析 / 聚合接口
- **feedback**：用户反馈提交与查看
- **operation_logs**：操作日志记录与查询

## 亮点 / 可复盘点

- 规范使用 **Alembic** 做数据库版本管理（比手写迁移更可维护）
- 清晰的路由分层，便于扩展
- 预警 + 分析 + 操作日志一体化，适合采购监控类场景

## 需注意的已知问题

- 外部数据源抓取逻辑与失败重试、幂等性需结合 `services` 具体实现复核
- 若默认 SQLite，高并发写入需评估；生产建议 PostgreSQL
- 前端消费方未在本仓库内（纯后端），前端需另行对接

## 相关链接

- 入口：`backend/api/main.py`
- 路由：`backend/api/routes/*.py`
- 模型/鉴权：`backend/api/models/schemas.py`、`backend/api/deps.py`
- 迁移：`alembic/`
