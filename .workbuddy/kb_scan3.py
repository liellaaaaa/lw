import os, re
from collections import defaultdict

ROOT = r"E:\lw"
SKIP_DIRS = {".workbuddy", ".git", ".obsidian", ".trash", ".codebuddy", "node_modules"}

md_files = []
all_dirs = set()
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
    all_dirs.add(dirpath)
    for f in filenames:
        if f.lower().endswith('.md'):
            md_files.append(os.path.join(dirpath, f))

existing_note_paths = set(os.path.normpath(os.path.splitext(p)[0]) for p in md_files)
existing_dir_paths = set(os.path.normpath(d) for d in all_dirs)

# global basename (without .md) -> list of full paths
basename_index = defaultdict(list)
for p in md_files:
    bn = os.path.splitext(os.path.basename(p))[0]
    basename_index[bn].append(os.path.normpath(os.path.splitext(p)[0]))

def clean_target(t):
    t = t.strip()
    t = t.rstrip('\\/')
    if t.lower().endswith('.md'):
        t = t[:-3]
    return t

def resolve_link(link_text, source_file):
    raw = link_text.split('|')[0].split('#')[0].strip()
    if raw == "" or raw.startswith(('http', 'mailto:')):
        return None, raw, "skip"
    is_folder = raw.endswith('/') or raw.endswith('\\')
    t = clean_target(raw)
    if t == "":
        return None, raw, "skip"
    src_dir = os.path.dirname(source_file)
    candidates = []
    if t.startswith('/'):
        candidates.append(os.path.normpath(os.path.join(ROOT, t.lstrip('/'))))
    elif t.startswith('./') or t.startswith('../'):
        candidates.append(os.path.normpath(os.path.join(src_dir, t)))
    elif '/' in t:
        candidates.append(os.path.normpath(os.path.join(ROOT, t)))
    # global basename resolution (Obsidian behavior)
    candidates += basename_index.get(t, [])
    # also try basename of the last path segment for root-relative w/ folder
    last = os.path.basename(t)
    if last and last != t:
        candidates += basename_index.get(last, [])
    seen = set()
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
        if is_folder:
            if c in existing_dir_paths:
                return c, raw, "ok"
        else:
            if c in existing_note_paths:
                return c, raw, "ok"
    return None, raw, "broken"

wikilink_re = re.compile(r'\[\[([^\]]+)\]\]')
broken = defaultdict(list)
placeholder = defaultdict(list)
ok_count = 0

for p in md_files:
    try:
        content = open(p, encoding='utf-8').read()
    except:
        continue
    for m in wikilink_re.finditer(content):
        inner = m.group(1)
        if inner.split('|')[0].split('#')[0].strip() == "":
            continue
        resolved, raw, status = resolve_link(inner, p)
        if status == "ok":
            ok_count += 1
        elif status == "skip":
            pass
        else:
            rel = os.path.relpath(p, ROOT)
            if rel.startswith('90-系统模板' + os.sep) or rel.startswith('90-系统模板'):
                placeholder[raw].append(p)
            else:
                broken[raw].append(p)

print("==== 真实断链 (最终, 已贴近 Obsidian 解析) ====")
print(f"断链目标数: {len(broken)}, 引用处数: {sum(len(v) for v in broken.values())}, 有效链接: {ok_count}\n")
for t, srcs in sorted(broken.items()):
    print(f"◆ [[{t}]]  ({len(srcs)} 处)")
    for s in srcs:
        print(f"     <- {os.path.relpath(s, ROOT)}")
print("\n==== 模板占位符(非错误) ====")
for t, srcs in sorted(placeholder.items()):
    print(f"  [[{t}]] <- {len(srcs)} 处")
