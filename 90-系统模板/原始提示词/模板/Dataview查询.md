# Dataview 查询合集

> 复制到任意笔记或 MOC 中使用，配合 Dataview 插件。下列查询默认排除模板与归档目录。
> 库相对路径下，归档目录为 `00-原始资料/项目/归档`；模板在 `02-方法库与提示词/模板`。

## 1. 孤立笔记（无入链/出链）
```dataview
LIST
WHERE length(file.inlinks) = 0 AND length(file.outlinks) = 0
AND file.folder != "02-方法库与提示词/模板"
AND file.folder != "00-原始资料/项目/归档"
```

## 2. 本周新建的笔记
```dataview
TABLE type, status
WHERE file.cday >= date(today) - dur(7 days)
SORT file.cday DESC
```

## 3. 所有草稿（待完善）
```dataview
TABLE type, file.mtime as "最后修改"
WHERE status = "草稿"
SORT file.mtime ASC
```

## 4. 按标签统计笔记数
```dataview
TABLE WITHOUT ID
file.tags AS "标签",
length(rows) AS "笔记数"
FROM ""
WHERE file.tags
FLATTEN file.tags AS tag
GROUP BY tag
SORT length(rows) DESC
```

## 5. 长期未修改（30 天+）
```dataview
TABLE type, status, file.mtime as "最后修改"
WHERE file.mtime < date(today) - dur(30 days)
AND status != "归档"
AND file.folder != "02-方法库与提示词/模板"
SORT file.mtime ASC
```
