---
created: 2026-07-28
updated: 2026-07-31
tags: [项目, 毕业设计, AI]
period: 入职前
repo: https://github.com/liellaaaaa/LabEqManager
github_created: 2026-01-10
github_pushed: 2026-02-16
---

# LabEqManager · 大学实验室设备管理系统

## 项目简介
本科毕业设计（作者：肖聪）。一个面向高校场景的**实验室设备与场地一体化管理系统**：基于 Spring Boot + Vue 3 前后端分离架构，覆盖设备全生命周期管理、实验室预约、维修/报废、课程资源关联，并集成一个以「本地知识库优先、通义千问兜底」为策略的轻量级 AI 咨询助手。

业务主线是「人—设备—场地—课程」关联的一体化协同管理；角色分管理员（admin）、教师（teacher）、学生（student）三类 RBAC 角色。设计边界（见 `docs/功能清单_规则文件.md`）：所有审批固定两级（申请人→管理员）、前端页面 ≤25 个、演示数据规模 ≤5 实验室/≤50 设备/≤100 用户、AI 严禁生成或修改业务数据。

## 仓库地址
https://github.com/liellaaaaa/LabEqManager

## 技术栈
- 后端：Java 17 + Spring Boot 3.2.5（Maven；groupId `org.cong`，作者肖聪）
  - 核心依赖：spring-boot-starter-web / security / data-jpa / validation、springdoc-openapi（Swagger UI）、mysql-connector-j、JJWT 0.11.5（JWT）、Lombok、阿里云 dashscope-sdk-java 2.8.3（通义千问）
- 前端：Vue 3.5 + TypeScript 5.9 + Vite 7，Vue Router 4、Pinia 3（状态）、Element Plus 2.13（UI）、Axios；ESLint 9 + Prettier 3；Node 要求 `^20.19.0 || >=22.12.0`
- 数据库：MySQL（utf8mb4，InnoDB）；JPA 方言 MySQLDialect，`ddl-auto=none`（表结构由 SQL 脚本手动建）

## 系统架构
- 前后端分离：前端经 Axios 调后端 REST 接口，基址 `http://localhost:8080/api/v1`，后端端口 8080，所有接口统一前缀 `/api/v1/{模块}`。
- 统一响应体：`common/ApiResponse.java` 封装 `{code, message, data}`；前端 Axios 拦截器按 code 判断（200 成功，401 清 token 跳登录，403/404/500 提示）。
- 鉴权：JWT（`JwtTokenProvider` + `JwtAuthenticationFilter`），登录后 token 存 localStorage，请求头 `Authorization: Bearer {token}`；`SecurityConfig` 禁用 CSRF、Session 无状态、CORS 放行 `*` 且允许凭证，放行登录与 Swagger 路径，其余需认证；方法级用 `@PreAuthorize("hasAnyRole('admin','teacher','student')")` 控制。
- 接口文档：springdoc Swagger UI（`/swagger-ui/**`）+ `docs/api-docs/` 下 8 个模块 Markdown 文档（auth/user/equipment/laboratory/borrow/reservation/repair-scrap/ai）。

## 数据模型（来自 lab_equipment_manager.sql，共 17 张表）
- 用户与权限：`user`（username 唯一，含 role_code 冗余字段、status 0/1）、`role`（admin/teacher/student 三枚）、`user_role`（多对多关联，CASCADE）
- 实验室与设备：`laboratory`（name/code 唯一，status 0不可用/1可用/2维护中）、`equipment_status`（待入库/已入库/使用中/维修中/报废字典）、`equipment`（资产编号 asset_code 唯一，须关联实验室）
- 业务流程（均带 approver_id/approve_time/approve_remark 审批字段）：
  - `equipment_borrow`：借用（status 0待审→1通过→2拒绝→3已借出→4已归还→5逾期）
  - `equipment_repair`：维修（0待维修→1维修中→2已修好→3无法修复）
  - `equipment_scrap`：报废（0待审→1通过→2拒绝）
  - `laboratory_reservation`：实验室预约（含联合唯一索引防时间冲突；status 0待审→1通过→2拒绝→3已取消→4已完成→5已使用）
- 课程管理（选做/展示型）：`course`、`course_schedule`、`course_resource`、`course_selection`（学生-课程唯一）
- AI 模块：`ai_knowledge`（知识库问答）、`ai_conversation`（对话记录，落库名实际为 `ai_chat_log`，与 SQL 命名略有出入）
- 初始化：预置 3 角色、5 种设备状态、管理员 `admin`；`lab_equipment_manager_sample_data.sql`（示例数据）、`lab_equipment_manager_ai_knowledge_init.sql`（25 条知识库问答）、`lab_equipment_manager_cleanup.sql`（清业务数据保留基础配置）

## 核心功能模块
- 用户与角色：登录、个人中心；三类角色经 `@PreAuthorize` + 前端路由守卫双重控制
- 实验室管理：实验室 CRUD、状态维护
- 设备全生命周期：增删改查、状态流转（待入库/已入库/使用中/维修中/报废），须关联实验室
- 设备借用：申请→管理员审批→借出→归还→逾期标记的完整闭环（BorrowApply / MyList / Approval 三类视图）
- 实验室预约：申请 + 时间冲突检测 + 两级审批
- 维修与报废：报修状态流转、报废申请与审批
- 课程管理（选做）：课程/安排/资源/选课，仅展示型不做自动排课
- 统计与提醒：`StatisticsController` 提供设备使用次数、借用/逾期统计、到期提醒；提醒仅页面红点 + 列表高亮，无推送

## AI 智能助手（重点亮点）
- 配置：`application.yml` 的 `dashscope.apiKey` + `dashscope.model: qwen-turbo`；`ai/config/DashScopeConfig.java` 绑定。
- 后端 `ai/service/AiAssistantService.java`：单轮对话，接口 `POST /api/v1/ai/chat`。
- 策略「知识库优先，通义千问兜底」：
  - 知识库 `KNOWLEDGE_BASE`（内置 25 条 Map，与 `ai_knowledge_init.sql` 一致），匹配逻辑先完全匹配→包含匹配→关键词提取匹配（带停用词表、2–4 字短语滑动窗口）
  - 未命中则调通义千问，并用**反射**解析 SDK 返回（兼容 2.8.3 返回类型），失败优雅降级
- 安全护栏 `buildPrompt()`：限制 AI 只答系统相关问题、不得生成/修改业务数据、不得执行 SQL/调内部接口、不得答无关话题
- 每次对话落库（来源 knowledge/api），日志失败不影响主流程

## 目录结构要点
- backend（包 `org.cong.backend`）：按 `ai/auth/borrow/equipment/laboratory/repair/reservation/scrap/statistics/user` 分层（各含 controller/dto/entity/repository/service）；公共 `common/`（ApiResponse、BusinessException、GlobalExceptionHandler）；`config/`（SecurityConfig 等）；`security/`（JWT 相关）；测试覆盖 9 个模块 ControllerTest
- frontend（Vue3+TS+Vite）：`src/api/` 按模块拆分统一走 `utils/request.ts`；`src/views/` 20+ 业务视图；`src/stores/user.ts` 管登录态；`router/index.ts` 登录守卫；`vite.config.ts` 仅配 `@` 别名与 vue 插件，无代理靠后端 8080 直连

## 开发 / 测试痕迹
- `开发记录/` 10 篇（01 用户角色→…→09 AI 助手→10 知识库迁移），是与论文对应的开发日志
- `测试记录/` HTML 报告 + 问题汇总，覆盖 Equipment/Laboratory/Borrow/Reservation/Repair/Scrap/Statistics/Ai；`04/05/08/09问题汇总.md` 记录了真实缺陷（字段名不一致、状态码断言偏差、DashScope SDK 类型不匹配改用反射、`ai_chat_log` 建表改用 `ddl-auto=update` 等），体现测试驱动完善
- `docs/`：需求文档 V1.0、功能清单规则文件、8 模块接口文档、系统总体架构图
- `E-R图/` + `pic/`：7 张分模块 + 总 E-R 图；大量 drawio 源文件与导出图（功能结构/数据流/时序【AI 三张+借用四张】/架构/状态/用例/界面截图/类图），文档化程度高

## 亮点 / 可复盘点（毕业设计价值）
1. 架构规范：Spring Boot 分层 + Vue3 组合式 + Pinia + 统一 ApiResponse + 全局异常处理，结构清晰便于答辩
2. 安全设计：JWT 无状态 + Spring Security 方法级 `@PreAuthorize` + 前端路由守卫双重鉴权
3. AI 模块务实：本地知识库优先 + 大模型兜底（零训练成本）、轻量 NLP 匹配、Prompt 安全护栏、答案来源可追溯（可作「可解释 AI」论述点）
4. 工程痕迹完整：需求/功能边界/接口文档/各类图/开发记录/测试报告齐全，体现完整软件生命周期
5. 需求管理意识：清晰区分必做/选做、固定两级审批、页面与演示数据规模约束

### 需注意的已知问题（如实记录，便于答辩说明或修正）
- `AuthController.login` 中密码为**明文比较**（`request.getPassword().equals(user.getPassword())`），与引入 BCrypt、初始化数据用 BCrypt 哈希相矛盾——演示可用但实现不一致，建议答辩说明或改为 `PasswordEncoder` 校验
- `user` 表 `role_code` 冗余字段与 `user_role` 关联表并存，权限以 JWT roleCode + 注解为准，存在一定设计冗余
- AI 知识库「Java 内存 Map」与「MySQL `ai_knowledge` 表」两份并存，代码内置 Map 为主、SQL 表为初始化，二者未完全打通（可作论文下一步工作）
- 前后端契约在字段名/状态码一致性上仍有待统一（测试记录已报）

## 相关链接
- 仓库：https://github.com/liellaaaaa/LabEqManager
- 接口文档：`docs/api-docs/`（仓库内）
- 开发日志：`开发记录/`（仓库内）
