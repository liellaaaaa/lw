---
type: 种子
status: 已完成
domain: 技术归档
created: 2026-08-14
modified: 2026-08-14
tags: [type/原子, domain/技术归档, skill/Skill机制, skill/Agent架构, source/开源分析]
related: ["AI集成策略-三种模式与选择", "报价单生成器-Skill制作笔记"]
---

# microsoft/skill-recorder 深度分析

> 一句话总结：微软开源的桌面应用，录制你完成任务的屏幕操作过程，用 GitHub Copilot CLI 逆向重构为"意图+有序步骤"，最终生成可复用的 SKILL.md 或定时 Automation。核心价值不在工具本身（绑定 Copilot 生态），而在于它展示的"示教式 Skill 生成"完整架构。

## 项目概况

| 维度     | 信息                                          |
| ------ | ------------------------------------------- |
| 仓库     | microsoft/skill-recorder                    |
| 版本     | 0.5.0（2026-08-12）                           |
| 许可证    | MIT                                         |
| 首次提交   | 2026-07-25                                  |
| 技术栈    | Electron + React + TypeScript + Vite        |
| AI 引擎  | GitHub Copilot CLI（@github/copilot-sdk）     |
| 语音转写   | Whisper（本地，@huggingface/transformers，99 语言） |
| OCR/脱敏 | Tesseract.js + @secretlint                  |
| 图片处理   | Sharp                                       |
| 模式验证   | Zod                                         |
| 平台     | macOS（主要）/ Windows 11 / Ubuntu              |

## 核心工作流

```
录制（本地）                    分析（上云）                    生成（本地）
┌─────────┐                  ┌──────────┐                 ┌───────────┐
│ 屏幕视频  │                  │ Copilot  │                 │ SKILL.md  │
│ 窗口切换  │  ──bundle.json──>│ describer│──analysis.json─>│ builder   │
│ URL 跟踪  │                  │ 重建意图  │                 │ 泛化步骤   │
│ 剪贴板    │                  │ +步骤列表  │                 │ 生成产物   │
│ 语音旁白  │                  └──────────┘                 └───────────┘
└─────────┘                       │                           │
   全本地                          │                           │
   数据不离开设备                    │                           │
                           用户审查编辑 ◄────────────────────┘
                           可多轮反馈
```

四步流程：Record → Control → Analyze → Create。关键设计：**输出不是 UI 点击回放，而是优先使用 Agent 原生工具**（如 `gh` CLI、`web_fetch`），并从单一示例泛化。

## 架构拆解（源码级）

### 1. 事件系统（common/events.ts）

录制的一切都始于事件。项目定义了一套类型安全的事件模式：

```
EventType = {
  SessionStart, SessionStop, Marker,        // 会话生命周期
  AppActivate, AppTitleChange,              // 窗口跟踪
  ClipboardChange,                          // 剪贴板
  TerminalCommand,                          // 终端（已移除 live producer，保留词汇）
  BrowserUrl,                               // 浏览器 URL
  VideoStart, VideoStop, FrameCaptured      // 视频/帧
}
```

每个事件类型绑定一个 Payload 类型（如 `AppActivatePayload` 包含 app、title、url、host、bounds 等），通过 `EventPayloads` 接口实现 type → payload 的类型映射。采集器（collectors）产出 `EventInput`，会话存储加盖 `seq`、`t`、`epoch` 后持久化为 `RecEvent`，落盘格式是每会话一个 `events.jsonl`。

**设计要点**：事件模式是采集器和消费者（关联引擎、描述器）之间的正式契约，TypeScript 类型系统保证两端类型安全。

### 2. 关联引擎（common/correlation.ts）

这是最精妙的部分。问题：录制同时产生两路数据——事件流（窗口切换/URL/剪贴板）和视频帧序列——如何把它们关联起来？

**核心思路**：事件是主，视频是辅。关联引擎把帧"吸附"到附近的事件上，同时发现两类异常：

| 异常类型 | 含义 | 处理 |
|---------|------|------|
| **unexplained frame** | 画面变了，但附近没有有意义的事件 | 标记为候选微步骤，触发探针请求（加密采样） |
| **silent event** | 有事件发生，但附近没有视觉变化帧 | 记录但不阻塞，说明事件流捕获了视频遗漏的信息 |

**探针机制**（两种）：
1. **unexplained-change probe**：在未解释帧周围 ±1200ms 加密采样（1fps，最多 24 帧）
2. **gap probe**：两个有意义事件之间间隔超过 10 秒时，做一次低频扫描（1fps，最多 12 帧）

探针请求合并去重后输出 `ProbeRequest[]`，由上层决定是否执行二次采样。**这个设计让非视频事件流越丰富，gap 越短，探针越少——自适应地偏向事件流**。

关键参数：`windowMs=1500`（帧吸附窗口）、`probePadMs=1200`、`gapProbeMs=10000`、`maxGapProbes=8`。

### 3. 包构建器（common/bundle.ts）

关联后的数据需要被切成人类可理解的"步骤"。bundle 构建器是纯函数、确定性的，用 Zod 验证输出。

**步骤切分规则**（按优先级）：
1. `app-change`：应用切换（如从 Chrome 切到 VS Code）
2. `url-change`：浏览器 URL host 变化（如从 github.com 切到 google.com）
3. `command`：终端命令执行

其他事件（标题变化、剪贴板、marker）折叠进当前步骤，不触发新步骤。

每个 Step 包含：index、时间范围、boundary 类型、app、titles[]、hosts[]、urls[]、commands[]、clipboardCount、markers[]、eventSeqs[]、frames[]、summary。

输出 `SessionBundle`（版本 1），包含 session 元信息 + steps 数组 + stats 统计。

### 4. 基线描述器（common/describe.ts）

**无 LLM 的确定性描述器**——保证即使没有网络/Copilot 也能产出描述。它把 bundle 渲染成 `description.md`：

```markdown
# Session recording — 2026-08-14 08:00:00 UTC

_3m 42s · 8 steps · 23 events · 15 keyframes_

## Overview
Over 3m 42s the user moved through 8 steps across 3 apps (Chrome, VS Code, Terminal).
Visited 4 sites: github.com, google.com, ...

## Steps

### 1. Chrome — on github.com
`+0:00` · 45s · Chrome
- Opened: `https://github.com/microsoft/skill-recorder`

### 2. ran `git clone ...`
`+0:45` · 12s · Terminal
- Commands: `git clone https://github.com/microsoft/skill-recorder`
```

Copilot describer 在此基础上产出更丰富的叙述，但基线描述器保证"永远有输出"。

### 5. 分析契约（common/analysis.ts）

Copilot describer 的输出不是自由文本，而是结构化的 `Analysis` 对象（Zod 验证）：

```
Analysis = {
  intent: string,              // 用户整体目标
  intentConfidence: "high"|"medium"|"low",
  intentRationale: string,     // 为什么认为这是意图（证据支撑）
  steps: [{
    id: "s1",
    title: "Searched Google for 'interesting articles'",
    detail: "1-3 sentences, past tense, addressed to user",
    apps: ["Microsoft Edge"],
    evidence: ["events", "urls", "frame files"],
    confidence: "high"|"medium"|"low",
    startMs, endMs
  }],
  feedbackLog: [...],          // 反馈轮次记录
  approved: boolean             // 用户是否批准
}
```

**关键设计**：
- 步骤用过去时、第二人称（"You opened..."），不是第三人称（"The user..."）
- 每步都有 confidence 级别和 evidence 引用——可追溯
- 支持多轮反馈：用户用自然语言提反馈 → Copilot 重新分析 → 迭代直到满意 → approved=true
- 只有 approved 的 analysis 才能进入 Skill 生成

### 6. Skill 生成器（common/skill.ts + electron/skillbuilder/）

从 approved analysis 到 SKILL.md 的流程：

```
Analysis (approved) → Copilot agent proposes SkillPlan → 用户审查 → agent submits SkillSubmission → renderSkillMarkdown() → SKILL.md
```

**SkillPlan** 包含：
- `architecture`：目标架构（scout / cowork / agent-skill / copilot-studio）
- `name`：kebab-case ID（如 `submit-expense-records`）
- `title`：人类可读标题
- `description`：触发关键词（成为 SKILL.md frontmatter 的 description）
- `generalization`：如何从单次录制泛化为可重复流程
- `values`：固定值（URL/路径/常量），用 `{{id}}` token 引用
- `steps`：有序步骤，每步标记为 `calculation`（无副作用）或 `action`（有副作用）
- `allowedTools`：允许的原生工具（如 `Bash(git *)`）

**步骤类型区分**是核心设计——`calculation`（读取/推导/格式化）和 `action`（提交/发送/创建/删除）分开，让计划对副作用诚实。

**SKILL.md 格式**：
```markdown
---
name: submit-expense-records
description: "Submit monthly expense records to the finance portal"
allowed-tools:
  - Bash(git *)
  - web_fetch
---

## Steps

1. **Collect receipts** (calculation)
   Scan the ~/Receipts folder for PDF files dated this month...

2. **Submit to portal** (action)
   Open https://finance.internal/submit and upload each receipt...
```

**值替换机制**：录制中的具体值（如某个 URL）在 plan 阶段提取为 `{{id}}` token + ValueSchema，导出时才确定性地替换为字面量。draft 阶段保持 token+值可编辑，只有渲染 SKILL.md 或 automation.json 时才插值。

### 7. Automation 生成器（common/automation.ts）

Automation 是"带触发条件的 Skill"。与 Skill 共享 analysis 输入，但输出格式不同：

**触发器**（AutomationTrigger）：
- `schedule`：定时触发
- `condition`：条件触发（定时检查条件，满足才执行）

**调度类型**（AutomationSchedule，三种）：
- `single`：每天一次，指定时间
- `interval`：间隔触发（intervalMinutes 必须整除 1440）
- `multi`：每天多次，指定多个时间

输出为 Scout 的 `automation.json` 格式，带 `hour`/`minute` 冗余字段以满足 Scout 严格的 import schema。

### 8. 目标架构注册表（common/architecture-registry.ts）

支持 4 种导出目标：

| 架构 ID | 标签 | Skill | Automation | 安装 | 导出 |
|---------|------|-------|------------|------|------|
| `scout` | Scout | ✅ | ✅ | ✅ | ✅ |
| `cowork` | Microsoft 365 Copilot | ✅ | ❌ | ❌ | ✅ |
| `agent-skill` | Agent skill（通用） | ✅ | ❌ | ❌ | ✅ |
| `copilot-studio` | Copilot Studio | ❌（coming soon） | ❌ | ❌ | ❌ |

`agent-skill` 是一个通用目标——数据驱动的架构，不绑定特定工具，只使用可移植能力（文件、shell/CLI、HTTP API）。这为接入非微软生态的 Agent 留了口子。

架构注册表用 `defineArchitectures()` 函数定义，启动时验证：无重复 ID、每个架构至少一个 target、每个 target 至少一个 placement。

### 9. 隐私与安全架构

**分层隐私设计**：

| 层 | 机制 | 实现 |
|----|------|------|
| 录制阶段 | 全本地，数据不离开设备 | Chromium MediaRecorder + 本地事件存储 |
| 语音转写 | 设备端 Whisper（99 语言） | @huggingface/transformers + onnxruntime-node |
| 敏感信息检测 | 发送前扫描密码/PII | @secretlint（文本）+ Tesseract.js（OCR 屏幕） |
| 帧模糊 | 高级保护模式（默认开启） | 设备端帧模糊处理 |
| 非阻塞遮蔽 | 自动遮蔽 + 审查 UI | src/SensitiveReview.tsx |
| Analyze 阶段 | 明确提醒数据将上云 | 每次录制前提醒 |

**关键取舍**：录制完全本地（零网络），只有 Analyze 才上云。这与"数据不出境"原则高度一致。

### 10. 评测体系（evals/）

项目有完整的 fixture-based 评测套件：

| 评测 | 命令 | 评分对象 |
|------|------|---------|
| describer eval | `npm run eval` | 描述器对合成录制的重建质量 |
| builder eval | `npm run eval:builder` | Skill/Automation 泛化能力 |
| skillbuilder eval | `npm run eval:skill` | Skill 构建质量 |
| sensitive eval | `npm run eval:sensitive` | 敏感信息检测准确率 |

评测使用确定性评分规则（rubric），也有可选的 LLM 语义评分器（`judge.ts`，0-5 分）。测试覆盖：音频、麦克风、屏幕、旁白、敏感信息、OCR、帧遮蔽、会话存储、帧提取等。

## 核心设计模式提炼

### 模式 1：事件流为主，视频为辅

```
事件流（窗口/URL/剪贴板/终端）= 主信号
视频帧 = 辅助信号（仅在事件流遗漏时补位）
```

不是"录屏然后让 AI 看视频"，而是"采集结构化事件，视频只用于填补事件间隙"。这让数据量可控、处理确定性高、隐私风险低。

### 模式 2：确定性管道 + LLM 增强

```
确定性基线（describe.ts） ── 保证永远有输出
        ↓
Copilot 增强 ── 更丰富的叙述和泛化
        ↓
用户审查 ── 人工把关
```

每个环节都有"确定性兜底"：describe.ts 保证无网络也能产出描述，skillbuilder 在 Copilot 不可用时回退到 reviewed steps verbatim。

### 模式 3：Plan → Review → Submit 三阶段

```
Copilot proposes Plan → 用户审查/自然语言反馈 → Copilot submits final artifact
```

不是一次性生成，而是"提案-审查-确认"循环。用户可以用自然语言修改计划（"把第 3 步改成..."），Copilot 重新生成。plan 和 submission 是分离的 Zod schema，保证类型安全。

### 模式 4：副作用分类

Skill 步骤分为 `calculation`（无副作用）和 `action`（有副作用），让计划对风险诚实。actions 是需要审查的重点。

### 模式 5：值与步骤分离

录制中的具体值（URL、路径、常量）提取为 `{{id}}` token，在 plan 阶段保持可编辑，导出时才确定性地替换为字面量。这让"录了一次"可以泛化为"跑所有同类任务"。

## 与 WorkBuddy Skill 体系的对照

| 维度 | skill-recorder（微软） | WorkBuddy |
|------|----------------------|-----------|
| Skill 生成方式 | **示教式**：录一遍操作 → AI 观察重建 | **声明式**：人写 SKILL.md 规则 + 工作流 |
| 输入 | 屏幕录制 + 事件流 + 语音旁白 | 人工编写 |
| 泛化能力 | 从单一示例泛化（Copilot 驱动） | 取决于人写的规则覆盖度 |
| 步骤描述 | 自然语言 prompt（给 Agent 执行） | 结构化指令 + 工具调用 |
| 值替换 | `{{id}}` token + 确定性替换 | 参数化 |
| 副作用标记 | calculation vs action 分离 | 无显式区分 |
| 隐私 | 录制全本地 + Analyze 才上云 | 不涉及录制 |
| 评测 | fixture-based eval suite | 无标准化评测 |
| 生态绑定 | GitHub Copilot + Microsoft Scout | WorkBuddy 原生 |

**启示**：两种范式可以互补。WorkBuddy 的声明式 Skill 更精确可控，但编写成本高；skill-recorder 的示教式更易上手，但泛化质量取决于 Copilot。理想方案是"示教生成草稿 → 人工精修 → 声明式部署"。

## 对个人工作的参考价值

### 1. Skill 机制的活教材
面试时面试官建议研究"ReAct 里 Skill 的逻辑"。这个项目完整展示了：Skill 如何从人类操作中提取、意图如何分解为步骤、步骤如何泛化、副作用如何标记。是 Skill 机制的端到端实践参考。

### 2. 隐私优先的录制架构
做退税审单、开票明细等涉及企业敏感数据的工具时，"录制全本地 + Analyze 才上云 + PII 自动遮蔽"是成熟范式。如果未来需要做操作录制类工具（如 SOP 自动生成），这套架构可直接参考。

### 3. 确定性管道 + LLM 增强模式
与已有的 [[AI集成策略-三种模式与选择]] 中的"AI 优先 → 降级兜底"模式互补。skill-recorder 展示了另一种思路："确定性基线 → LLM 增强"，即先保证无 AI 也能工作，再叠加 AI 提升。

### 4. 事件驱动架构设计
关联引擎的"事件为主、视频为辅"思路，以及探针机制的自适应采样，对设计任何"多源数据关联"的系统都有参考价值。

## 局限性

- **强依赖 GitHub Copilot CLI**：没有 Copilot 订阅完全不可用
- **绑定微软生态**：Scout / Copilot Cowork / Copilot Studio 是主要目标，`agent-skill` 通用目标能力有限
- **早期版本**：v0.5.0，2026-07-25 才首次提交，不到一个月
- **macOS 优先**：Windows 支持较新，部分功能（如 URL 跟踪）仅 macOS 可用
- **单示例泛化的局限**：从一次录制泛化出通用 Skill，复杂任务可能不准确
- **终端命令采集已移除**：live terminal producer 不再随附，保留词汇但无 producer

## 可复用经验

1. **事件类型设计要分组**：会话生命周期 / 窗口 / 剪贴板 / 终端 / 浏览器 / 视频，分组让消费者可以按需过滤
2. **Zod 验证贯穿全链路**：从事件 payload 到 analysis 到 skill plan 到 built artifact，每一步都有 schema 验证——类型安全不是可选项
3. **纯函数 + 确定性是基石**：correlate()、buildBundle()、renderDescription() 都是纯函数，无副作用，trivially unit-testable
4. **Plan → Review → Submit 优于一次性生成**：让用户在中间介入，避免"黑盒生成 → 结果不可用"的困境
5. **副作用分类是 Skill 质量的关键**：calculation vs action 的区分让审查聚焦在真正有风险的步骤上
6. **值与步骤分离实现泛化**：具体值变 token，token 可替换，一次录制泛化为通用流程
7. **评测套件不是可选项**：describer / builder / sensitive 都有独立 eval，保证 AI 组件质量可量化

## 来源

- 仓库：https://github.com/microsoft/skill-recorder
- 版本：0.5.0（2026-08-12）
- 核心源码：common/{events,correlation,bundle,describe,analysis,skill,automation,architecture-registry}.ts
- 文档：README.md, docs/future-features.md
- 分析时间：2026-08-14
