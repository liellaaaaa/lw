import os, re, json
from collections import defaultdict

ROOT = r"E:\lw"
SKIP_DIRS = {".workbuddy", ".git", ".obsidian", ".trash", ".codebuddy", "node_modules"}

md_files = []
empty_dirs = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
    has_md = any(f.lower().endswith('.md') for f in filenames)
    # record empty dirs (no md, no non-skip subdirs)
    if not has_md and not dirnames and not any(not f.startswith('.') for f in filenames):
        empty_dirs.append(dirpath)
    for f in filenames:
        if f.lower().endswith('.md'):
            md_files.append(os.path.join(dirpath, f))

name_to_paths = defaultdict(list)
for p in md_files:
    base = os.path.splitext(os.path.basename(p))[0]
    name_to_paths[base].append(p)

file_info = {}
for p in md_files:
    try:
        size = os.path.getsize(p)
        with open(p, encoding='utf-8') as fh:
            content = fh.read()
    except Exception as e:
        content = ""
        size = -1
    stripped = content.strip()
    file_info[p] = {"size": size, "empty": len(stripped) == 0, "chars": len(stripped)}

wikilink_re = re.compile(r'\[\[([^\]]+)\]\]')
mdlink_re = re.compile(r'\]\(([^)]+)\)')

incoming = defaultdict(list)   # target basename -> source files
empty_wikilinks = defaultdict(list)  # source -> list of '[[ ]]' empty links
all_wikilinks = defaultdict(list)

for p in md_files:
    try:
        with open(p, encoding='utf-8') as fh:
            content = fh.read()
    except:
        continue
    for m in wikilink_re.finditer(content):
        inner = m.group(1)
        target = inner.split('|')[0].split('#')[0].strip()
        if target == "":
            empty_wikilinks[p].append(m.group(0))
            continue
        all_wikilinks[p].append(target)
        incoming[target].append(p)
    for m in mdlink_re.finditer(content):
        tgt = m.group(1)
        if tgt.startswith(('http', '#', 'mailto:', 'data:')):
            continue
        if '.md' in tgt:
            base = tgt.split('#')[0].rsplit('.md', 1)[0]
            base = os.path.basename(base)
            incoming[base].append(p)
            all_wikilinks[p].append(base)

# Broken links: linked target not found anywhere
broken = {}
for target, sources in incoming.items():
    if target not in name_to_paths and not target.startswith(('http',)):
        broken[target] = sorted(set(sources))

# Empty files
empty_files = [p for p, info in file_info.items() if info["empty"]]

# Empty files that are linked (have incoming)
empty_linked = []
for p in empty_files:
    base = os.path.splitext(os.path.basename(p))[0]
    if base in incoming:
        empty_linked.append((p, sorted(set(incoming[base]))))

# Weird filenames containing link syntax chars
weird = [p for p in md_files if any(c in os.path.basename(p) for c in '[]|')]

# Dup basenames
dups = {n: ps for n, ps in name_to_paths.items() if len(ps) > 1}

# Orphan files: no incoming and no outgoing
orphans = []
for p in md_files:
    base = os.path.splitext(os.path.basename(p))[0]
    has_in = base in incoming
    has_out = len(all_wikilinks.get(p, [])) > 0
    if not has_in and not has_out:
        orphans.append(p)

print("==== 扫描统计 ====")
print(f"Markdown 文件总数: {len(md_files)}")
print(f"空文件(0字节/纯空白): {len(empty_files)}")
print(f"断链目标(被链接但找不到文件): {len(broken)}")
print(f"空 [[ ]] 链接(指向空): {sum(len(v) for v in empty_wikilinks.values())} 处")
print(f"重名 basename: {len(dups)}")
print(f"孤立文件(无入链无出链): {len(orphans)}")
print(f"空目录: {len(empty_dirs)}")
print()
print("==== 空文件列表 ====")
for p in empty_files:
    rel = os.path.relpath(p, ROOT)
    print(f"  {rel}  (size={file_info[p]['size']})")
print()
print("==== 文件名含链接语法的文件(异常名) ====")
for p in weird:
    rel = os.path.relpath(p, ROOT)
    print(f"  {rel}")
print()
print("==== 断链目标(被链接但文件不存在) ====")
for t, srcs in sorted(broken.items()):
    print(f"  目标: [[{t}]]  被 {len(srcs)} 处链接:")
    for s in srcs:
        print(f"      <- {os.path.relpath(s, ROOT)}")
print()
print("==== 空 [[ ]] 链接 ====")
for s, lst in empty_wikilinks.items():
    print(f"  {os.path.relpath(s, ROOT)}: {len(lst)} 处空链接")
print()
print("==== 空文件但被链接(删了会断链) ====")
for p, srcs in empty_linked:
    print(f"  {os.path.relpath(p, ROOT)}  被链接自:")
    for s in srcs:
        print(f"      <- {os.path.relpath(s, ROOT)}")
print()
print("==== 重名文件 ====")
for n, ps in dups.items():
    print(f"  [{n}]")
    for p in ps:
        print(f"      {os.path.relpath(p, ROOT)}")
print()
print("==== 空目录 ====")
for d in empty_dirs:
    print(f"  {os.path.relpath(d, ROOT)}")
print()
print("==== 孤立文件(前20) ====")
for p in orphans[:20]:
    print(f"  {os.path.relpath(p, ROOT)}")
