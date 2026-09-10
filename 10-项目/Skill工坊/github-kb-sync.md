---
created: 2026-09-10
updated: 2026-09-10
period: 入职后
status: 🔄 维护中（随 GitHub 推送手动触发）
tags:
  - 项目
  - Skill
  - 知识库
  - GitHub
  - 同步
department: 内部工具（知识库运维）
requester: 自建
skill_path: ~/.workbuddy/skills/github-kb-sync/
---

# github-kb-sync（GitHub 知识库同步）

**日期**：2026-09-10 归档

> **一句话**：拉取 liellaaaaa 各 repo 最新提交 → 对照知识库已记录状态 → 按重要性分类补写项目主文件/项目日志/索引，保证 lw 与代码仓库不脱节。

## 工作流

1. **取数**：列账号下全部仓库（按 pushed 排序，防漏新仓库）→ 拉有知识库存在的 repo 近 30 提交 → 重大变更拉 commit 详情。
2. **比对**：GitHub `pushed_at` vs 知识库 frontmatter `github_pushed`，找出未记录变更，按 架构变更/功能完成（必记）、bugfix（一行带过）、docs/config（仅状态变化才记）分级。
3. **补写**（顺序固定）：项目主文件 frontmatter + 开发历程表（只增行不改行）→ 项目日志（1-2 行/条，只写做了什么不写怎么做的）→ 汇总文档 → 索引。
4. **提炼**：发现可复用模式时落 20-知识 对应子目录并更新知识索引。

## 写入红线（与知识库规范对齐）

- **只写**：做了什么（结果/能力）、状态变化、里程碑、量化指标、单行 bugfix。
- **绝不写**：函数名/类名/文件路径/变量名/配置键/CSS 选择器/commit SHA/分支名/敏感信息。
- 项目↔repo 映射表内置（ProcurementAnalysis 维护、shippiing_helper 活跃、Tax_check 已交付、ai-sales-coach 活跃；宏昊AI助手/开票明细无 repo 走日报追踪）。

## 踩坑沉淀（取数环节为主）

- **MCP 工具索引每会话重置**：`list_commits` 每次都要重新 ToolSearch 加载，直接调用报 not found；MCP 不可用回退 curl 未认证 REST API（限流 403 别硬试，等整点）。
- **UTC 必须 +8**：API 返回 UTC 时间，写入日报前必须换算并标注（UTC+8），曾把 08:44Z 误标成北京时间导致与企微工作记录对不上。当日查询窗口 = UTC 前一日 16:00Z ~ 当日 15:59Z。
- **committer date ≠ push 时间**：同日两次拉取条数不同通常是用户又 push 了，重新拉即可，别误判异常。
- **沙箱 /tmp 不可写**：临时文件落工作区内并收尾清理，不污染知识库仓库。

## 进度时间线

| 日期 | 进展 |
|---|---|
| 2026-08-31 | SKILL.md 定稿交付（含映射表 + 取数踩坑沉淀） |
| 至今 | 按需手动触发（用户说「同步知识库/拉最新进展」时调用） |

## 下一步

- [ ] 评估是否挂 automation 定期跑（如每周一早上对齐一次）
- [ ] 随项目增减维护映射表（新增 repo/项目文件夹时同步）
