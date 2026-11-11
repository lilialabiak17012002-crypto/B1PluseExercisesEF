"""Grammar explanations under wrong answers.

  python3 tools/why.py patch                 add the explanation code to every lesson page (safe to re-run)
  python3 tools/why.py dump a2/some-lesson    print the exercises of a page compactly (for writing explanations)
  python3 tools/why.py apply a2/some-lesson file.json

file.json: {"<section number n>": {"rule": ["bullet", ...], "items": {"<item number, 1-based>": ["bullet", ...]}}}
"rule" bullets are shown under every wrong answer of that exercise; "items" bullets are added for that one question.
Bullets may contain <b>, <u>, <i>, <s>. A1 and A2 pages show "Правильна відповідь", other levels "Correct answer".
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SECS_RE = re.compile(r'const SECS=(\[.*?\]);\n', re.S)
UK = ('a1', 'a2')

CSS = ('.why{background:#F7F4EE;border:1px solid #E4DCCD;border-left:4px solid var(--ink);border-radius:10px;padding:12px 16px;'
       'margin:10px 0 4px;color:var(--ink);font-size:15.5px;line-height:1.6}\n'
       '.why-ans{color:var(--green);font-weight:700;margin-bottom:4px}\n'
       '.why ul{margin:0;padding-left:18px}.why li{margin:2px 0}.why li::marker{content:\'▸  \';color:var(--muted)}\n'
       '.why u{text-decoration-thickness:1.5px;text-underline-offset:3px;font-weight:600}\n')
A_LI = "const li=mk('li','q');ol.append(li);const fix=mk('div','fix');"
A_CHECK = "const [li,ok]=f();li.dataset.done='1';li.classList.add(ok?'ok':'bad');"
A_DOLLAR = "const $=id=>document.getElementById(id);"


def js(lang):
    return (f"const WHY_LANG='{lang}';\n"
            "function showWhy(li){const fix=li.querySelector('.fix');const ans=fix.textContent.replace(/^✗ Правильно:\\s*/,'');fix.textContent='';\n"
            "  const box=mk('div','why');box.append(mk('div','why-ans',(WHY_LANG==='en'?'Correct answer: ':'Правильна відповідь: ')+ans));\n"
            "  const ul=mk('ul');li._why.forEach(h=>{const x=mk('li');x.innerHTML=h;ul.append(x);});box.append(ul);fix.append(box);}\n")


def pages():
    for f in sorted(glob.glob('*/*.html')):
        if f.endswith('index.html') or f.startswith('tools/'): continue
        s = open(f).read()
        if SECS_RE.search(s): yield f, s


def patch():
    n = 0
    for f, s in pages():
        lang = 'uk' if f.split('/')[0] in UK else 'en'
        s = re.sub(r"const WHY_LANG='(uk|en)';\n", f"const WHY_LANG='{lang}';\n", s)
        if 'function showWhy' not in s:
            assert s.count(A_LI) == 1 and s.count(A_CHECK) == 1 and s.count(A_DOLLAR) == 1, f
            s = s.replace(A_LI, A_LI + "li._why=[...(sec.why||[]),...(it.why||[])];if(!li._why.length)li._why=null;", 1)
            s = s.replace(A_CHECK, A_CHECK + "if(!ok&&li._why)showWhy(li);", 1)
            s = s.replace(A_DOLLAR, js(lang) + A_DOLLAR, 1)
            s = s.replace('</style>', CSS + '</style>', 1)
        else:  # older pilot: per-item only -> section + item
            s = s.replace("li._why=it.why;", "li._why=[...(sec.why||[]),...(it.why||[])];if(!li._why.length)li._why=null;")
        open(f, 'w').write(s); n += 1
    print('patched', n)


def load(page):
    f = page if page.endswith('.html') else page + '.html'
    s = open(f).read(); m = SECS_RE.search(s)
    return f, s, m, json.loads(m.group(1))


def dump(page):
    f, s, m, secs = load(page)
    for sec in secs:
        if sec['type'] == 'explain':
            print('[RULE CARD]', re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', sec['html']))[:1500]); continue
        print(f"\n## {sec['n']} {sec['type']} | {sec['title']} | {sec.get('task','')}" + (f" | bank: {', '.join(sec['bank'])}" if sec.get('bank') else ''))
        for i, it in enumerate(sec['items'], 1):
            if sec['type'] == 'match': print(f"{i}. {it[0]} => {it[1]}")
            elif sec['type'] == 'choice': print(f"{i}. {it['t']}  [{' / '.join(it['o'])}] => {it['o'][it['c']]}")
            elif sec['type'] == 'order': print(f"{i}. {it['t']} => {it['a'][0]}")
            else: print(f"{i}. {it['t']} => {' | '.join('/'.join(a) for a in it['a'])}")


def apply(page, path):
    f, s, m, secs = load(page)
    data = json.load(open(path))
    by_n = {str(x.get('n')): x for x in secs if x['type'] != 'explain'}
    for n, d in data.items():
        sec = by_n[n]
        if d.get('rule'): sec['why'] = d['rule']
        for i, b in d.get('items', {}).items():
            sec['items'][int(i) - 1]['why'] = b
    s = s[:m.start(1)] + json.dumps(secs, ensure_ascii=False) + s[m.end(1):]
    open(f, 'w').write(s)
    print('applied', f, len(data), 'sections')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'patch': patch()
    elif cmd == 'dump': [dump(p) for p in sys.argv[2:]]
    elif cmd == 'apply': apply(sys.argv[2], sys.argv[3])
