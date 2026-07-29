import os
root = 'e:/lw'
fixed = []
for dirpath, dirs, files in os.walk(root):
    dirs[:] = [d for d in dirs if d not in ('.codebuddy', '.git', 'node_modules')]
    for f in files:
        if not f.endswith('.md'):
            continue
        p = os.path.join(dirpath, f)
        with open(p, 'r', encoding='utf-8') as fh:
            c = fh.read()
        n = c.replace('[[wiki/', '[[00-原始资料/').replace('[[raw/', '[[raw/未处理/')
        if n != c:
            with open(p, 'w', encoding='utf-8') as fh:
                fh.write(n)
            fixed.append(p)
print('FIXED %d files:' % len(fixed))
for x in fixed:
    print(' -', x)
