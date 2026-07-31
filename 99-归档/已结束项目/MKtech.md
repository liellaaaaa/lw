---
created: 2026-07-28
updated: 2026-07-31
tags:
  - 项目
  - 学习记录
  - Python
  - 练手项目
period: 入职前
repo: https://github.com/liellaaaaa/MKtech
github_created: 2025-10-19
github_pushed: 2025-10-21
---

# MKtech · 三个月 Python+AI 学习档案与练手项目 TaskMpg

## 项目简介

这是一份 **2025 年 10 月起约三个月的 Python + AI 学习记录**，而非生产应用。仓库混合了两层内容：
1. **学习资料**：按周组织的文档（第一周/第二周），含 PDF / PPTX / DOCX / Markdown，记录该阶段学习的 Python 与 AI 知识点与任务。
2. **练手项目 `TaskMpg`**：第一周里用 Python 写的一个命令行**任务管理器**，用于巩固基础（文件 IO、函数、数据结构、异常处理等）。

作为「学习档案」价值在于：能回看自己从 0 到 1 的练习轨迹与代码演进。

## 仓库地址

https://github.com/liellaaaaa/MKtech

## 技术栈

- Python（标准库为主，文件存储，无第三方依赖）
- 开发环境：IntelliJ / PyCharm（含 `.idea/` 配置，已入库）
- 资料格式：PDF / PPTX / DOCX / Markdown

## 系统架构（TaskMpg）

命令行工具，模块划分：
- `task_manager.py`：主程序 / 交互入口
- `task_operations.py`：任务增删改查等操作
- `data_handler.py`：读写 `tasks.txt` 数据文件
- `tasks.txt`：任务数据存储（纯文本/行式）
- `test_cases.txt`：测试用例
- `README.md`：项目说明

数据流：用户输入 → `task_manager` → `task_operations` → `data_handler` ↔ `tasks.txt`。

## 数据模型

- `tasks.txt`：以行式/分隔符存储任务（标题、状态、备注等），由 `data_handler` 解析

## 核心功能模块（TaskMpg）

- **task_manager.py**：命令行交互与调度
- **task_operations.py**：新增 / 删除 / 查询 / 修改任务
- **data_handler.py**：持久化（读写 `tasks.txt`）
- **test_cases.txt**：手测用例

## 目录结构要点

- `第一周/TaskMpg/`：练手项目源码（Python）
- `第一周/doc1/第一周任务.md`：当周任务说明
- `第二周/`：学习资料
- 含二进制学习资料（PDF/PPTX/DOCX）与 `.idea/` IntelliJ 配置

## 亮点 / 可复盘点

- 完整的「从 0 学 Python」轨迹，适合复盘与教学参考
- TaskMpg 用纯标准库实现 CRUD，是文件 IO / 函数拆分的好范例

## 需注意的已知问题

- **仅单机文件存储**：`tasks.txt` 无并发/一致性保障，多人/多进程不可用
- **异常处理偏弱**：练手阶段，边界输入（空行、格式错）可能未充分处理
- `.idea/` 与二进制资料已入库，建议加 `.gitignore` 并改用 LFS/外链管理大文件

## 相关链接

- 练手项目：`第一周/TaskMpg/task_manager.py`、`task_operations.py`、`data_handler.py`
- 任务说明：`第一周/doc1/第一周任务.md`
