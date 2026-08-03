import os, re
from collections import defaultdict

ROOT = r"E:\lw"
SKIP_DIRS = {".workbuddy", ".git", ".obsidian", ".trash", ".codebuddy", "node_modules"}

md_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
    for f in filenames:
        if f.lower().endswith('.md'):
            md_files.append(os.path.join(dirpath, f))

note_set = set(os.path.normpath(os.path.splitext(p)[0]) for p in md_files)
dir_set = set(os.path.normpath(d) for d in
              [root for root,_,_ in os.walk(ROOT) if not any(x in root for x in SKIP_DIRS)])

# basename -> list of vault-relative posix paths (no .md)
basename_map = defaultdict(list)
for p in md_files:
    bn = os.path.splitext(os.path.basename(p))[0]
    rel = os.path.relpath(p, ROOT).replace(os.sep, '/')[:-3]
    basename_map[bn].append(rel)

def resolve(inner, source_file):
    """Return True if link resolves in Obsidian."""
    # 1) split alias
    core = inner.split('|')[0]
    # 2) split heading
    core = core.split('#')[0].strip()
    if core == "":
        return True  # empty link, skip (rare)
    if core.startswith(('http', 'mailto:')):
        return True
    is_folder = core.endswith('/') or core.endswith('\\')
    t = core.strip().rstrip('\\/')
    if t.lower().endswith('.md'):
        t = t[:-3]
    if t == "":
        return True
    src_dir = os.path.dirname(source_file)
    cands = []
    if t.startswith('/'):
        cands.append(os.path.normpath(os.path.join(ROOT, t.lstrip('/'))))
    elif t.startswith('./') or t.startswith('../'):
        cands.append(os.path.normpath(os.path.join(src_dir, t)))
    elif ('/' in t) or ('\\' in t):
        cands.append(os.path.normpath(os.path.join(ROOT, t)))
    # global basename fallback (Obsidian behavior)
    last = os.path.basename(t)
    for rel in basename_map.get(last, []):
        cands.append(os.path.normpath(os.path.join(ROOT, rel)))
    for c in cands:
        if is_folder:
            if c in dir_set:
                return True
        else:
            if c in note_set:
                return True
    return False

wikilink_re = re.compile(r'\[\[([^\]]+)\]\]')

# collect broken
broken = defaultdict(list)   # inner -> [(src_rel)]
for p in md_files:
    try:
        content = open(p, encoding='utf-8').read()
    except:
        continue
    for m in wikilink_re.finditer(content):
        inner = m.group(1)
        if inner.split('|')[0].split('#')[0].strip() == "":
            continue
        if not resolve(inner, p):
            broken[inner].append(os.path.relpath(p, ROOT))

# dedupe
uniq = {k: sorted(set(v)) for k, v in broken.items()}

# categorize each broken inner
def categorize(inner):
    core = inner.split('|')[0].split('#')[0].strip()
    if core.startswith(('http', 'mailto:')):
        return "URL"
    is_folder = core.endswith('/') or core.endswith('\\')
    t = core.strip().rstrip('\\/')
    if t.lower().endswith('.md') or '.' in os.path.basename(t):
        return "MISSING_ATTACH"
    if t.startswith('./') or t.startswith('../') or ('/' in t) or ('\\' in t):
        return "BAD_PATH"
    return "MISSING_NOTE"

cats = defaultdict(list)
for inner, srcs in uniq.items():
    cats[categorize(inner)].append((inner, srcs))

print(f"=== 真正断链总数: {sum(len(v) for v in uniq.values())} 处, 涉及 {len(uniq)} 个不同链接 ===\n")
for cat in ["BAD_PATH", "MISSING_NOTE", "MISSING_ATTACH"]:
    rows = cats.get(cat, [])
    print(f"### {cat}  ({sum(len(s) for _,s in rows)} 处引用, {len(rows)} 个不同链接)")
    for inner, srcs in sorted(rows):
        print(f"  [[{inner}]]")
        for s in srcs:
            print(f"      <- {s}")
    print()

# Also report the garbage-named empty file explicitly
print("### 异常文件名(结构错误) ###")
for p in md_files:
    if any(c in os.path.basename(p) for c in '[]|'):
        size = os.path.getsize(p)
        print(f"  {os.path.relpath(p, ROOT)}  (size={size})")
print("\n### 空文件(0字节) ###")
for p in md_files:
    if os.path.getsize(p) == 0:
        print(f"  {os.path.relpath(p, ROOT)}")
