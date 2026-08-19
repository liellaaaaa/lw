import zipfile, sys
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def extract(path):
    z = zipfile.ZipFile(path)
    xml = z.read('word/document.xml')
    root = ET.fromstring(xml)
    body = root.find(W+'body')
    out = []
    for el in body.iter():
        tag = el.tag
        if tag == W+'p':
            texts = [t.text or '' for t in el.iter(W+'t')]
            out.append(''.join(texts))
        elif tag == W+'tbl':
            out.append('[TABLE]')
    return '\n'.join(out)

for p in sys.argv[1:]:
    print('\n\n========== FILE: %s ==========' % p)
    try:
        print(extract(p))
    except Exception as e:
        import traceback; traceback.print_exc()
