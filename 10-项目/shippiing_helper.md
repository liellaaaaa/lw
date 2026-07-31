---
created: 2026-07-28
updated: 2026-07-31
status: 95% · 调整阶段 · 即将进入维护
period: 入职后
tags:
  - 项目
  - 船务/外贸
  - Python
  - FastAPI
  - Vue3
  - SQLite
  - OnlyOffice
repo: https://github.com/liellaaaaa/shippiing_helper
github_created: 2026-05-28
github_pushed: 2026-07-29
---

# shippiing_helper · 船务部制单与文档一体化平台

> 仓库名 `shippiing_helper` 为 `shipping_helper` 的拼写变体（README 内仍称 shipping_helper）。
> **时间线**：2026-05-28 首次提交，此前有一个 PyQt5 桌面版尝试（`260527_giveup_shipping_helper`）于 5/27 被放弃；当前版本采用 FastAPI + Vue3 Web 架构重写。
> **状态**：95%，与船务部对接中，处于最后的调整阶段，即将进入维护。GitHub 200+ 次提交。

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

## 调整阶段待办

> 95%，船务部对接反馈后的最后调整。

- [ ] 认证与用户体系的收口方案（维护阶段再评估 Alembic / Postgres / RBAC 等大改项）
- [ ] 补充 `data/users.json`（部署前必补，否则登录链路断）
- [ ] 最终交付前做一次完整的功能回归测试

## 开发历程（来自飞书项目日志 + 月度汇报）

> 2026-05-28 ~ 2026-07-20，独立全栈开发，船务部对接交付

### 五月：启动与 Phase 1

| 日期 | 里程碑 |
|------|--------|
| 5/28 | 项目框架搭建（Vue3 + FastAPI + SQLite）、订单粘贴解析上线 |
| 5/29 | PI文件解析（.xlsx/.xls，自动列映射+置信度评分） |
| 5/30 | 订单与PI数据合并（按产品编码关联，差异高亮） |
| 5/31 | 包装计算服务上线（13种桶类型、2种托盘、20GP适配）、数据看板上线 |

### 六月：Phase 2/3 全面开发

| 日期 | 里程碑 |
|------|--------|
| 6/1 | Phase 2框架搭建、OnlyOffice集成、Booking/LOI/MSDS模板系统 |
| 6/2 | 多产品混算包装、PI支持PDF OCR解析 |
| 6/3 | 空白模板加载、我的模板、数据中心（MSDS/运输报告目录树） |
| 6/4 | TypeScript构建修复 |
| 6/5 | 产品知识库初始化（389条HS编码） |
| 6/6 | 三栏布局统一、OnlyOffice编辑器优化 |
| 6/9 | Phase 3报关模块独立页面（5工作表中国报关Excel） |
| 6/12 | 订舱单填写确认弹窗、多产品模板 |
| 6/14 | 包装计算重构（以板数为锚点、余数散货分配、3种装载模式） |
| 6/15 | 报关品名查询、HS编码冲突检测、一单多品汇总、服务器搭建上线 |
| 6/18 | 登录认证模块（JWT Token机制） |
| 6/22 | **MSDS自动化生成上线，正式交付船务部（万凤、潘慧兰）** |
| 6/23 | 英文MSDS生成（自动查表补CAS号） |
| 6/25 | 后端依赖补充、跨平台路径修复 |
| 6/27 | /health健康检测接口（OnlyOffice/DB/Tesseract三组件） |
| 6/29 | 翻译功能切换为translatepy，英文MSDS乱码修复 |
| 6/30 | LOI按钮SVG路径修复 |

### 七月：闭环优化

| 日期 | 里程碑 |
|------|--------|
| 7/3 | **三数据源数据流打通**（PI合同表+销售订单表+PI合同文件→台账→四种文档），AI解析企微粘贴格式 |
| 7/7 | 报关资料重构、Phase 3整合进Phase 2、MSDS台账改版 |
| 7/8 | 界面格式统一、台账写入补全、PI解析增强 |
| 7/9 | MSDS多选批量生成中英文ZIP包、英文MSDS自动翻译、申报要素修复 |
| 7/13 | 币制字段全链路打通、报关单模板重构为占位符模式 |
| 7/16 | 包装计算新增"每桶实际装入量"、台账编辑/删除/判重 |
| 7/20 | **PI解析接入DeepSeek AI**（优先AI识别→降级Regex匹配，准确率大幅提升） |

### 交付后反馈与待定项

船务部试用后反馈的调整项：
- 连通性检查按钮
- 反馈按钮
- 操作时长记录
- MSDS翻译优化（成分名匹配、空格差异处理）
- 订单处理功能扩展（产品组合、包装计算优化、价格条款、付款方式等）

## 个人价值

- 2026-05-28 起独立从 0 开发（前身 `260527_giveup_shipping_helper` PyQt5 桌面版同日废弃），代表从「用 AI 平台」到「自己造企业工具」的能力跃迁。
- OnlyOffice 集成范式（JWT + 单端口代理 + 模板占位符填充）可迁移到后续项目。
- **AI集成里程碑**：7/20 将 DeepSeek AI 嵌入 PI 解析流程，从传统正则匹配升级为 AI 语义识别。

## 相关知识

- [[../20-知识/业务拆解方法/业务需求拆解与AI切入点]] — 基于本项目和采购分析助手提炼的拆解方法论

## 工作文稿

- [[../20-知识/工作文稿/shipping_log|shipping-helper-项目日志（飞书）]]

## 相关链接

- 后端入口/中间件：`backend/app/main.py`
- 认证服务：`backend/app/services/auth_service.py`
- 路由层：`backend/app/api/v1/*.py`
- 模型层：`backend/app/models/*.py`
- 前端入口：`frontend/src/main.ts`、`router/index.ts`、`stores/auth.ts`、`api/axios.ts`
- 文档：`README.md`、`CLAUDE.md`、`AGENTS.md`、`DEPLOYMENT.md`
