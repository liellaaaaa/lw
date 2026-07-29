---
created: 2026-07-28
updated: 2026-07-28
tags:
  - 项目
  - AI应用
  - RAG
  - Python
  - LLM
  - 美食/导购
repo: https://github.com/liellaaaaa/productGuide
---

# productGuide · 美食/超市商品导购助手（RAG）

## 项目简介

基于 **RAG（检索增强生成）** 的超市/美食商品导购助手。把商品资料（名称、规格、成分、口味、适用场景等）构建为本地 Chroma 向量知识库，用户用自然语言提问（如「适合送长辈的低糖零食」），系统检索相关知识后由大模型生成导购回答。仓库附带完整设计文档（需求/概要/详细设计），是学习「RAG 应用从 0 到 1」的好样本。

## 仓库地址

https://github.com/liellaaaaa/productGuide

## 技术栈

- Python（CLI 应用，argparse/标准库为主）
- **Chroma**：向量知识库（本地持久化）
- LLM：通过 `ark_client.py` 调用（疑似**火山引擎方舟 / Ark** 兼容 OpenAI 的接口）
- 数据：`src/data/items.json`（商品语料）
- 文档：`00记录文件.md`、`01需求文档.md`、`02概要设计.md`、`03详细设计.md`、`README.md`

## 系统架构（RAG 数据流）

```
ingest (items.json → 切分/向量化) → kb (Chroma 持久化)
                                          ↓
user query → retrieve (相似度检索) → prompt (拼装) → ark_client (LLM 生成) → 回答
```

- `ingest.py`：读取 `items.json`，构建/更新 Chroma 知识库
- `kb.py`：知识库读写与检索封装
- `ark_client.py`：LLM 调用客户端（方舟/Ark）
- `prompt.py`：提示词模板与拼装
- `cli.py` / `__main__.py`：命令行入口与各子命令
- `config.py`：配置（API key、路径等）
- `json_log.py`：结构化日志

## 数据模型

- **items.json**：商品语料数组，每个商品含名称、规格、成分、口味、适用场景/人群等字段（用于切分与向量化）
- **Chroma 集合**：以商品切片为文档、嵌入向量为索引，支持相似度检索

## 核心功能模块（src/product_guide）

- **cli.py**：命令行入口，编排 ingest / query 等子命令
- **ingest.py**：商品数据入库（向量化 → Chroma）
- **kb.py**：知识库检索与读写
- **ark_client.py**：大模型调用（方舟/Ark 兼容接口）
- **prompt.py**：提示词模板
- **config.py**：配置管理
- **json_log.py**：JSON 结构化日志

## 目录结构要点

- `src/product_guide/`：主程序包（上述模块）
- `src/data/items.json`：商品语料
- 设计文档：`00记录文件.md` / `01需求文档.md` / `02概要设计.md` / `03详细设计.md`

## 亮点 / 可复盘点

- 完整 **需求 → 概要 → 详细设计** 文档，适合作为 RAG 应用教学/复盘样本
- Chroma 本地向量库 + 方舟 LLM 的轻量 RAG 实现，依赖少、易跑通
- CLI 子命令化（ingest / query），流程清晰

## 需注意的已知问题

- 检索召回质量高度依赖 `items.json` 覆盖度与切分策略
- 是否做重排/过滤、上下文窗口管理需看 `prompt.py`/`kb.py` 实现复核
- API key 等敏感配置需放 `config.py`（避免硬编码提交）

## 相关链接

- 入口：`src/product_guide/__main__.py`、`cli.py`
- RAG 核心：`ingest.py`、`kb.py`、`ark_client.py`、`prompt.py`
- 设计文档：`01需求文档.md`、`02概要设计.md`、`03详细设计.md`
