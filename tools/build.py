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
    ('business-c1', 'C1', 'Advanced', 'c-peach', BE),
]
SECTIONS = [(GE, 'English for life'), (BE, 'English for work')]
STICKER = {GE: ('climb', 'Sticker: a student climbing a staircase of books'), BE: ('presentation', 'Sticker: a presentation at work')}
STICKERS = {'climb': 'Sticker: a student climbing a staircase of books', 'desk': 'Sticker: a student working at a laptop',
            'books': 'Sticker: a stack of books', 'friends': 'Sticker: two students talking with books',
            'think': 'Sticker: a student thinking', 'notes': 'Sticker: a student planning with sticky notes',
            'interview': 'Sticker: a job interview', 'presentation': 'Sticker: a presentation at work'}
LEVEL_STICKER = {'a1': 'friends', 'a2': 'climb', 'b1-1': 'notes', 'b1-2': 'books', 'b1-plus': 'think', 'b2': 'desk',
                 'business-a2-b1': 'interview', 'business-b1-b2': 'presentation', 'business-b2-c1': 'think', 'business-c1': 'desk'}

def level_sticker(folder):
    f = LEVEL_STICKER.get(folder)
    return f'<img class="dc-sticker" src="/img/stickers/{f}.png" alt="{STICKERS[f]}" loading="lazy">' if f and os.path.exists(f'img/stickers/{f}.png') else ''

def sticker(sec):
    f, alt = STICKER[sec]
    return f'<img class="dc-sticker" src="/img/stickers/{f}.png" alt="{alt}" loading="lazy">' if os.path.exists(f'img/stickers/{f}.png') else ''
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


ICONS = ('<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" href="/img/icon-32.png">'
         '<link rel="apple-touch-icon" href="/img/icon-180.png">')


def header_html():
    return (f'<header class="site-header"><div class="hwrap">'
            f'<a class="brand" href="/"><img class="logo-slot" src="/img/logo.png" width="48" height="48" alt="">'
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


def page(title, body, head=''):
    return (f'<!DOCTYPE html>\n<html lang="en"><head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{title}</title>\n'
            f'{FONTS}\n{ICONS}\n<link rel="stylesheet" href="/chrome.css">\n<link rel="stylesheet" href="/site.css">\n{head}'
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
            f'<div class="lvl-code">{code}</div><h1>{name}</h1>{count}{level_sticker(folder)}</section>\n'
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
                         f'<h2>{h}</h2>{sticker(sec)}</div>\n<div class="tiles">\n' + '\n'.join(tiles[sec]) + '\n</div></section>'
                         for i, (sec, h) in enumerate(SECTIONS)))
open('index.html', 'w').write(page(SITE_NAME, home_body))

# ---------- about page: link-only, at /meet-liliia (not in the menu, noindex) ----------
SAMPLES = [  # (embed url, open url, title, what the lesson is)
    ('https://docs.google.com/presentation/d/19TMewG2A5rG4Q1t2ErUFBR7-QPD-stbqkpYmHFQB6-g/embed?start=false&amp;loop=false',
     'https://docs.google.com/presentation/d/19TMewG2A5rG4Q1t2ErUFBR7-QPD-stbqkpYmHFQB6-g/view', 'Dark Patterns', 'B1 · Everyday tech'),
    ('https://docs.google.com/presentation/d/1rT1fGx0mo6QEBZBx6K6HkrbZdJz-o2TvNCwZiqhA7LI/embed?start=false&amp;loop=false',
     'https://docs.google.com/presentation/d/1rT1fGx0mo6QEBZBx6K6HkrbZdJz-o2TvNCwZiqhA7LI/view', 'Stormy weather', 'B2 · Weather and the future'),
    ('https://docs.google.com/presentation/d/1ktZh2WhCIwmI9KqfHuwIgL32U68G0_jHiQCcgT3sL8o/embed?start=false&amp;loop=false',
     'https://docs.google.com/presentation/d/1ktZh2WhCIwmI9KqfHuwIgL32U68G0_jHiQCcgT3sL8o/view', 'Your RAM Is Wasted on You', 'C1 · Tech & AI news'),
]
BOARDS = [  # image file in img/lessons, title, level and what's inside
    ('survive-the-drive-b1', 'Survive the Drive', 'B1 · Vocabulary, speaking, reading and listening'),
    ('the-necklace-b2', 'The Necklace', 'B2 · A short story: reading, listening and discussion'),
    ('the-way-we-used-to-sleep-b2', 'The way we used to sleep', 'B2 · Grammar (used to, be used to, get used to), reading and speaking'),
]
STUDENTS = [  # photo in img/students (all cropped to 4:3), caption, small line
    ('group-lesson', 'Learn together', 'A group lesson: Lost in the jungle'),
    ('interview', 'Prepare for interviews', 'Mock job interviews in English'),
    ('pets', 'Study with pets', 'Cats are always welcome at my lessons'),
    ('traveling', 'Study while traveling', 'English goes with you everywhere'),
]
FACTS = [  # big value, label
    ('5 years', 'teaching English to adults'),
    ('100+', 'tech specialists prepared for job interviews and client calls'),
    ('A0–C1', 'General, Business and IT English'),
    ('MA · TESOL', "Master's in Germanic languages, TESOL certificate (Arizona State University)"),
]
about_body = (
    '<a class="back" href="/">← Home</a>\n'
    '<section class="ab-hero"><div class="ab-text"><span class="pill pill-light">About me</span>'
    '<h1>Hi, I\'m Liliia</h1>'
    '<p class="ab-sub">I\'m an English teacher with 5 years of experience. I teach adults General, Business and IT English, '
    'from complete beginners (A0) to advanced (C1). I have worked for a British company, and in the last year alone I have helped '
    'more than 100 tech specialists get ready for job interviews and calls with clients.</p>'
    '<a class="ab-cta" href="https://t.me/Lilia_labiak">Text me on Telegram →</a></div>'
    '<figure class="ab-photo"><img src="/img/liliia.jpg" alt="Liliia Labiak, English teacher" width="720" height="900">'
    '<img class="ab-sticker" src="/img/stickers/interview.png" alt="Sticker: a job interview" loading="lazy"></figure></section>\n'
    '<div class="ab-strip">'
    + ''.join(f'<div class="ab-stat"><span class="n">{H.escape(n)}</span><span class="t">{H.escape(t)}</span></div>' for n, t in FACTS) +
    '</div>\n'
    '<section class="section"><div class="section-head"><span class="pill">Video</span><h2>A peek into my lessons</h2></div>'
    '<div class="ab-video"><video controls playsinline preload="metadata" poster="/img/lesson-promo-poster.jpg">'
    '<source src="/video/lesson-promo.mp4" type="video/mp4">Your browser can\'t play this video.</video></div></section>\n'
    '<section class="section"><div class="section-head"><span class="pill">What I teach</span><h2>My lessons</h2></div>'
    '<div class="ab-cols">'
    '<div class="ab-col c-blue"><h3>General English</h3><p>Speaking, grammar, vocabulary and reading for everyday life and travel, A0–C1.</p></div>'
    '<div class="ab-col c-butter"><h3>Business English</h3><p>Meetings, emails, presentations, negotiations and job interviews.</p></div>'
    '<div class="ab-col c-blush"><h3>IT English</h3><p>English for developers, QA and other IT specialists: stand-ups, tickets, technical interviews.</p></div>'
    '</div>'
    '<div class="ab-how">'
    '<div class="ab-how-item"><span class="i">01</span><h3>Lessons on Miro</h3><p>We work on an online whiteboard: all the materials of every lesson stay in one place, so you can always go back to them.</p></div>'
    '<div class="ab-how-item"><span class="i">02</span><h3>Made for you</h3><p>I prepare every lesson for you: your level, your goals and the topics you really need at work and in life.</p></div>'
    '<div class="ab-how-item"><span class="i">03</span><h3>Interactive homework</h3><p>Homework is on <a href="/">my own practice platform</a>: you check your answers at once and see why a mistake is a mistake.</p></div>'
    '</div></section>\n'
    '<section class="section"><div class="section-head"><span class="pill">Examples</span><h2>Lessons I made</h2></div>'
    '<p class="ab-note">Every lesson is built around a real topic: a warm-up, new vocabulary, a video or an article, grammar in context and lots of speaking. Click through the slides.</p>'
    '<div class="ab-decks">'
    + ''.join(f'<figure class="ab-deck"><div class="frame"><iframe src="{e}" '
              f'title="Lesson slides: {H.escape(t)}" loading="lazy" allowfullscreen></iframe></div>'
              f'<figcaption><span class="t">{H.escape(t)}</span><span class="k">{H.escape(k)}</span>'
              f'<a href="{o}" target="_blank" rel="noopener">Open ↗</a></figcaption></figure>'
              for e, o, t, k in SAMPLES) +
    '</div></section>\n'
    '<section class="section"><div class="section-head"><span class="pill">Inside a lesson</span><h2>Reading, grammar and speaking</h2></div>'
    '<p class="ab-note">This is what a lesson board looks like: every lesson combines new language with reading, listening and lots of speaking. Click a picture to see it in full size.</p>'
    '<div class="ab-boards">'
    + ''.join(f'<figure class="ab-board"><a href="/img/lessons/{f}.jpg" target="_blank" rel="noopener">'
              f'<img src="/img/lessons/{f}-small.jpg" alt="Lesson board: {H.escape(t)}" loading="lazy"></a>'
              f'<figcaption><span class="t">{H.escape(t)}</span><span class="k">{H.escape(k)}</span></figcaption></figure>'
              for f, t, k in BOARDS) +
    '</div></section>\n'
    '<section class="section"><div class="section-head"><span class="pill">Real lessons</span><h2>With my students</h2></div>'
    '<div class="ab-people">'
    + ''.join(f'<figure class="ab-person"><img src="/img/students/{f}.jpg" alt="{H.escape(t)}: {H.escape(k)}" loading="lazy">'
              f'<figcaption><span class="t">{H.escape(t)}</span><span class="k">{H.escape(k)}</span></figcaption></figure>'
              for f, t, k in STUDENTS) +
    '</div></section>')
open('meet-liliia.html', 'w').write(page(f'Meet Liliia · {SITE_NAME}', about_body, '<meta name="robots" content="noindex, nofollow">\n<link rel="stylesheet" href="/about.css">\n'))

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
MARK = re.compile(r'\n?<!-- site-(?:nav|header|footer|dnd) -->.*?<!-- /site-(?:nav|header|footer|dnd) -->\n?', re.S)
HEADMARK = re.compile(r'<!-- site-head -->.*?<!-- /site-head -->\n', re.S)
for folder, code, name, cls, section in LEVELS:
    for f in glob.glob(f'{folder}/*.html'):
        if f.endswith('index.html'): continue
        s = HEADMARK.sub('', MARK.sub('', open(f).read()))
        assert s.count('<body><div class="wrap">') == 1 and s.count('</head>') == 1 and s.count('</body>') == 1, f
        s = s.replace('</head>', f'<!-- site-head -->{FONTS}{ICONS}<link rel="stylesheet" href="/chrome.css">'
                                 f'<link rel="stylesheet" href="/lesson-theme.css"><!-- /site-head -->\n</head>', 1)
        s = s.replace('<body><div class="wrap">',
                      f'<body>\n<!-- site-header -->{header_html()}<!-- /site-header -->\n<div class="wrap">\n'
                      f'<!-- site-nav --><nav class="sitenav"><a href="/{folder}">← All {code} lessons</a>'
                      f'<a href="/">All levels</a></nav><!-- /site-nav -->\n', 1)
        if re.search(r'"?(?:bank|pics)"?\s*:\s*[\[{]', s):
            s = s.replace('</body>', '\n<!-- site-dnd --><script src="/dnd.js"></script><!-- /site-dnd -->\n</body>', 1)
        s = s.replace('</body>', f'\n<!-- site-footer -->{footer_html()}<!-- /site-footer -->\n</body>', 1)
        open(f, 'w').write(s)
print('ok')
