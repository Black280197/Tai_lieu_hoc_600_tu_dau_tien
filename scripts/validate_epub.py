import sys, zipfile, xml.etree.ElementTree as ET

path = sys.argv[1]
z = zipfile.ZipFile(path)
names = z.namelist()

first = names[0]
info = z.getinfo('mimetype')
print('Entry dau tien      :', first)
print('mimetype compress   :', info.compress_type, '(0 = STORED)')
print('mimetype content    :', z.read('mimetype').decode())

xhtml = [n for n in names if n.endswith('.xhtml')]
imgs = [n for n in names if n.startswith('OEBPS/images/')]
print('Tong entry          :', len(names))
print('So xhtml            :', len(xhtml))
print('So anh              :', len(imgs))

ok = True
for n in names:
    if n.endswith(('.xhtml', '.opf', '.ncx', '.xml')):
        try:
            ET.fromstring(z.read(n))
        except Exception as e:
            ok = False
            print('LOI XML:', n, e)
print('XML hop le          :', ok)

ns = {'c': 'http://www.idpf.org/2007/opf'}
opf = ET.fromstring(z.read('OEBPS/content.opf'))
items = opf.findall('.//c:manifest/c:item', ns)
print('Manifest items      :', len(items))

ncx = ET.fromstring(z.read('OEBPS/toc.ncx'))
points = ncx.findall('.//{http://www.daisy.org/z3986/2005/ncx/}navPoint')
print('NCX navPoint        :', len(points))

nav = ET.fromstring(z.read('OEBPS/nav.xhtml'))
NS = {'x': 'http://www.w3.org/1999/xhtml'}
links = nav.findall('.//x:nav[@epub:type="toc"]//x:a',
                    {'x': NS['x'], 'epub': 'http://www.idpf.org/2007/ops'})
print('Nav TOC links       :', len(links))

css = z.read('OEBPS/style.css').decode('utf-8')
print('CSS co e-ink        :', ('#000' in css) and ('break-inside' in css))
print('CSS img max-width   :', 'max-width: 60%' in css)
print()
print('Vi du nhan muc:')
for p in points[:3] + points[-2:]:
    t = p.find('{http://www.daisy.org/z3986/2005/ncx/}navLabel/{http://www.daisy.org/z3986/2005/ncx/}text')
    print('  -', t.text)
