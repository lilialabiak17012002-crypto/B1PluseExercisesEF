"""Builds the home page, level pages and the shared header/footer/nav inside every lesson.

Run from anywhere:  python3 tools/build.py
Lesson list for each level lives in a hidden <!-- lessons --> block in <level>/index.html,
one line per lesson:  <a class="card" href="/a2/slug" data-title="Title">Title</a>
To add a lesson: copy its HTML to <level>/<slug>.html, add a line to that block, run this script.
"""
import re, os, glob, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SITE_NAME = 'Your Digital Workbook'
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600'
         '&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">')

GE, BE = 'General English', 'Business English'
LEVELS = [  # folder, code, name, colour class, section
    ('a1', 'A1', 'Elementary', 'c-blue', GE),
    ('a2', 'A2', 'Pre-Intermediate', 'c-butter', GE),
    ('b1-1', 'B1.1', 'Intermediate', 'c-blush', GE),
    ('b1-2', 'B1.2', 'Intermediate', 'c-peach', GE),
    ('b1-plus', 'B1+', 'Intermediate Plus', 'c-cedar', GE),
    ('b2', 'B2', 'Upper Intermediate', 'c-wine', GE),
    ('business-a2-b1', 'A2–B1', 'Pre-Intermediate to Intermediate', 'c-blue', BE),
    ('business-b1-b2', 'B1–B2', 'Intermediate to Upper Intermediate', 'c-butter', BE),
    ('business-b2-c1', 'B2–C1', 'Upper Intermediate to Advanced', 'c-blush', BE),
]
SECTIONS = [(GE, 'English for life'), (BE, 'English for work')]
COVER_CYCLE = ['c-blue', 'c-butter', 'c-blush', 'c-sand']

DESC_OVERRIDE = {
    'b1-plus/will-shall-going-to': 'Future forms: will / won\'t, shall, be going to · was / were going to',
    'a2/revise-present-simple-continuous': 'Revision: present simple and present continuous',
}

GROUPED = {'b1-1': 'Unit', 'b1-2': 'File', 'a1': 'File'}  # one card per sub-unit (1A, 1B…) with Vocabulary / Grammar; value = heading word
UNIT_RE = re.compile(r'^(\d+[A-Z])\s+(?:(.+?)\s+·\s+)?(Vocabulary|Grammar|Additional Grammar)\s*:\s*(.*)$')
KIND_ORDER = {'Vocabulary': 0, 'Grammar': 1, 'Additional Grammar': 2}


def plural_uroky(n):
    return f'{n} lesson' if n == 1 else f'{n} lessons'


def header_html():
    return (f'<header class="site-header"><div class="hwrap">'
            f'<a class="brand" href="/"><span class="logo-slot" aria-hidden="true">logo</span>'
            f'<span class="brand-name">{SITE_NAME}</span></a>'
            f'<nav class="hnav"><a href="/#levels">Levels</a><a href="#contacts">Contact</a></nav>'
            f'</div></header>')


def footer_html():
    return ('<footer class="site-footer" id="contacts"><div class="fwrap">'
            f'<div class="fcol fabout"><div class="fbrand">{SITE_NAME}</div>'
            '<p>Liliia Labiak · English teacher.<br>Exercises for the lessons we do together.</p></div>'
            '<div class="fcol"><h4>Contact</h4>'
            '<a href="mailto:lilia.labiak17012002@gmail.com">lilia.labiak17012002@gmail.com</a>'
            '<a href="tel:+380989960039">+380 98 996 00 39</a>'
            '<a href="https://t.me/Lilia_labiak">Telegram: @Lilia_labiak</a></div>'
            '<div class="fcol"><h4>Info</h4>'
            '<a href="/terms">Terms &amp; Conditions</a></div>'
            '</div><div class="fbottom"><span>© 2026 Liliia Labiak</span>'
            '<span>English practice · A1–C1</span></div></footer>')


def page(title, body):
    return (f'<!DOCTYPE html>\n<html lang="en"><head>\n<meta charset="utf-8">\n'
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
            f'<span class="lbody"><span class="lkicker">Lesson {i}</span>'
            f'<span class="ltitle">{H.escape(title, quote=False)}</span>'
            + (f'<span class="ldesc">{H.escape(d, quote=False)}</span>' if d else '') + '</span></a>')


def units_html(cs, head_word='Unit'):
    units, order, out = {}, [], []
    for h, t in cs:
        m = UNIT_RE.match(t)
        if not m:
            order.append(('single', h, t)); continue
        u = m.group(1)
        if u not in units:
            units[u] = []; order.append(('unit', u, m.group(2)))
        elif m.group(2) and not next(o for o in order if o[0] == 'unit' and o[1] == u)[2]:
            i = next(i for i, o in enumerate(order) if o[0] == 'unit' and o[1] == u); order[i] = ('unit', u, m.group(2))
        units[u].append((m.group(3), m.group(4), h))
    n, cur_unit = 0, None
    for kind, a, b in order:
        n += 1
        if kind == 'single':
            out.append(lesson_card(n, a, b)); continue
        unit_no = re.match(r'\d+', a).group()
        if unit_no != cur_unit:
            cur_unit = unit_no
            out.append(f'<h2 class="unit-head">{head_word} {unit_no}</h2>')
        cover = COVER_CYCLE[(n - 1) % len(COVER_CYCLE)]
        links = ''.join(
            f'<a class="ulink{" extra" if k.startswith("Additional") else ""}" href="{h}"><span class="k">{k}</span><span class="t">{H.escape(t, quote=False)}</span>'
            f'<span class="arr" aria-hidden="true">→</span></a>'
            for k, t, h in sorted(units[a], key=lambda x: KIND_ORDER[x[0]]))
        topic = f'<div class="utopic">{H.escape(b, quote=False)}</div>' if b else ''
        out.append(f'<div class="ucard"><div class="lcover {cover}"><span class="lnum">{a}</span></div>'
                   f'<div class="ubody">{topic}<div class="ulinks">{links}</div></div></div>')
    return '\n'.join(out)


# ---------- level pages ----------
for folder, code, name, cls, section in LEVELS:
    os.makedirs(folder, exist_ok=True)
    cs = cards(folder)
    if not cs:
        listing = '<p class="empty">Lessons coming soon.</p>'
    elif folder in GROUPED:
        listing = f'<div class="ugrid">\n{units_html(cs, GROUPED[folder])}\n</div>'
    else:
        listing = '<div class="lgrid">\n' + '\n'.join(lesson_card(i, h, t) for i, (h, t) in enumerate(cs, 1)) + '\n</div>'
    count = f'<span class="lvl-count">{plural_uroky(len(cs))}</span>' if cs else ''
    body = (f'<a class="back" href="/">← All levels</a>\n'
            f'<section class="lvl-hero {cls}"><span class="pill">{section}</span>'
            f'<div class="lvl-code">{code}</div><h1>{name}</h1>{count}</section>\n'
            f'{source_block(cs)}\n{listing}')
    open(f'{folder}/index.html', 'w').write(page(f'{code} {name} · {SITE_NAME}', body))

# ---------- home page ----------
tiles = {sec: [] for sec, _ in SECTIONS}
for folder, code, name, cls, section in LEVELS:
    long = ' long' if len(code) > 4 else ''
    n = len(cards(folder))
    photo = next((p for p in glob.glob(f'img/levels/{folder}.*')), None)
    style = f' style="--photo:url(/{photo})"' if photo else ''
    extra = ' has-photo' if photo else ''
    if n:
        tiles[section].append(f'<a class="tile {cls}{extra}" href="/{folder}"{style}><span class="code{long}">{code}</span>'
                     f'<span class="tmeta"><span class="name">{name}</span><span class="count">{plural_uroky(n)}</span></span></a>')
    else:
        tiles[section].append(f'<div class="tile soon"><span class="code{long}">{code}</span>'
                     f'<span class="tmeta"><span class="pill">soon</span><span class="name">{name}</span></span></div>')
home_body = ('<section class="hero"><div class="hero-text"><span class="pill pill-light">practice for our lessons · A1–C1</span>'
             '<h1>Let\'s make your <mark>practice</mark> perfect</h1>'
             '<p class="hero-sub">Open the exercise from our lesson, check your answers and send me your score.</p></div>' +
             ('<figure class="hero-photo has-img"><img src="/img/hero.jpg" alt="Illustration: students studying English grammar and vocabulary around a table" width="480" height="480">'
              if os.path.exists('img/hero.jpg') else '<figure class="hero-photo" aria-hidden="true"><span>photo</span>') +
             '<img class="sticker-img" src="/img/sticker.png" width="290" height="155" alt="A little practice goes a long way. You\'ve got this!"></figure></section>\n'
             + '\n'.join(f'<section class="section"{" id=\"levels\"" if i == 0 else ""}><div class="section-head"><span class="pill">{sec}</span>'
                         f'<h2>{h}</h2></div>\n<div class="tiles">\n' + '\n'.join(tiles[sec]) + '\n</div></section>'
                         for i, (sec, h) in enumerate(SECTIONS)))
open('index.html', 'w').write(page(SITE_NAME, home_body))

# ---------- terms page ----------
terms_body = (
    '<a class="back" href="/">← Home</a>\n<article class="doc"><span class="pill">Info</span><h1>Terms &amp; Conditions</h1>'
    '<h2>1. About this website</h2><p>This website contains interactive English exercises for my students. '
    'It is intended only for learning as part of our lessons.</p>'
    '<h2>2. Materials</h2><p>The exercises were created by me or developed on the basis of the topics, grammar and vocabulary of the '
    '<em>English File</em> (Oxford University Press) and <em>Roadmap</em> (Pearson) coursebooks. This website is not affiliated with, '
    'or endorsed by, these publishers. All rights to the coursebooks belong to their publishers and authors. '
    'For complete learning, I recommend using the original coursebooks.</p>'
    '<h2>3. Use of the exercises</h2><p>You are welcome to do and repeat the exercises as many times as you like for your own learning. '
    'Copying, sharing or using the materials of this website for commercial purposes without my permission is not allowed.</p>'
    '<h2>4. Your results and privacy</h2><p>This website does not save your answers and does not collect any personal data. '
    'Your score is visible only to you. If you want me to see it, take a screenshot and send it to me.</p>'
    '<h2>5. Contact</h2><p>If you have any questions, contact me: '
    '<a href="mailto:lilia.labiak17012002@gmail.com">lilia.labiak17012002@gmail.com</a>, '
    '<a href="https://t.me/Lilia_labiak">Telegram @Lilia_labiak</a>, <a href="tel:+380989960039">+380 98 996 00 39</a>.</p>'
    '</article>')
open('terms.html', 'w').write(page(f'Terms & Conditions · {SITE_NAME}', terms_body))

# ---------- lesson pages: theme, header, nav, footer ----------
MARK = re.compile(r'\n?<!-- site-(?:nav|header|footer) -->.*?<!-- /site-(?:nav|header|footer) -->\n?', re.S)
HEADMARK = re.compile(r'<!-- site-head -->.*?<!-- /site-head -->\n', re.S)
for folder, code, name, cls, section in LEVELS:
    for f in glob.glob(f'{folder}/*.html'):
        if f.endswith('index.html'): continue
        s = HEADMARK.sub('', MARK.sub('', open(f).read()))
        assert s.count('<body><div class="wrap">') == 1 and s.count('</head>') == 1 and s.count('</body>') == 1, f
        s = s.replace('</head>', f'<!-- site-head -->{FONTS}<link rel="stylesheet" href="/chrome.css">'
                                 f'<link rel="stylesheet" href="/lesson-theme.css"><!-- /site-head -->\n</head>', 1)
        s = s.replace('<body><div class="wrap">',
                      f'<body>\n<!-- site-header -->{header_html()}<!-- /site-header -->\n<div class="wrap">\n'
                      f'<!-- site-nav --><nav class="sitenav"><a href="/{folder}">← All {code} lessons</a>'
                      f'<a href="/">All levels</a></nav><!-- /site-nav -->\n', 1)
        s = s.replace('</body>', f'\n<!-- site-footer -->{footer_html()}<!-- /site-footer -->\n</body>', 1)
        open(f, 'w').write(s)
print('ok')
