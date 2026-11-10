"""Builds the home page, level pages and the shared header/footer/nav inside every lesson.

Run from anywhere:  python3 tools/build.py
Lesson list for each level lives in a hidden <!-- lessons --> block in <level>/index.html,
one line per lesson:  <a class="card" href="/a2/slug" data-title="Title">Title</a>
To add a lesson: copy its HTML to <level>/<slug>.html, add a line to that block, run this script.
"""
import re, os, glob, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SITE_NAME = 'English Exercises'
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600'
         '&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">')

LEVELS = [  # folder, code, name, colour class
    ('a1', 'A1', 'Elementary', 'c-blue'),
    ('a2', 'A2', 'Pre-Intermediate', 'c-butter'),
    ('b1-1', 'B1.1', 'Intermediate', 'c-blush'),
    ('b1-2', 'B1.2', 'Intermediate', 'c-peach'),
    ('b1-plus', 'B1+', 'Intermediate Plus', 'c-cedar'),
    ('b2', 'B2', 'Upper Intermediate', 'c-wine'),
]
COVER_CYCLE = ['c-blue', 'c-butter', 'c-blush', 'c-sand']

DESC_OVERRIDE = {
    'b1-plus/will-shall-going-to': 'Future forms: will / won\'t, shall, be going to · was / were going to',
    'a2/revise-present-simple-continuous': 'Revision: present simple and present continuous',
}

GROUPED = {'b1-1'}  # Roadmap-style: one card per sub-unit (1A, 1B…) with Vocabulary / Grammar
UNIT_RE = re.compile(r'^(\d+[A-Z])\s+(Vocabulary|Grammar)\s*:\s*(.*)$')
KIND_ORDER = {'Vocabulary': 0, 'Grammar': 1}


def plural_uroky(n):
    if n % 10 == 1 and n % 100 != 11: return f'{n} урок'
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14: return f'{n} уроки'
    return f'{n} уроків'


def header_html():
    return (f'<header class="site-header"><div class="hwrap">'
            f'<a class="brand" href="/"><span class="logo-slot" aria-hidden="true">logo</span>'
            f'<span class="brand-name">{SITE_NAME}</span></a>'
            f'<nav class="hnav"><a href="/#levels">Рівні</a><a href="#contacts">Контакти</a></nav>'
            f'</div></header>')


def footer_html():
    return ('<footer class="site-footer" id="contacts"><div class="fwrap">'
            f'<div class="fcol fabout"><div class="fbrand">{SITE_NAME}</div>'
            '<p>Тут буде кілька речень про викладачку: досвід, підхід, з ким працює.</p></div>'
            '<div class="fcol"><h4>Контакти</h4>'
            '<a href="mailto:email@example.com">email@example.com</a>'
            '<a href="tel:+380000000000">+380 00 000 00 00</a>'
            '<a href="https://t.me/username">Telegram: @username</a></div>'
            '<div class="fcol"><h4>Інформація</h4>'
            '<a href="#">Terms &amp; Conditions</a><a href="#">Privacy Policy</a></div>'
            '</div><div class="fbottom"><span>© 2026 ' + SITE_NAME + '</span>'
            '<span>Вправи до уроків англійської · A1–B2</span></div></footer>')


def page(title, body):
    return (f'<!DOCTYPE html>\n<html lang="uk"><head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{title}</title>\n'
            f'{FONTS}\n<link rel="stylesheet" href="/chrome.css">\n<link rel="stylesheet" href="/site.css">\n'
            f'</head>\n<body>\n{header_html()}\n<main class="wrap">\n{body}\n</main>\n{footer_html()}\n</body></html>\n')


def desc(href):
    key = href.strip('/')
    if key in DESC_OVERRIDE: return DESC_OVERRIDE[key]
    f = key + '.html'
    if not os.path.exists(f): return ''
    m = re.search(r'<p class="sub">(.*?)</p>', open(f).read(), re.S)
    if not m: return ''
    d = H.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()
    return re.sub(r'^(English File )?(A1|A2|B1\+?|B1\.[12]|B2)\s*·\s*', '', d)


def cards(folder):
    """Lesson list of a level -> [(href, title)], read from the source lines in its index.html."""
    p = f'{folder}/index.html'
    if not os.path.exists(p): return []
    out = []
    for line in open(p).read().splitlines():
        m = re.match(r'^<a class="card" href="([^"]+)"(?: data-title="([^"]*)")?>(.*)</a>$', line)
        if not m: continue
        title = H.unescape(m.group(2)) if m.group(2) is not None else H.unescape(re.sub(r'<[^>]+>', '', m.group(3)))
        out.append((m.group(1), title))
    return out


def source_block(cs):
    return '<!-- lessons\n' + '\n'.join(
        f'<a class="card" href="{h}" data-title="{H.escape(t)}">{H.escape(t, quote=False)}</a>' for h, t in cs) + '\n-->'


def lesson_card(i, href, title):
    d = desc(href)
    cover = COVER_CYCLE[(i - 1) % len(COVER_CYCLE)]
    return (f'<a class="lcard" href="{href}"><span class="lcover {cover}"><span class="lnum">{i:02d}</span></span>'
            f'<span class="lbody"><span class="lkicker">Урок {i}</span>'
            f'<span class="ltitle">{H.escape(title, quote=False)}</span>'
            + (f'<span class="ldesc">{H.escape(d, quote=False)}</span>' if d else '') + '</span></a>')


def units_html(cs):
    units, order, out = {}, [], []
    for h, t in cs:
        m = UNIT_RE.match(t)
        if not m:
            order.append(('single', h, t)); continue
        u = m.group(1)
        if u not in units:
            units[u] = []; order.append(('unit', u, None))
        units[u].append((m.group(2), m.group(3), h))
    n = 0
    for kind, a, b in order:
        n += 1
        if kind == 'single':
            out.append(lesson_card(n, a, b)); continue
        cover = COVER_CYCLE[(n - 1) % len(COVER_CYCLE)]
        links = ''.join(
            f'<a class="ulink" href="{h}"><span class="k">{k}</span><span class="t">{H.escape(t, quote=False)}</span>'
            f'<span class="arr" aria-hidden="true">→</span></a>'
            for k, t, h in sorted(units[a], key=lambda x: KIND_ORDER[x[0]]))
        out.append(f'<div class="ucard"><div class="lcover {cover}"><span class="lnum">{a}</span></div>'
                   f'<div class="ulinks">{links}</div></div>')
    return '\n'.join(out)


# ---------- level pages ----------
for folder, code, name, cls in LEVELS:
    os.makedirs(folder, exist_ok=True)
    cs = cards(folder)
    if not cs:
        listing = '<p class="empty">Уроки скоро з\'являться.</p>'
    elif folder in GROUPED:
        listing = f'<div class="ugrid">\n{units_html(cs)}\n</div>'
    else:
        listing = '<div class="lgrid">\n' + '\n'.join(lesson_card(i, h, t) for i, (h, t) in enumerate(cs, 1)) + '\n</div>'
    count = f'<span class="lvl-count">{plural_uroky(len(cs))}</span>' if cs else ''
    body = (f'<a class="back" href="/">← Усі рівні</a>\n'
            f'<section class="lvl-hero {cls}"><span class="pill">General English</span>'
            f'<div class="lvl-code">{code}</div><h1>{name}</h1>{count}</section>\n'
            f'{source_block(cs)}\n{listing}')
    open(f'{folder}/index.html', 'w').write(page(f'{code} {name} · {SITE_NAME}', body))

# ---------- home page ----------
tiles = []
for folder, code, name, cls in LEVELS:
    n = len(cards(folder))
    photo = next((p for p in glob.glob(f'img/levels/{folder}.*')), None)
    style = f' style="--photo:url(/{photo})"' if photo else ''
    extra = ' has-photo' if photo else ''
    if n:
        tiles.append(f'<a class="tile {cls}{extra}" href="/{folder}"{style}><span class="code">{code}</span>'
                     f'<span class="tmeta"><span class="name">{name}</span><span class="count">{plural_uroky(n)}</span></span></a>')
    else:
        tiles.append(f'<div class="tile soon"><span class="code">{code}</span>'
                     f'<span class="tmeta"><span class="pill">скоро</span><span class="name">{name}</span></span></div>')
home_body = ('<section class="hero"><div class="hero-text"><span class="pill pill-light">practice for our lessons · A1–B2</span>'
             '<h1>Let\'s make your <mark>practice</mark> perfect</h1>'
             '<p class="hero-sub">Open the exercise from our lesson, check your answers and send me your score.</p></div>'
             '<figure class="hero-photo" aria-hidden="true"><span>photo</span>'
             '<span class="sticker">one lesson<br>at a time</span></figure></section>\n'
             '<section class="section" id="levels"><div class="section-head"><span class="pill">General English</span>'
             '<h2>Choose your level</h2></div>\n<div class="tiles">\n' + '\n'.join(tiles) + '\n</div></section>')
open('index.html', 'w').write(page(SITE_NAME, home_body))

# ---------- lesson pages: theme, header, nav, footer ----------
MARK = re.compile(r'\n?<!-- site-(?:nav|header|footer) -->.*?<!-- /site-(?:nav|header|footer) -->\n?', re.S)
HEADMARK = re.compile(r'<!-- site-head -->.*?<!-- /site-head -->\n', re.S)
for folder, code, name, cls in LEVELS:
    for f in glob.glob(f'{folder}/*.html'):
        if f.endswith('index.html'): continue
        s = HEADMARK.sub('', MARK.sub('', open(f).read()))
        assert s.count('<body><div class="wrap">') == 1 and s.count('</head>') == 1 and s.count('</body>') == 1, f
        s = s.replace('</head>', f'<!-- site-head -->{FONTS}<link rel="stylesheet" href="/chrome.css">'
                                 f'<link rel="stylesheet" href="/lesson-theme.css"><!-- /site-head -->\n</head>', 1)
        s = s.replace('<body><div class="wrap">',
                      f'<body>\n<!-- site-header -->{header_html()}<!-- /site-header -->\n<div class="wrap">\n'
                      f'<!-- site-nav --><nav class="sitenav"><a href="/{folder}">← Усі уроки {code}</a>'
                      f'<a href="/">Усі рівні</a></nav><!-- /site-nav -->\n', 1)
        s = s.replace('</body>', f'\n<!-- site-footer -->{footer_html()}<!-- /site-footer -->\n</body>', 1)
        open(f, 'w').write(s)
print('ok')
