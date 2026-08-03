import os, re
from collections import defaultdict

ROOT = r"E:\lw"
SKIP_DIRS = {".workbuddy", ".git", ".obsidian", ".trash", ".codebuddy", "node_modules"}

# collect all md files and all dirs
md_files = []
all_dirs = set()
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
    all_dirs.add(dirpath)
    for f in filenames:
        if f.lower().endswith('.md'):
            md_files.append(os.path.join(dirpath, f))

# Pre-build set of existing note paths (without .md) and dir paths for fast lookup
def norm(p):
    return os.path.normpath(p)

existing_note_paths = set()  # normalized full path without .md
existing_dir_paths = set()
for p in md_files:
    d = norm(os.path.splitext(p)[0])
    existing_note_paths.add(d)
for d in all_dirs:
    existing_dir_paths.add(norm(d))

def resolve_link(link_text, source_file):
    # strip alias and heading
    target = link_text.split('|')[0].split('#')[0].strip()
    if target == "" or target.startswith('http') or target.startswith('mailto:'):
        return None, target, "skip"
    is_folder = target.endswith('/')
    t = target.rstrip('/')
    # build candidate paths
    src_dir = os.path.dirname(source_file)
    candidates = []
    if t.startswith('/'):
        candidates.append(norm(os.path.join(ROOT, t.lstrip('/'))))
    elif t.startswith('./') or t.startswith('../'):
        candidates.append(norm(os.path.join(src_dir, t)))
    elif '/' in t:
        # Obsidian: path with slash but no ./ is vault-root relative
        candidates.append(norm(os.path.join(ROOT, t)))
    else:
        # bare note name -> search anywhere (Obsidian also allows root-relative bare)
        candidates.append(norm(os.path.join(ROOT, t)))
        candidates.append(norm(os.path.join(src_dir, t)))
    # check
    for c in candidates:
        if is_folder:
            if c in existing_dir_paths:
                return c, target, "ok"
        else:
            if c in existing_note_paths:
                return c, target, "ok"
            # also try with .md already (shouldn't happen) 
    return None, target, "broken"

wikilink_re = re.compile(r'\[\[([^\]]+)\]\]')

broken = defaultdict(list)      # target -> [(source, resolved_candidate)]
placeholder_targets = defaultdict(list)  # template placeholder links
ok_count = 0
skip_count = 0

for p in md_files:
    try:
        with open(p, encoding='utf-8') as fh:
            content = fh.read()
    except:
        continue
    for m in wikilink_re.finditer(content):
        inner = m.group(1)
        # ignore empty
        target = inner.split('|')[0].split('#')[0].strip()
        if target == "":
            continue
        resolved, tname, status = resolve_link(inner, p)
        if status == "ok":
            ok_count += 1
        elif status == "skip":
            skip_count += 1
        else:
            # broken. Distinguish placeholder (in template dir, target looks like placeholder)
            is_tmpl = '\\90-系统模板\\' in p or p.endswith('90-系统模板' + os.sep) or '\\90-系统模板\\' in os.path.relpath(p, ROOT)
            if is_tmpl:
                placeholder_targets[tname].append(p)
            else:
                broken[tname].append((p, resolved))

print("==== 真实断链 (真·目标不存在, 排除模板占位符) ====")
print(f"共 {len(broken)} 个断链目标, {sum(len(v) for v in broken.values())} 处引用\n")
for t, srcs in sorted(broken.items()):
    print(f"◆ [[{t}]]   (被 {len(srcs)} 处链接)")
    for s, _ in srcs:
        print(f"     <- {os.path.relpath(s, ROOT)}")
    print()

print("==== 模板中的占位符链接 (90-系统模板, 大概率是模板预留, 非错误) ====")
for t, srcs in sorted(placeholder_targets.items()):
    print(f"  [[{t}]]  <- {len(srcs)} 处 (模板文件)")
print()
print(f"统计: 有效链接 {ok_count}, 跳过(URL等) {skip_count}, 真实断链 {sum(len(v) for v in broken.values())}")
