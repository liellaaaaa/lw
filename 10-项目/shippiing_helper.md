---
created: 2026-07-28
updated: 2026-07-28
tags:
  - 项目
  - 船务/外贸
  - Python
  - FastAPI
  - Vue3
  - SQLite
  - OnlyOffice
repo: https://github.com/liellaaaaa/shippiing_helper
---

# shippiing_helper · 船务部制单与文档一体化平台

> 仓库名 `shippiing_helper` 为 `shipping_helper` 的拼写变体（README 内仍称 shipping_helper）。
> **时间线**：2026-05-28 首次提交，此前有一个 PyQt5 桌面版尝试（`260527_giveup_shipping_helper`）于 5/27 被放弃；当前版本采用 FastAPI + Vue3 Web 架构重写，已持续开发约两个月、临近收尾。GitHub 200+ 次提交。

## 项目简介

面向**船务部门**的一站式制单与文档协作工具，覆盖从「销售订单 / PI / 产品知识」三源合并，到 MSDS 生成、包装计算、运输鉴定报告、报关单证（Booking / MSDS / 报关单）在线编辑与导出的完整工作流。目标是把原本分散在 Excel / Word / PDF 里的船务操作集中到一套 Web 系统，减少人工录入与字段不一致。

系统分三期演进：
- **Phase 1（基础台账）**：订单 / PI 解析、三源合并比对、台账读写、MSDS / 运输报告索引。
- **Phase 2（智能生成）**：MSDS 自动生成（对接 OnlyOffice）、包装方案计算、单证生成填充。
- **Phase 3（增强）**：数据中心、审计日志、看板、导出编码查询等。

## 仓库地址

https://github.com/liellaaaaa/shippiing_helper

## 技术栈

- 后端：Python + **FastAPI**，`uvicorn`，**SQLAlchemy** + **Pydantic**，SQLite（`database.py`，手写增量迁移 `migrations/001–016`，非 Alembic）
- 解析/生成：`PyMuPDF`(PDF 文本/字段抽取)、`python-docx` / `openpyxl`(Word/Excel)、`python-multipart`(上传)、`aiohttp`/`requests`(外部，如 OnlyOffice Document Server)、`pytesseract`/`tesseract`(OCR 自检)
- 前端：Vue 3 + **TypeScript** + Vite + Pinia + Vue Router + axios（JWT 拦截器）；`frontend/dist` 由后端 `StaticFiles` 单端口托管
- 集成：**OnlyOffice** Document Server（JWT + 单端口代理 + 模板占位符填充）
- 自检：`/health` 多组件（api / onlyoffice / database / tesseract）

## 系统架构

`app/main.py`(入口 + 中间件 + SPA 挂载) → `api/v1`(路由) + `api/deps.py`(DI) → `services/`(业务逻辑) → `core/`(解析器/配置/knowledge_filler) → `models/`(ORM) + `schemas/`(Pydantic) → SQLite。

- 启动期全量扫描 MSDS / 运输报告目录建内存索引
- JWT 鉴权 + 审计日志 + 文档版本化（`ShipmentDoc.content_hash/version`）+ 编辑锁（`locked_by`）

## 数据模型（backend/app/models/*.py）

- **Order**(`orders`)：`order_no`(唯一索引)、`customer_code/name`、`pi_no`、`salesperson`、`merchandiser`、`order_status`(默认 pending)、`locked_by/locked_at`(编辑锁)、`total_quantity_kg/total_gross_weight_kg/total_volume_cbm`、`fits_20gp`；关系 `items → OrderItem`
- **OrderItem**(`order_items`)：`internal_code`、`product_cn/en`、`spec_kg`、`hs_code`、`customs_name`、`quantity_kg`、`unit_price`、`total_amount`、`packaging_type_id`(FK)、`drum_count/pallet_count`、`net/gross_weight_kg`、`volume_cbm`
- **OrderPiRecord**(`order_pi_records`)：三源合并落库表（订单/PI/产品知识），含 `customs_match_status`、`status`、`packaging_result_json`、PI 头(consignee/destination/price_term/payment_terms/bank_info)、分组字段(`group_id/group_name/is_group_header`)
- **PIContract**(`pi_contracts`) + **PiContractItem**：PI 合同头与明细
- **PiData**(`pi_data`)：PI 知识库（`internal_code` 唯一，含 `hs_code`/`customs_name`/`customs_composition`）
- **MSDSIndex**(`msds_indexes`)：MSDS 文件索引（PDF 抽取字段）
- **MsdsLedger**(`msds_product_ledger`)：MSDS 产品台账（`internal_code`/`customs_name` 索引，含 `composition` JSON）
- **MSDSCorrection**：MSDS 修正历史
- **TransportReport**(`transport_reports`) + **OrderItemTransportReport**：运输鉴定报告及与订单项多对多关联
- **ShipmentDoc**(`shipment_docs`)：单证版本化（`file_blob`/`content_hash`/`version`/`change_reason`）
- **DocumentTemplate**(`document_templates`)：Booking/MSDS 模板 + `placeholders` JSON
- **AuditLog**(`audit_logs`)：审计日志（`event_type`/`user_name`/`module`/`action_time`/`detail`/`ip_address`）
- 其它：`PackagingType`(`packaging_types`)、`ProductKnowledge`(`products_knowledge`)（在 `order.py` 内）
- **User**：注意 `models/user.py` 仅为 **Pydantic schema**（`name`/`password`），**非** SQLAlchemy 表；用户来自 `data/users.json`

## 核心功能模块（backend/app/api/v1）

- **orders**：粘贴订单/PI 文本解析、三源合并预览、台账读写与保存
- **pi**：上传解析 PI `.xlsx/.xls`，提取合同头与明细
- **merge**：订单-PI 关联状态列表与逐项比对（pending/completed/all）
- **packaging / packages**：包装类型/卡板查询；单/多方案、整单包装计算（海/空/陆运，返回桶数、卡板、体积、集装箱推荐、计费重、公路限重）
- **msds / msds_generator / msds_ledger**：MSDS 索引与内容抽取、自动生成（OnlyOffice）、产品台账 CRUD/批量导入导出
- **transport / transport_reports**：运输鉴定报告 PDF 上传抽取、目录搜索/预览/与订单项关联
- **name-mapping**：商品中英文品名对照（cn↔en）
- **data-center**：MSDS 参考文件三级优先级搜索、预览、修正上传
- **documents / onlyoffice**：Booking/MSDS/报关单证生成填充；OnlyOffice JWT/配置/下载/回调（含 Document Server 代理）
- **export_codes**：按 `internal_code` 查询 HS/出口编码
- **audit / dashboard**：审计日志查询统计导出；合并数据看板（按订单分组）与落库导出
- **auth**：`/auth/login` 返回 JWT

## 目录结构要点

- 后端分层：`main → api/v1 + deps → services → core → models/schemas → database`；`migrations/` 为顺序脚本（无 Alembic 版本管理）
- 前端分层：`src/views`(phase1/phase2/auth/data-center) + `src/components` → `src/api/*.ts`(axios) → `src/stores/auth.ts`(Pinia) → `router`/`plugins/track.ts`(埋点)/`constants`/`utils`
- 关键解析：`core/pi_parser.py`、`core/order_parser.py`、`core/knowledge_filler.py`
- 关键服务：`ledger_service`、`merge_service`、`document_service`、`msds_generator_service`、`packaging_service`、`calculation_service`

## 亮点 / 可复盘点

- 销售订单 / PI / 产品知识**三源合并 + 去重 + 差异对比**，外贸垂直场景完整工作流
- 包装计算同时覆盖海运/空运(IATA×167 / 航司÷6000)/陆运，含集装箱适配与余数分配
- OnlyOffice 集成（JWT + 单端口代理 + 模板占位符填充）实现在线编辑 Booking/MSDS
- `/health` 多组件自检 + 审计日志 + 文档版本化 + 编辑锁

## 需注意的已知问题

- **认证中间件冗余**：`main.py` 的 `auth_middleware` 白名单几乎放行全部 `/api/v1/*`（仅 `orders` 受保护），JWT 鉴权形同虚设；且与 `auth.py` 的 `get_current_user` 依赖机制并存、职责重叠
- **users.json 缺失**：`auth_service.py` 指向 `data/users.json`，全仓无此文件；`load_users()` 文件缺失时返回 `[]`，登录必失败（需自建用户文件）
- **README vs 代码不匹配**：README 模型清单漏列 `msds_ledger.py`/`audit_log.py`/`template.py`/`order_item_transport_report.py`；仓库名拼写 `shippiing_helper` 与 README 内 `shipping_helper` 不一致
- **User 无数据库表**：所谓 User 仅 Pydantic schema + json 文件，无法多用户/权限管控
- **数据库为 SQLite + 手写迁移**：多环境易不一致
- **硬编码密钥**：`JWT_SECRET` 默认 `shipping-helper-secret-key-change-in-production`，生产需改

## 待探索 / 收尾决策清单

> 来源：消化笔记整理；收尾阶段需要本人拍板。

- [ ] 收尾优先级：先补认证（收紧 `auth_middleware` 白名单 + 统一到 `get_current_user`），还是先补用户体系（`users.json` → 数据库表）？
- [ ] 是否用 Alembic 替代手写迁移（`migrations/001–016`）？
- [ ] 是否换 Postgres 替代 SQLite？
- [ ] 是否引入 RBAC 简单角色？
- [ ] 能否沉淀为「自研企业工具」通用模板？（OnlyOffice 集成范式可迁移到后续项目）
- [ ] 补充 `data/users.json`（部署前必补，否则登录链路断）

## 个人价值

- 2026-05-28 起独立从 0 开发（前身 `260527_giveup_shipping_helper` PyQt5 桌面版同日废弃），代表从「用 AI 平台」到「自己造企业工具」的能力跃迁。
- OnlyOffice 集成范式（JWT + 单端口代理 + 模板占位符填充）可迁移到后续项目。

## 相关链接

- 后端入口/中间件：`backend/app/main.py`
- 认证服务：`backend/app/services/auth_service.py`
- 路由层：`backend/app/api/v1/*.py`
- 模型层：`backend/app/models/*.py`
- 前端入口：`frontend/src/main.ts`、`router/index.ts`、`stores/auth.ts`、`api/axios.ts`
- 文档：`README.md`、`CLAUDE.md`、`AGENTS.md`、`DEPLOYMENT.md`
