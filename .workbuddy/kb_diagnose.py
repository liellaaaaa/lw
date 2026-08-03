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

# vault-relative path (no .md) for each note, keyed by basename
rel_paths = {}        # vault-relative posix path without .md
basename_map = defaultdict(list)
for p in md_files:
    rel = os.path.relpath(p, ROOT).replace(os.sep, '/')[:-3]
    rel_paths[p] = rel
    bn = os.path.splitext(os.path.basename(p))[0]
    basename_map[bn].append(rel)

def find_note_by_basename(bn):
    return basename_map.get(bn, [])

def diagnose(raw, source_file):
    """Return (category, suggestion)."""
    is_folder = raw.endswith('/') or raw.endswith('\\')
    t = raw.strip().rstrip('\\/')
    if t.lower().endswith('.md'):
        t = t[:-3]
    # candidate by last segment basename
    last = os.path.basename(t.replace('\\','/'))
    matches = find_note_by_basename(last)
    if '.' in last:  # e.g. .pdf
        return ("MISSING_ATTACH", None, last)
    if matches:
        # pick the match; if multiple, pick first
        return ("REWRITE", matches[0], None)
    # try fuzzy: link basename vs existing with minor diff (贵州/贵阳)
    return ("MISSING_NOTE", None, last)

# Now scan for broken links with proper Obsidian-ish resolution
wikilink_re = re.compile(r'\[\[([^\]]+)\]\]')
# rebuild existing note path set
note_set = set(os.path.normpath(os.path.splitext(p)[0]) for p in md_files)

def resolves(raw, src):
    target = raw.split('|')[0].split('#')[0].strip()
    if target == "" or target.startswith(('http','mailto:')):
        return True
    t = target.rstrip('\\/')
    if t.lower().endswith('.md'): t = t[:-3]
    is_folder = target.endswith('/') or target.endswith('\\')
    src_dir = os.path.dirname(src)
    cands = []
    if t.startswith('/'):
        cands.append(os.path.normpath(os.path.join(ROOT, t.lstrip('/'))))
    elif t.startswith('./') or t.startswith('../'):
        cands.append(os.path.normpath(os.path.join(src_dir, t)))
    elif '/' in t or '\\' in t:
        cands.append(os.path.normpath(os.path.join(ROOT, t)))
    last = os.path.basename(t)
    if last and last != t:
        for m in basename_map.get(last, []):
            cands.append(os.path.normpath(os.path.join(ROOT, m)))
    for c in cands:
        if is_folder:
            if os.path.isdir(c): return True
        else:
            if c in note_set: return True
    return False

manifest = []  # (source_rel, raw_inner, category, suggestion)
for p in md_files:
    try:
        content = open(p, encoding='utf-8').read()
    except:
        continue
    for m in wikilink_re.finditer(content):
        inner = m.group(1)
        if inner.split('|')[0].split('#')[0].strip() == "":
            continue
        if resolves(inner, p):
            continue
        cat, sug, extra = diagnose(inner, p)
        manifest.append((os.path.relpath(p, ROOT), inner, cat, sug, extra))

# Dedupe by (source, inner)
seen=set(); uniq=[]
for row in manifest:
    k=(row[0],row[1])
    if k in seen: continue
    seen.add(k); uniq.append(row)

print(f"待修复链接总数: {len(uniq)}\n")
cats = defaultdict(list)
for row in uniq:
    cats[row[2]].append(row)

for cat in ["REWRITE","MISSING_NOTE","MISSING_ATTACH"]:
    rows = cats.get(cat, [])
    print(f"### {cat}  ({len(rows)} 条)")
    for src, inner, c, sug, extra in rows:
        if c=="REWRITE":
            print(f"  [{src}]\n     原: [[{inner}]]\n     改: [[{sug}]]")
        elif c=="MISSING_NOTE":
            print(f"  [{src}]\n     原: [[{inner}]]  -> 目标笔记不存在(疑似命名差异: {extra})")
        else:
            print(f"  [{src}]\n     原: [[{inner}]]  -> 附件不存在: {extra}")
    print()
