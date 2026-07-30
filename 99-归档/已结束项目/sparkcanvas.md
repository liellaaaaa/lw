---
created: 2026-07-28
updated: 2026-07-28
tags:
  - 项目
  - 自媒体/内容
  - UniApp
  - Vue
  - RAG
  - LLM
repo: https://github.com/liellaaaaa/sparkcanvas
---

# sparkcanvas · 自媒体全自动内容生产系统（流量爆破）

## 项目简介

面向**自媒体运营**的「全自动内容生产」系统，定位关键词是**流量爆破**。围绕一个工作区（workspace）组织内容创作流程：结合 RAG 检索素材、调用大模型生成文案/脚本，沉淀历史记录，帮助运营者批量产出短视频/图文内容。前端为 UniApp（可跨端：H5 / 小程序 / App），默认开发分支为 `develop`。

## 仓库地址

https://github.com/liellaaaaa/sparkcanvas （注意：默认分支为 `develop`）

## 技术栈

- 前端：**UniApp（基于 Vue）**（`spark-uniapp/`），含 `pages`、`components`、`stores`、`utils`、`api`
- 能力：本地 **RAG**（`pages/rag` 相关页面）、LLM 生成、历史管理
- 构建产物：`spark-uniapp/unpackage/`（**非源码**，分析时忽略）
- 后端：见仓库内 server/backend 相关目录（具体以实际代码为准）

## 系统架构

- 用户登录/注册 → 进入 workspace（工作区）→ 通过 RAG 检索素材 → 大模型生成内容 → 历史记录留存
- 前端 `stores`(Pinia) 管理状态，`api` 封装请求，`utils` 放通用函数

## 数据模型 / 关键结构

- 以页面/状态推断：用户、workspace、rag 知识条目、生成任务、历史记录等（具体以接口/存储实现为准，本笔记未逐一核对）

## 核心功能模块（按 pages/功能归纳）

- **登录/注册**：账号体系入口
- **workspace（工作区）**：内容生产主界面，组织创作流程
- **rag**：RAG 素材检索/知识库页面
- **history（历史）**：生成内容历史管理

## 目录结构要点

- 源码：`spark-uniapp/src`（或根）下的 `pages/`、`components/`、`stores/`、`utils/`、`api/`
- **忽略** `spark-uniapp/unpackage/` 构建产物
- 关注 RAG 相关源码与 LLM 调用封装

## 亮点 / 可复盘点

- UniApp 跨端，一次开发多端分发
- 把「RAG 检索 + LLM 生成 + 历史管理」串成自媒体内容生产闭环
- `develop` 分支为活跃开发分支，适合跟踪最新进展

## 需注意的已知问题

- `unpackage/` 构建产物易误提交，需 `.gitignore` 管控
- 后端服务与 LLM/向量库选型需在 `spark-uniapp` 之外（server/backend）核对
- 多端适配（小程序/H5/App）的权限与 API 差异需注意

## 相关链接

- 前端入口：`spark-uniapp/`（pages/workspace、pages/rag、pages/history）
- 默认分支：`develop`
