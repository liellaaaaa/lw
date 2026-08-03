import os, re
from collections import defaultdict
ROOT = r"E:\lw"
SKIP = {".workbuddy", ".git", ".obsidian", ".trash", ".codebuddy", "node_modules"}
def canon(p): return os.path.normpath(p).replace(chr(92), '/')

md = []
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in SKIP and not d.startswith('.')]
    for f in fn:
        if f.lower().endswith('.md'): md.append(os.path.join(dp, f))
note_set = set(canon(os.path.splitext(p)[0]) for p in md)
dir_set = set(canon(d) for d in [r for r,_,_ in os.walk(ROOT) if not any(x in r for x in SKIP)])

# folder detection helper for root-relative folder links
def resolve(inner, source_file, fix_pipe=False):
    s = inner
    if fix_pipe:
        s = s.replace(chr(92)+'|', '|')
    core = s.split('|')[0].split('#')[0].strip()
    if core == "" or core.startswith(('http','mailto:')): return True
    is_folder = core.endswith('/') or core.endswith(chr(92))
    t = core.strip().rstrip(chr(92)+'/')
    if t.lower().endswith('.md'): t = t[:-3]
    if t == "": return True
    src_dir = canon(os.path.dirname(source_file))
    cands = []
    if t.startswith('/'):
        cands.append(canon(os.path.join(ROOT, t.lstrip('/'))))
    elif t.startswith('./') or t.startswith('../'):
        cands.append(canon(os.path.join(src_dir, t)))
    elif ('/' in t) or (chr(92) in t):
        cands.append(canon(os.path.join(ROOT, t)))
    last = os.path.basename(t)
    for rel in [x for x in [canon(os.path.relpath(p, ROOT))[:-3] for p in md] if os.path.basename(x)==last]:
        cands.append(canon(os.path.join(ROOT, rel)))
    # also try folder by basename
    for d in dir_set:
        if os.path.basename(d)==last:
            cands.append(d)
    for c in cands:
        if is_folder:
            if c in dir_set: return True
        else:
            if c in note_set: return True
    return False

# count raw \| inside wikilinks
pipe_bad = 0
pipe_files = set()
for p in md:
    try: txt = open(p,encoding='utf-8').read()
    except: continue
    for m in re.finditer(r'\[\[([^\]]+)\]\]', txt):
        if chr(92)+'|' in m.group(1):
            pipe_bad += 1; pipe_files.add(canon(p))
print(f"含 '\\|' 的 wikilink 处数: {pipe_bad}, 涉及文件数: {len(pipe_files)}")

# For each broken link, classify
wikilink_re = re.compile(r'\[\[([^\]]+)\]\]')
broken = defaultdict(list)
for p in md:
    try: txt = open(p,encoding='utf-8').read()
    except: continue
    for m in wikilink_re.finditer(txt):
        inner = m.group(1)
        if inner.split('|')[0].split('#')[0].strip()=="" : continue
        if not resolve(inner, p, fix_pipe=False):
            # try with pipe fix
            if resolve(inner, p, fix_pipe=True):
                kind="FIX_PIPE"
            else:
                kind="GENUINE"
            broken[(kind, inner)].append(canon(p))

genuine = {k:v for k,v in broken.items() if k[0]=="GENUINE"}
fixpipe = {k:v for k,v in broken.items() if k[0]=="FIX_PIPE"}
print(f"\n修正 '\\|'->'|' 后即可恢复: {sum(len(v) for v in fixpipe.values())} 处")
print(f"仍然真断链(修正后): {sum(len(v) for v in genuine.values())} 处\n")
print("### 真断链(修正 \\| 后仍断) ###")
for (kind,inner),srcs in sorted(genuine.items()):
    print(f"  [[{inner}]]  <- {srcs}")
