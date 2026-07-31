---
type: 种子
status: 已完成
domain: 技术归档
created: 2026-07-31
modified: 2026-07-31
tags: [type/原子, domain/技术归档, skill/python-docx, skill/word模板]
related: []
---

# 报价单生成器 Skill 制作笔记

> 💡 一句话总结：业务员发来非结构化消息（公司/产品/电话等），脚本用 python-docx 读取 Word 模板、替换 `{{占位符}}`、填充表格，一步生成报价单 .docx。

## 解决什么问题

客服部收到业务员发来的订单信息（微信/文本，格式不固定），需要手动填到 Word 报价单模板里。这个 skill 把"解析消息 → 填模板 → 输出 docx"自动化，省去人工复制粘贴。

## 核心结论

- **python-docx 模板填充法**是轻量级 Word 自动化的首选：跨平台、不需要装 Word、纯 Python。
- 对比 win32com（COM 自动化）：win32com 能力更强但依赖 Windows + Word 安装，慢且重；python-docx 够用且通用。
- 非结构化消息用正则按"字段：值"模式解析，够轻量，不需要上 NLP。

## 使用场景

- 业务员直接发文本消息，需要快速生成格式化 Word 文档。
- 模板固定、字段明确的单次文档生成场景。
- 任何"文本输入 → Word 模板填充 → 输出"的小工具需求都可复用这套模式。

## 方法与步骤

### 1. 模板设计

Word 模板里用 `{{占位符}}` 标记替换位置：
- 段落级：`{{公司名}}`、`{{负责人}}`、`{{电话}}`、`{{日期}}`
- 表格级：产品行按序号填充（品名/单价/备注），最后一行放 `{{说明}}`

### 2. 消息解析（正则）

业务员消息格式示例：
```
公司：顺德新阳织染
产品：
1. 纯棉府绸 13372 18.5元/米 白色
2. 涤纶布 13372 12元/米 黑色
负责人：张三
电话：13800138000
```

解析逻辑：
- 按 `字段：值` 正则 `^(.+?)[：:](.+)$` 提取键值对
- 产品行用 `^\d+\.` 识别，再从每行拆出品名/单价/颜色备注
- 单价匹配：`(\d+(?:\.\d+)?)\s*元\s*/?\s*米`

### 3. 段落占位符替换

```python
for para in doc.paragraphs:
    for run in para.runs:
        for key in ['{{公司名}}', '{{负责人}}', '{{电话}}', '{{日期}}']:
            if key in run.text:
                run.text = run.text.replace(key, data.get(key.strip('{}'), ''))
```

> ⚠️ 这里有个坑，见下方"踩坑点"。

### 4. 表格填充

```python
for table in doc.tables:
    for row_idx, row in enumerate(table.rows):
        if row_idx == 0:          # 跳过表头
            continue
        if row_idx == len(table.rows) - 1:  # 最后一行放说明
            ...
        idx = row_idx - 1
        if idx < len(products):
            row.cells[0].text = str(idx + 1)     # 序号
            row.cells[1].text = products[idx]['name']
            row.cells[2].text = products[idx]['price']
            row.cells[3].text = products[idx]['remark']
        else:
            for cell in row.cells:               # 多余行清空
                cell.text = ''
```

## 踩坑点

### ⚠️ Word run 级替换会失效

**问题**：Word 把一个段落里的文字拆成多个 `run`（格式片段）。如果 `{{公司名}}` 被拆到了两个 run 里（比如 `{{公司` + `名}}`），`run.text.replace()` 根本匹配不到。

**解法**（`patch_template.py` 的方案）：把段落所有 run 合并成完整字符串，整体替换后写回第一个 run，清空其余 run：

```python
def patch_paragraphs(paragraphs):
    for p in paragraphs:
        if not p.runs:
            continue
        original = ''.join(r.text for r in p.runs)
        new = original
        for old, repl in REPLACEMENTS:
            new = new.replace(old, repl)
        if new != original:
            p.runs[0].text = new
            for r in p.runs[1:]:
                r.text = ''
```

**取舍**：这会丢失段落内多 run 的差异化格式（比如一句话里部分加粗），但对报价单这种"整段同格式"的场景没问题。如果需要保留行内格式，得逐 run 拼接后做更精细的回写。

### ⚠️ python-docx 无法直接操作 .doc

模板必须是 `.docx` 格式。如果原始模板是 `.doc`，先用 Word 另存为 `.docx`。

## 判断标准

- 模板字段用 `{{}}` 占位符标记 → 替换成功
- 产品行数 ≤ 模板预留行数 → 正常填充；超出 → 需要扩展模板或截断
- 生成的文件名格式：`报价单_公司名_日期.docx`

## 适用边界

- **适用**：模板固定、字段明确、单次生成、格式简单的 Word 文档。
- **不适用**：需要复杂排版动态调整、需要图表/图片动态插入、需要 .doc 格式输出、需要行内混合格式保留的场景。
- 复杂场景考虑 win32com 或 python-docx 的更深度 API（样式/节/图片操作）。

## 可复用经验

1. **"文本输入 → Word 模板填充"是高频小工具模式**，这套解析+替换+表格填充的骨架可直接搬运。
2. **占位符替换永远做段落级合并**，不要信任 run 级替换——这是 Word 自动化最大的坑。
3. **python-docx 优先于 win32com**，除非确实需要 Word 独有功能（修订/宏/复杂排版）。
4. 非结构化消息解析用正则就够了，不用上 NLP——业务消息通常有"字段：值"的隐式结构。

## 相关笔记

- [[OnlyOffice 单端口集成模式]] — 另一种 Word 文档自动化方案（在线编辑），适合需要协作的场景

## 来源

- Skill 源目录：`C:\Users\windows\Desktop\客服-报价单生成\quotation-generator\`
- 关键文件：
  - `scripts/generate_word.py` — 主生成脚本
  - `scripts/patch_template.py` — 模板补丁脚本（run 级替换解法）
  - `assets/templates/报价单模板.docx` — Word 模板
  - `references/template-fields.md` — 模板字段文档
- 制作时间：2026-07-20
