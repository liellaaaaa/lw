---
created: 2026-07-28
updated: 2026-07-31
status: 50% · 开发中
period: 入职后
tags:
  - 项目
  - AI应用
  - 销售陪练
  - Python
  - FastAPI
  - React
  - LLM
  - RAG
repo: https://github.com/liellaaaaa/ai-sales-coach
github_created: 2026-07-22
github_pushed: 2026-07-22
---

# ai-sales-coach · AI 销售陪练 / 培训 Web 应用（mvp-main）

> **对接部门**：营销部门（整个营销体系，非单一销售团队）
> **状态**：50%，仍在本人的主力开发阶段。

## 项目简介

基于大模型的**销售培训 / 陪练** Web 应用（mvp-main 分支）：把企业的销售资料（文档、话术、产品知识）沉淀为**知识库**，结合 LLM 为销售员提供培训模拟、知识检索与陪练对话，并配套仪表盘、设置与鉴权。定位是「营销部门的内部 AI 教练」，用 RAG + LLM 把静态销售资料变成可交互的训练与问答能力。

## 接手背景

本人（肖聪，AI 技术专员）于 **2026 年 7 月中旬**正式接手 / 负责本项目，当前为 mvp-main 版本，进度约 50%。此前（4–6 月）知识库中出现的 `ai-sales-coach` 相关记录属前期阶段，**本笔记聚焦本人接手后的内容**。

## 仓库地址

https://github.com/liellaaaaa/ai-sales-coach

## 技术栈

- 后端：Python + **FastAPI**（`backend/app/main.py`），**SQLAlchemy**(ORM) + **Pydantic**(schemas)
- 服务层：`services/llm`(大模型调用)、`services/knowledge`(知识库/RAG)、`services/document_parser`(文档解析)
- 前端：JavaScript / **React**（`frontend/src/App.jsx`、`frontend/src/api.js`）
- 部署：`docker-compose`（含后端 + 前端 + 依赖服务）
- 文档：`AGENTS.md`、`docs/`（handoff / roadmap / API draft）
- 知识库：向量检索（具体向量库见 `services/knowledge` 实现，如 Chroma/FAISS 等）

## 系统架构

分层：`backend/app/main.py` → `backend/app/routers/*`(auth/dashboard/knowledge/training/settings) + `backend/app/deps.py`(鉴权) → `backend/app/services/*`(llm/knowledge/document_parser) → `backend/app/models.py`(ORM) + `schemas.py`(Pydantic) → 数据库。

- 文档先经 `document_parser` 解析入库，再由 `knowledge` 建索引（RAG）
- `training` 调用 `llm` 生成陪练/模拟对话；`dashboard` 汇总训练数据
- 前端 React 通过 `api.js` 调后端，JWT 鉴权

## 数据模型（backend/app/models.py）

- **users**：账号（与 `auth` 配合，JWT）
- **knowledge / documents**：知识库文档与切片（RAG 语料）
- **training**：培训/陪练会话与记录
- **dashboard**：仪表盘聚合数据
- **settings**：用户/系统设置

> 具体字段以 `models.py` / `schemas.py` 为准（本笔记未逐一核对字段级定义）。

## 核心功能模块（backend/app/routers）

- **auth**：登录 / 当前用户（JWT）
- **knowledge**：知识库文档管理、检索（RAG 入口）
- **training**：销售陪练 / 培训模拟（调用 LLM）
- **dashboard**：训练数据仪表盘
- **settings**：设置项

## 目录结构要点

- 后端：`backend/app/{main,models,schemas,deps}.py` + `routers/` + `services/{llm,knowledge,document_parser}.py`
- 前端：`frontend/src/App.jsx`（React 入口）、`frontend/src/api.js`（接口封装）、`frontend/package.json`
- 部署：`docker-compose.yml`
- 文档：`AGENTS.md`、`docs/handoff.md`、`docs/roadmap.md`、`docs/api-draft.md`

## 亮点 / 可复盘点

- RAG + LLM 把销售资料转化为可交互「陪练」，场景清晰
- 清晰的前后端分离 + docker-compose 一键部署
- `docs/` 含 handoff / roadmap / API draft，工程协作资料完整

## 需注意的已知问题

- 具体向量库选型、`llm` 调用方式与模型供应商需看 `services/` 实现复核（本笔记未深入核查）
- 知识库文档解析对格式（PDF/Word/网页）的覆盖度待确认
- 多用户/权限、计费与对话留存策略见 `models` 与 `settings` 实现

## 相关链接

- 入口：`backend/app/main.py`
- 路由：`backend/app/routers/*.py`
- 服务：`backend/app/services/{llm,knowledge,document_parser}.py`
- 前端：`frontend/src/App.jsx`、`frontend/src/api.js`
- 文档：`AGENTS.md`、`docs/`
