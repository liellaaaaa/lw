---
created: 2026-07-28
updated: 2026-08-14
status: 98% · 功能闭环 · 进入收尾维护
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
github_pushed: 2026-08-14
---

# shippiing_helper · 船务部制单与文档一体化平台

> 仓库名 `shippiing_helper` 为 `shipping_helper` 的拼写变体（README 内仍称 shipping_helper）。
> **时间线**：2026-05-28 首次提交，此前有一个 PyQt5 桌面版尝试（`260527_giveup_shipping_helper`）于 5/27 被放弃；当前版本采用 FastAPI + Vue3 Web 架构重写。
> **状态**：98%，船务部持续使用中。7 月底至 8 月初完成多轮功能增强与架构重构（JSON→SQLite 迁移、报关单动态扩展、产品拆行等），功能已基本闭环，进入收尾维护阶段。GitHub 250+ 次提交。

## 项目简介

面向**船务部门**的一站式制单与文档协作工具，覆盖从「销售订单 / PI / 产品知识」三源合并，到 MSDS 生成、包装计算、运输鉴定报告、报关单证（Booking / MSDS / 报关单）在线编辑与导出的完整工作流。目标是把原本分散在 Excel / Word / PDF 里的船务操作集中到一套 Web 系统，减少人工录入与字段不一致。

系统分三期演进：
- **Phase 1（基础台账）**：订单 / PI 解析、三源合并比对、台账读写、MSDS / 运输报告索引。
- **Phase 2（智能生成）**：MSDS 自动生成（对接 OnlyOffice）、包装方案计算、单证生成填充。
- **Phase 3（增强）**：数据中心、审计日志、看板、导出编码查询等。

## 仓库地址

https://github.com/liellaaaaa/shippiing_helper

## 技术栈

- 后端：Python + **FastAPI**，`uvicorn`，**SQLAlchemy** + **Pydantic**，SQLite（`database.py`，手写增量迁移 `migrations/001–018`，非 Alembic）
- 解析/生成：`PyMuPDF`(PDF 文本/字段抽取)、`python-docx` / `openpyxl`(Word/Excel)、`python-multipart`(上传)、`aiohttp`/`requests`(外部，如 OnlyOffice Document Server)、`pytesseract`/`tesseract`(OCR 自检)
- 前端：Vue 3 + **TypeScript** + Vite + Pinia + Vue Router + axios（JWT 拦截器）；`frontend/dist` 由后端 `StaticFiles` 单端口托管
- 集成：**OnlyOffice** Document Server（JWT + 单端口代理 + 模板占位符填充）
- 自检：`/health` 多组件（api / onlyoffice / database / tesseract）
- **AI 集成**：DeepSeek API（PI 文件解析优先 AI 识别 → 降级 Regex 匹配）

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
- **User**(`users`)：08-01 重构后已迁入 SQLite（`models/user.py` + `schemas/auth.py`），不再是 Pydantic schema + json 文件
- **reference_data.py（08-01 新增）**：7 张引用数据表统一管理——`pallets`/`container_specs`/`declaration_elements`/`ingredient_mappings`/`translation_mappings`/`msds_templates`；`products_knowledge` 并入 `customs_codes`（新增 `product_appearance` 列）；`packaging_types` 补 `is_palletizable`

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

- ~~**认证中间件冗余**~~：已通过 08-01 重构部分解决（users 迁入数据库，auth 统一走 DB）
- ~~**users.json 缺失**~~：✅ 已解决——08-01 重构将 users.json 及所有静态 JSON 迁入 SQLite（migration 018）
- ~~**User 无数据库表**~~：✅ 已解决——08-01 重构后 User 为正式 SQLAlchemy 表
- **README vs 代码不匹配**：仓库名拼写 `shippiing_helper` 与 README 内 `shipping_helper` 不一致；08-01 已更新 README/CLAUDE/AGENTS 文档
- **数据库为 SQLite + 手写迁移**：多环境易不一致（已积累 18 个迁移脚本）
- **硬编码密钥**：`JWT_SECRET` 默认 `shipping-helper-secret-key-change-in-production`，生产需改

## 收尾维护待办

> 98%，功能基本闭环，剩余为船务部反馈的小项与维护评估。

- [x] ~~认证与用户体系收口~~（08-01 JSON→SQLite 迁移已解决核心问题）
- [x] ~~补充 `data/users.json`~~（08-01 迁入数据库）
- [ ] 最终交付前做一次完整的功能回归测试
- [x] 申报要素台账功能（08-10 数据中心 Tab 化 + 增删改查落地）
- [ ] 评估 Alembic / Postgres / RBAC 等大改项（维护阶段再议）

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

| 日期   | 里程碑                                           |
| ---- | --------------------------------------------- |
| 6/1  | Phase 2框架搭建、OnlyOffice集成、Booking/LOI/MSDS模板系统 |
| 6/2  | 多产品混算包装、PI支持PDF OCR解析                         |
| 6/3  | 空白模板加载、我的模板、数据中心（MSDS/运输报告目录树）                |
| 6/4  | TypeScript构建修复                                |
| 6/5  | 产品知识库初始化（389条HS编码）                            |
| 6/6  | 三栏布局统一、OnlyOffice编辑器优化                        |
| 6/9  | Phase 3报关模块独立页面（5工作表中国报关Excel）                |
| 6/12 | 订舱单填写确认弹窗、多产品模板                               |
| 6/14 | 包装计算重构（以板数为锚点、余数散货分配、3种装载模式）                  |
| 6/15 | 报关品名查询、HS编码冲突检测、一单多品汇总、服务器搭建上线                |
| 6/18 | 登录认证模块（JWT Token机制）                           |
| 6/22 | **MSDS自动化生成上线，正式交付船务部（万凤、潘慧兰）**               |
| 6/23 | 英文MSDS生成（自动查表补CAS号）                           |
| 6/25 | 后端依赖补充、跨平台路径修复                                |
| 6/27 | /health健康检测接口（OnlyOffice/DB/Tesseract三组件）     |
| 6/29 | 翻译功能切换为translatepy，英文MSDS乱码修复                 |
| 6/30 | LOI按钮SVG路径修复                                  |

### 七月：闭环优化

| 日期   | 里程碑                                                  |
| ---- | ---------------------------------------------------- |
| 7/3  | **三数据源数据流打通**（PI合同表+销售订单表+PI合同文件→台账→四种文档），AI解析企微粘贴格式 |
| 7/7  | 报关资料重构、Phase 3整合进Phase 2、MSDS台账改版                    |
| 7/8  | 界面格式统一、台账写入补全、PI解析增强                                 |
| 7/9  | MSDS多选批量生成中英文ZIP包、英文MSDS自动翻译、申报要素修复                  |
| 7/13 | 币制字段全链路打通、报关单模板重构为占位符模式                              |
| 7/16 | 包装计算新增"每桶实际装入量"、台账编辑/删除/判重                           |
| 7/20 | **PI解析接入DeepSeek AI**（优先AI识别→降级Regex匹配，准确率大幅提升）      |
| 7/27 | **产品分组功能**（合并预览支持父子结构、台账持久化、文档生成适配）；PI解析增加付款条款提取及TT/LC分类；订舱单装货港移除广州预设改为自定义选项；UUID兼容HTTP非安全上下文 |
| 7/28 | 新增国家/城市翻译字典与 `parse_destination()`；报关单目的港字段使用解析后的目的字段；币制/数量行自动填充所有产品；新增乌兹别克斯坦/中亚翻译；运费/保险币制自动跟随订单币制 |
| 7/29 | CIF保险英文条款修正（含目的港+C.I.C.）；报关资料装箱单单位/合同日期/保险条款修复；订舱单元数/复数随数量自适应（1→PALLET/DRUM，N→PALLETS/DRUMS）；单位检测遗漏PALLET单数形式修复；报关资料合同sheet合并单元格异常修复；MSDS台账表单优化 |
| 7/31 | 发票号生成保留地区缩写，仅将公司前缀 HT/HH/MH 替换为 IN |

### 八月：架构重构 + 功能增强

| 日期  | 里程碑                                                                                                                                                                      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 8/1 | **🔥 JSON→SQLite 架构重构**：静态数据 JSON 与 users.json 迁入 SQLite（7 张新表 + migration 018）；`products_knowledge` 并入 `customs_codes`；6 个服务改读库；删除 8 个 references JSON 文件；User 正式成为数据库表 |
| 8/1 | 移除文档编辑页空白模板与"我的模板"功能及关联代码（精简）                                                                                                                                            |
| 8/1 | 更新 README/CLAUDE/AGENTS 项目结构、API 概览与功能进度至当前状态                                                                                                                            |
| 8/4 | 报关资料币制显示中文化（USD→美元，CNY/RMB→人民币）                                                                                                                                          |
| 8/4 | **报关单按产品数动态扩展**（解除 6 产品上限，按产品数自动扩展行数）；扩展块行高取自块2                                                                                                                          |
| 8/5 | **PI目的港解析规范化**：国家/港口映射抽至 `core/destination_map.py`，三处目的港提取统一归一化（如 KEELUNG→基隆）                                                                                            |
| 8/5 | **入库前校验包装计算**：未计算包装的产品可确认后强制入库                                                                                                                                           |
| 8/5 | **同一产品支持拆多行录入**：移除批次去重折叠，粘贴同产品多行全部保留（如 3000 拆 1000+2000）；拆行金额按数量×单价分摊；重复检测改为订单级（订单号已入台账弹窗确认后覆盖更新）                                                                        |
| 8/6 | 目的港台账保留源数据（中英混合取英文），港口/国家对照迁入数据库表统一管理                                                                                                                                    |
| 8/6 | 修复 PI 合同表粘贴时行首片段未合并导致未解析到数据的问题                                                                                                                                           |
| 8/6 | MSDS 台账导入增加必填校验，含量不一致时按新配方列出并阻止自动选中                                                                                                                                      |
| 8/10 | **申报要素台账升级为数据中心独立 Tab**：支持条目增删改查与分页搜索，键值字段可视化编辑，编辑/删除后自动刷新缓存；参考文件 Tab 改为切换时按需加载 |
| 8/10 | 申报要素编辑器兼容无冒号的独立字段（如"无品牌""阳离子型"），可切换键值对/独立字段两种模式，长文本多行完整展示不再截断 |
| 8/10 | 修复 Excel/PDF 导入含异常字符导致接口响应崩溃的问题，数据入口/存储/全局响应三层清洗兜底 |
| 8/10 | 申报要素编辑器成分字段按逗号自动分行显示 |
| 8/13 | **申报要素台账重构（按 HS Code 动态字段）**：字段定义与产品要素值分离管理，搜索框改为下拉选择 HS Code；数据看板新增申报要素 Tab 并优化 UI |
| 8/13 | 申报要素页交互对齐 MSDS 台账（默认加载数据、只读表格+弹窗编辑、列宽自适应） |
| 8/13 | 修复报关资料填制单日期规则（发票/箱单/合同各取对应日期，合同保留 PI 日期）；修复合同页产品行丢失（发票页跳过模板预留行与公式布局对齐） |
| 8/14 | 合并预览排序改为 PI 合同表优先 + 颜色高亮，修复排序 Bug；去掉 PI/SO 小图标、统一行背景色 |
| 8/14 | 空格分隔解析保留空列，修复企业微信表格列错位 |

### 交付后反馈与待定项

船务部试用后反馈的调整项：
- 连通性检查按钮
- 反馈按钮
- 操作时长记录
- MSDS翻译优化（成分名匹配、空格差异处理）
- 订单处理功能扩展（产品组合、包装计算优化、价格条款、付款方式等）

> 截至 8/5，部分反馈项已通过功能增强覆盖（如付款方式 TT/LC 分类、价格条款、产品拆行等）。

## T/T 协议使用情况统计（2026-07 ~ 2026-08）

> 统计窗口 2026-07-01 ~ 2026-08-13（44 天）；数据来自生产数据库实采 + 船务部业务汇总（2026-08-18 补入）。

### 使用概况
- **使用人员（业务侧，按登录）**：万凤、李雪、潘慧兰、刘洁婷、向嘉倩、方浩旭（6 人；开发者肖聪的登录不计入业务使用）。
- **清关模块**：尚未开发（见主要问题）。

### 使用次数 / 处理量
| 指标 | 数值 | 说明 |
| --- | --- | --- |
| T/T 总金额 | ¥118,405.75 | 33 条合并记录 |
| L/C 总金额 | ¥137,110.00 | 13 条记录 |
| T/T 总数量 | 48,760 kg | — |
| 有效合并记录量 | 60 条 | — |
| 当前单据记录 | 22 份 | — |
| 价格条款分布（CIF） | 34 条 / ¥97,987.00 | 价格条款之一 |
| 产品类别分布 TOP | 硅油/柔软剂类 ¥160,217.00（31.7%） | 金额占比最高品类 |

### 效率（使用前 / 使用后）
- **使用前**：一份含完整数据的 PI 订单（3 个产品）约 20 分钟制作完成（人工逐项填单）。
- **使用后**：同一份数据约 10 分钟完成，且**单据产品越多提升越明显**。
- 结论：系统将单笔 PI 处理从 ~20 分钟压到 ~10 分钟（约提速 50%），多产品场景增益更大。

### 主要问题
1. **清关模块尚未开发**——当前覆盖订舱 / LOI / MSDS / 报关，清关环节缺位。
2. **审计字段缺少**——仅记录 user_login，无具体操作内容与操作时长（操作时长记录为交付待定项）。
3. **数据库缺少业务员字段**——`sales_person` 全空，无法按人归因与统计采纳率。

### 业务反馈
- 共 **18 条**反馈，覆盖：PI 解析识别、MSDS 台账、MSDS 配方增删改、模板样式修改、包装计算完善。
- 多数已闭环（详见 [[2607_自建应用问题反馈_TT]] / [[2608_自建应用问题反馈_TT]]）。

### 可用佐证
- 生产数据库文件（pi_contracts / order_pi_records / shipment_docs 等）、系统页面台账。

## 个人价值

- 2026-05-28 起独立从 0 开发（前身 `260527_giveup_shipping_helper` PyQt5 桌面版同日废弃），代表从「用 AI 平台」到「自己造企业工具」的能力跃迁。
- OnlyOffice 集成范式（JWT + 单端口代理 + 模板占位符填充）可迁移到后续项目。
- **AI集成里程碑**：7/20 将 DeepSeek AI 嵌入 PI 解析流程，从传统正则匹配升级为 AI 语义识别。
- **架构演进里程碑**：8/1 完成 JSON→SQLite 数据层统一迁移，从"静态文件 + 手动管理"升级为"数据库统一管理 + 迁移脚本"，解决长期存在的 users.json 缺失与用户体系问题。
- **报关单动态扩展**：8/4 解除 6 产品上限，按产品数自动扩展——从"固定模板"升级为"数据驱动模板"。

## 相关知识

- [[20-知识/业务拆解方法/业务需求拆解与AI切入点]] — 基于本项目和采购分析助手提炼的拆解方法论

## 框架化复用（需求池视角）

- [[TT协议可复用技术栈与话术]] — 方总/邓楚羿 8/4 周会指示：把 TT 协议抽象为可复用话术 + 验证过的技术栈，放进需求池快速判断复用场景

## 工作文稿

- [[shipping-helper-项目日志|shipping-helper-项目日志（飞书）]]

## 相关链接

- 后端入口/中间件：`backend/app/main.py`
- 认证服务：`backend/app/services/auth_service.py`
- 路由层：`backend/app/api/v1/*.py`
- 模型层：`backend/app/models/*.py`
- 前端入口：`frontend/src/main.ts`、`router/index.ts`、`stores/auth.ts`、`api/axios.ts`
- 文档：`README.md`、`CLAUDE.md`、`AGENTS.md`、`DEPLOYMENT.md`
