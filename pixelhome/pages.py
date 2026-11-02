"""The site's pages, written as static HTML by the build so search engines and people without JavaScript get the
text, headings and links. site/app.js adds the 3D player and the library's filters on top.

URLs: / and /library/ the library (until the schedule takes /), /sets/ every set and occasion, /<playlist>/ a set
or occasion page (an occasion's id is also its own playlist's), /<playlist>/<name>/ a sequence (its id), plus a
404.html that GitHub Pages serves for any missing path. Old library links (/#<home>/<playlist>/<name>) are sent to
the sequence's page by a line of script on the library page.

A set page's text comes from the set's README.md in its sequence folder: the sections named in README_SECTIONS,
written for visitors, turned into HTML here so the repo and the site never disagree."""
import html
import json
import os
import re
import time

from . import catalog
from .occasions import BY_ID, KINDS, OCCASIONS, PLAYLIST, SETS, playlists

ORIGIN = 'https://pixelhome.app'
README_SECTIONS = ('About the work', 'The stage', 'Who is who')
NAV = [('/sets/', 'Sets'), ('/library/', 'Library'), ('/live/', 'Live'), ('/about/', 'About')]
KIND_LABEL = {'show': 'Show', 'ambient': 'All-night loop', 'intermission': 'Intermission'}
GA = """<script async src="https://www.googletagmanager.com/gtag/js?id=G-KQYBQLRBMP"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-KQYBQLRBMP');
</script>"""
FONTS = ('https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;900&family=Instrument+Sans:'
         'wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap')
WEBSITE = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Pixelhome', 'url': f'{ORIGIN}/',
           'description': "Pixel light sequences for a house roofline: Halloween, Christmas, Wagner's Ring and more, "
                          'previewed in 3D and downloadable as FSEQ for Falcon Player (FPP).',
           'license': 'https://creativecommons.org/licenses/by-sa/4.0/'}


def esc(s):
    return html.escape(str(s))


# ---------------------------------------------------------------------------- Markdown, the subset READMEs use
def _href(url):
    """A README's link on the site: another set's README becomes its page."""
    m = re.fullmatch(r'\.\./([\w-]+)/README\.md', url)
    return f'/{m.group(1)}/' if m else url


def _inline(s):
    out = []
    for part in re.split(r'(`[^`]+`)', s):
        if len(part) > 1 and part[0] == part[-1] == '`':
            code = part[1:-1]
            if re.fullmatch(r'#[0-9a-fA-F]{6}', code):          # a colour: show it
                out.append(f'<code class="hex"><i style="background:{code}"></i>{code}</code>')
            else:
                out.append(f'<code>{esc(code)}</code>')
            continue
        t = html.escape(part, quote=False)
        t = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: f'<a href="{esc(_href(m.group(2)))}">{m.group(1)}</a>', t)
        t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', t)
        out.append(t)
    return ''.join(out)


def markdown(text):
    """Headings, paragraphs, lists, tables, fenced code, and inline code, links, bold and italics."""
    lines, out, para, i = text.split('\n'), [], [], 0

    def flush():
        if para:
            out.append(f'<p>{_inline(" ".join(para))}</p>')
            para.clear()
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            flush()
        elif s.startswith('```'):
            flush()
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code.append(lines[i])
                i += 1
            out.append(f'<pre><code>{esc(chr(10).join(code))}</code></pre>')
        elif m := re.match(r'(#{1,6})\s+(.*)', s):
            flush()
            out.append(f'<h{len(m.group(1))}>{_inline(m.group(2))}</h{len(m.group(1))}>')
        elif s.startswith('|'):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            i -= 1
            body = [r for r in rows[1:] if not all(re.fullmatch(r':?-+:?', c) for c in r)]
            out.append('<div class="tablewrap"><table><thead><tr>' + ''.join(f'<th>{_inline(c)}</th>' for c in rows[0])
                       + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{_inline(c)}</td>' for c in r) + '</tr>'
                                                         for r in body) + '</tbody></table></div>')
        elif re.match(r'([-*]|\d+\.)\s', s):
            flush()
            tag = 'ol' if s[0].isdigit() else 'ul'
            items = []
            while i < len(lines) and lines[i].strip():
                t = lines[i].strip()
                if re.match(r'([-*]|\d+\.)\s', t) and not lines[i].startswith('  '):
                    items.append(re.sub(r'^([-*]|\d+\.)\s+', '', t))
                else:
                    items[-1] += ' ' + t
                i += 1
            i -= 1
            out.append(f'<{tag}>' + ''.join(f'<li>{_inline(t)}</li>' for t in items) + f'</{tag}>')
        else:
            para.append(s)
        i += 1
    flush()
    return '\n'.join(out)


def readme(home, playlist):
    """The visitor sections of a set's README as HTML ('' when it has none), and the first paragraph of its
    'About the work' as plain text for the page's description."""
    path = os.path.join(catalog.HOMES, home, 'sequences', playlist, 'README.md')
    if not os.path.exists(path):
        return '', ''
    with open(path, encoding='utf-8') as f:
        text = f.read()
    sections = re.split(r'^## ', text, flags=re.M)[1:]
    keep = [s for s in sections if s.split('\n', 1)[0].strip() in README_SECTIONS]
    lede = ''
    for s in keep:
        if s.startswith('About the work'):
            first = s.split('\n', 1)[1].strip().split('\n\n')[0]
            lede = re.sub(r'\s+', ' ', re.sub(r'[*`]|\[([^\]]+)\]\([^)]*\)', r'\1', first)).strip()
    return '\n'.join(f'<section class="prose">{markdown("## " + s)}</section>' for s in keep), lede


# ---------------------------------------------------------------------------- pieces every page shares
def fmt(seconds):
    m, s = divmod(int(round(seconds)), 60)
    return f'{m}:{s:02d}'


def runtime(seqs):
    """How long a set's shows run, with their spoken intros when those add half a minute or more."""
    shows = [s for s in seqs if s['kind'] == 'show']
    bare = sum(s['seconds'] for s in shows)
    full = bare + sum(s.get('introFrames', 0) / 40 for s in shows)
    mins = lambda x: f'{max(1, round(x / 60))} min'
    n = f'{len(shows)} show{"" if len(shows) == 1 else "s"}'
    return f'{n} · {mins(bare)}' + (f' · {mins(full)} with intros' if full - bare >= 30 else '') if shows else ''


def head(title, desc, path, ld=(), index=True):
    url = ORIGIN + path
    meta = [f'<title>{esc(title)}</title>', f'<meta name="description" content="{esc(desc)}">']
    if index:
        meta += [f'<link rel="canonical" href="{url}">',
                 '<meta property="og:type" content="website">', '<meta property="og:site_name" content="Pixelhome">',
                 f'<meta property="og:title" content="{esc(title)}">', f'<meta property="og:description" content="{esc(desc)}">',
                 f'<meta property="og:url" content="{url}">', f'<meta property="og:image" content="{ORIGIN}/og.png">',
                 '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
                 '<meta property="og:image:alt" content="A single-story house at night, its roofline lit by pixel lights">',
                 '<meta name="twitter:card" content="summary_large_image">',
                 f'<meta name="twitter:title" content="{esc(title)}">', f'<meta name="twitter:description" content="{esc(desc)}">',
                 f'<meta name="twitter:image" content="{ORIGIN}/og.png">']
    else:
        meta.append('<meta name="robots" content="noindex">')
    lds = ''.join(f'\n<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in [WEBSITE, *ld])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
{GA}
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{chr(10).join(meta)}
<meta name="theme-color" content="#0b0a09">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">{lds}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/header.css">
<link rel="stylesheet" href="/style.css">"""


def nav(current, extra=''):
    links = ''.join(f'<a{" class=live" if href == "/live/" else ""} href="{href}"'
                    f'{" aria-current=page" if href == current else ""}>{label}</a>' for href, label in NAV)
    return f'<nav class="nav" aria-label="Site">{extra}{links}</nav>'


def top(current, extra=''):
    return f"""<header class="sitehead">
  <div class="brandbox">
    <a class="brand" href="/" aria-label="Pixelhome home">
      <svg viewBox="0 0 32 32" aria-hidden="true"><use href="/favicon.svg#mark"/></svg>
      <span>Pixel<b>home</b></span>
    </a>
    <a class="by" href="https://github.com/cjimti">by cjimti</a>
  </div>
  {nav(current, extra)}
</header>"""


def built_on(stamp):
    t = time.strptime(stamp, '%Y-%m-%dT%H:%M:%SZ')
    return f'Built {time.strftime("%b", t)} {t.tm_mday}, {t.tm_year}'


def footer(built):
    return f"""<footer>
  <p>Sequences and music: <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> · Code:
    <a href="https://github.com/cjimti/pixelhome/blob/main/LICENSE">MIT</a> · <a href="/about/#license">About the license</a></p>
  <p><a href="https://github.com/cjimti/pixelhome">Source on GitHub</a> · {built_on(built)} · <span class="version"></span></p>
</footer>"""


PLAYER = """<div class="player">
      <div class="stage" id="stage">
        <canvas id="view" aria-label="3D view of the house with its roofline lights"></canvas>
        <div class="now"><span class="code" id="nowCode"></span><span class="name" id="nowName"></span></div>
        <div class="views" role="group" aria-label="Camera">
          <button data-view="street" aria-pressed="true">Street</button>
          <button data-view="corner" aria-pressed="false">Corner</button>
          <button data-view="above" aria-pressed="false">Above</button>
        </div>
        <div class="hint">Drag to orbit · scroll or pinch to zoom · ↑ ↓ to change sequence</div>
        <div class="status" id="status">Loading…</div>
      </div>
      <div class="transport">
        <button class="play" id="play" aria-label="Play">
          <svg viewBox="0 0 24 24" id="playIcon"><path d="M7 4.5v15l13-7.5z"/></svg>
        </button>
        <input type="range" id="scrub" min="0" max="1" step="0.0001" value="0" aria-label="Position in sequence">
        <div class="time" id="time"><b>0:00.0</b> / 0:00</div>
        <span class="levels"><label class="exposure" for="exposure"><span>Exposure</span> <input type="range" id="exposure" min="-2" max="8" step="0.1" value="1"><output id="expOut">1.0×</output></label>
          <label class="exposure" for="houseLight"><span>House</span> <input type="range" id="houseLight" min="0" max="4" step="0.05" value="1"><output id="houseOut">1.0×</output></label></span>
        <span class="toggles"><button class="sound" id="sound" aria-pressed="false" hidden>Sound off</button><button id="intros" aria-pressed="false" hidden>Intros off</button></span>
        <span class="dls"><a class="dl" id="download" href="#" download hidden>Download .fseq</a><a class="dl" id="downloadAudio" href="#" download hidden>.mp3</a></span>
      </div>
    </div>"""
NOW = """<p class="about"><span id="nowDesc"></span> <a class="nowlink" id="nowLink" href="#" hidden>Its page</a></p>
      <p class="spec" id="homeSpec"></p>
      <p class="spec intro" id="intro" hidden>Spoken intro, to schedule before it in FPP: <a id="introFseq" href="#" download>.fseq</a> ·
        <a id="introAudio" href="#" download>.mp3</a></p>"""
SCRIPTS = """<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js" defer></script>
<script src="/app.js" defer></script>"""


def row(m, current=False):
    k = {'ambient': 'All night', 'intermission': 'Intermission'}.get(m['kind'])
    badges = (f'<span class="k">{k}</span>' if k else '') + \
             ('<span class="k" title="Has a spoken intro">Intro</span>' if m.get('introData') else '')
    cur = ' aria-current="true"' if current else ''
    return (f'<a class="item" href="/{m["id"]}/" data-id="{m["id"]}"{cur}><span class="r1"><span class="c">{esc(m["code"])}'
            f'</span><span class="t">{esc(m["title"])}</span>{badges}<span class="dur">{fmt(m["seconds"])}</span></span>'
            f'<span class="d">{esc(m["description"])}</span></a>')


def rows(seqs, accent, current=None, label='Sequences'):
    return (f'<div class="list" style="--c:{accent}" role="list" aria-label="{esc(label)}">'
            + ''.join(row(m, m['id'] == current) for m in seqs) + '</div>')


def crumbs(trail):
    """trail: [(label, path)]; the last is this page."""
    links = ' <span aria-hidden="true">›</span> '.join(
        f'<a href="{p}">{esc(l)}</a>' if i < len(trail) - 1 else f'<span aria-current="page">{esc(l)}</span>'
        for i, (l, p) in enumerate(trail))
    ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': l, 'item': ORIGIN + p} for i, (l, p) in enumerate(trail)]}
    return f'<nav class="crumbs" aria-label="Breadcrumb">{links}</nav>', ld


def write_page(out, path, text):
    d = os.path.join(out, path.strip('/'))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'index.html') if path.endswith('/') else os.path.join(out, path.lstrip('/')), 'w') as f:
        f.write(text)


def doc_page(out, path, title, desc, accent, body, built, current='', ld=(), home=None, seq=None, player=False):
    data = f' data-home="{home}"' + (f' data-seq="{seq}"' if seq else '') if player else ''
    write_page(out, path, f"""{head(title, desc, path, ld)}
</head>
<body class="page" style="--accent:{accent}">
{top(current)}
<main class="doc wide"{data}>
{body}
{footer(built)}
</main>
{SCRIPTS if player else ''}
</body>
</html>
""")


# ---------------------------------------------------------------------------- the pages
def _trail(pl):
    """Breadcrumb trail to a playlist's page: its occasion first when it is a playlist under one."""
    p = PLAYLIST[pl]
    t = [('Sets', '/sets/')]
    if p['occasion'] != pl:
        t.append((BY_ID[p['occasion']]['label'], f"/{p['occasion']}/"))
    t.append((BY_ID[pl]['label'] if pl in BY_ID else p['label'], f'/{pl}/'))
    return t


def _thumb(m, cls='', lazy=True):
    """A sequence's thumbnail: the house lit by its most colourful frame."""
    return (f'<img class="{cls}" src="/{m["thumb"]}" width="640" height="360" alt="The house lit by {esc(m["title"])}"'
            f'{" loading=lazy" if lazy else ""} decoding="async">') if m.get('thumb') else ''


def _best(seqs):
    """The scene a set's card shows: its most colourful show."""
    shows = [m for m in seqs if m['kind'] == 'show'] or seqs
    return max(shows, key=lambda m: m.get('thumbScore', 0))


def _stills(seqs, n=5):
    """Scenes spread across a set, for the pictures beside its text: n shows evenly from first to last."""
    shows = [m for m in seqs if m['kind'] == 'show' and m.get('thumb')]
    if len(shows) <= n:
        return shows
    return [shows[round(i * (len(shows) - 1) / (n - 1))] for i in range(n)]


def _card(pl, seqs):
    p = PLAYLIST[pl]
    return (f'<a class="setcard" href="/{pl}/" style="--c:{p["accent"]}">{_thumb(_best(seqs), "cardimg")}<span class="sk">{esc(BY_ID[p["occasion"]]["label"])}'
            f'</span><b>{esc(p["label"])}</b><span>{esc(p.get("desc", ""))}</span><span class="rt">{runtime(seqs) or f"{len(seqs)} sequences"}'
            f'</span></a>')


def _library(out, path, cat, built, by_pl):
    """The library: the player beside every sequence, filtered by app.js. Its links to every set and occasion
    are in the HTML so the rest of the site can be found from here."""
    home_sel = '<select id="homeSelect" aria-label="Home" hidden></select>'
    browse = ' · '.join(f'<a href="/{pl}/">{esc(PLAYLIST[pl]["label"] if pl not in BY_ID else BY_ID[pl]["label"])}</a>'
                        for o in OCCASIONS for pl in playlists(o['id']) if pl in by_pl or (pl == o['id'] and any(
                            x in by_pl for x in playlists(o['id']))))
    title = 'Pixelhome: light sequences for a house roofline'
    desc = ("Pixel light sequences for a house roofline: Wagner's Ring, Halloween, Christmas, New Year's and more. "
            'Preview each one in 3D, download the FSEQ for FPP.')
    write_page(out, path, f"""{head(title, desc, path)}
<script>(function () {{       // old links: #live, and #<home>/<playlist>/<name> to the sequence's page
  var h = decodeURIComponent(location.hash.slice(1)), p = h.split('/');
  if (h === 'live') location.replace('/live/');
  else if (p.length === 3 && p[1] && p[2]) location.replace('/' + p[1] + '/' + p[2] + '/');
}})();</script>
</head>
<body>
<div class="app">
  {top('/library/', home_sel)}
  <main class="main" data-home="{cat['homes'][0]['id'] if cat['homes'] else ''}">
    <h1 class="vh">Pixelhome: pixel light sequences for a house roofline</h1>
    {PLAYER}
    <div class="extras">
      {NOW}
      <footer>
        <p>Every sequence is a Python script that computes each pixel, frame by frame, from the home's 3D layout.
          Downloads are FSEQ v2 (zstd) at 40 fps for <a href="https://github.com/FalconChristmas/fpp">FPP</a>, made for a
          controller at <span id="ctrlNote">80% brightness and gamma 1.0</span>. All-night loops are dim on purpose; raise
          Exposure to see them on screen.</p>
        <p class="browse">Browse: {browse}</p>
        <p>Sequences and music: <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> · Code:
          <a href="https://github.com/cjimti/pixelhome/blob/main/LICENSE">MIT</a> · <a href="/about/#license">About the license</a></p>
        <p><a href="https://github.com/cjimti/pixelhome">Source on GitHub</a> · {built_on(built)} · <span class="version"></span></p>
      </footer>
    </div>
  </main>

  <section class="library" aria-labelledby="libHead">
    <div class="filters">
      <div class="libhead">
        <h2 id="libHead">Sequences</h2>
        <span class="count" id="count"></span>
      </div>
      <input type="search" id="search" placeholder="Search sequences" aria-label="Search sequences">
      <select id="occasions" aria-label="Occasion"></select>
      <div class="seg" id="kinds" role="group" aria-label="Kind">
        <button data-kind="" aria-pressed="true">All</button>
        <button data-kind="show" aria-pressed="false">Shows</button>
        <button data-kind="ambient" aria-pressed="false">All night</button>
      </div>
    </div>
    <div class="list" id="groups"></div>
    <p class="empty" id="empty" hidden>No sequences match. Clear the search or pick another occasion.</p>
  </section>
</div>
{SCRIPTS}
</body>
</html>
""")


def _sets_index(out, built, by_pl):
    featured = ''.join(_card(pl, by_pl[pl]) for pl in SETS if pl in by_pl)
    occ = []
    for o in OCCASIONS:
        n = sum(len(by_pl.get(pl, [])) for pl in playlists(o['id']))
        if n:
            occ.append(f'<li><a href="/{o["id"]}/" style="--c:{o["accent"]}">{esc(o["label"])}</a>'
                       f'<span>{esc(o["desc"])}</span><span class="n">{n}</span></li>')
    body = f"""<section class="intro">
  <p class="kicker">Sets</p>
  <h1>Sets and occasions</h1>
  <p class="lede">Operas, oratorios and stories told scene by scene on one roofline of pixel lights, and the pieces
    written for every holiday. Each scene plays in the 3D preview with its music.</p>
</section>
<section>
  <h2>The big sets</h2>
  <div class="setcards">{featured}</div>
</section>
<section>
  <h2>Every occasion</h2>
  <ul class="occlist">{''.join(occ)}</ul>
</section>"""
    doc_page(out, '/sets/', 'Sets and occasions · Pixelhome',
             "Wagner's Ring, Mendelssohn's Elijah, the Nightmare and every holiday, told in pixel lights on a house "
             'roofline, scene by scene, with music.', '#ff6a1f', body, built, current='/sets/')


def _playlist(out, pl, home, by_pl, built):
    """A set or occasion page: what it is (from its README), its sequences in the player, and its other sets."""
    p = PLAYLIST[pl]
    seqs = by_pl.get(pl, [])
    is_occ = pl in BY_ID
    others = [x for x in playlists(pl)[1:] if x in by_pl] if is_occ else []
    label = BY_ID[pl]['label'] if is_occ else p['label']
    text, lede = readme(home, pl)
    nav_html, ld = crumbs(_trail(pl))
    kicker = 'Occasion' if is_occ and not text else BY_ID[p['occasion']]['label'] if not is_occ else 'Set'
    rt = runtime(seqs)
    parts = [nav_html, f"""<section class="intro">
  <p class="kicker">{esc(kicker)}</p>
  <h1>{esc(label)}</h1>
  <p class="lede">{esc(p.get('desc', ''))}</p>
  {f'<p class="spec">{rt}</p>' if rt else ''}
</section>"""]
    if seqs:
        heading = esc(p['label']) if others else 'The scenes' if text else 'Sequences'
        parts.append(f"""<section class="watch">
  <div class="watchplayer">{PLAYER}
    {NOW}
  </div>
  <div class="watchlist"><h2>{heading}</h2>{rows(seqs, p['accent'], label=p['label'])}</div>
</section>""")
    if others:
        parts.append(f'<section><h2>Also for {esc(label)}</h2><div class="setcards">'
                     + ''.join(_card(x, by_pl[x]) for x in others) + '</div></section>')
    if text:
        figs = ''.join(f'<a class="still" href="/{m["id"]}/">{_thumb(m)}<span><b>{esc(m["code"])}</b> {esc(m["title"])}</span></a>'
                       for m in _stills(seqs))
        parts.append(f'<div class="story"><div class="storytext">{text}</div>'
                     + (f'<aside class="stills" aria-label="Scenes">{figs}</aside>' if figs else '') + '</div>')
    shows = len([s for s in seqs if s['kind'] == 'show'])
    title = f'{label}: a light show in {shows} scene{"" if shows == 1 else "s"} · Pixelhome' if text and shows \
        else f'{label} light sequences · Pixelhome'
    desc = lede or p.get('desc', '')
    doc_page(out, f'/{pl}/', title, desc, p['accent'], '\n'.join(parts), built, ld=[ld], home=home,
             player=bool(seqs))


def _sequence(out, m, home, siblings, built):
    pl = PLAYLIST[m['playlist']]
    trail = _trail(m['playlist']) + [(m['title'], f'/{m["id"]}/')]
    nav_html, ld = crumbs(trail)
    i = next(k for k, s in enumerate(siblings) if s['id'] == m['id'])
    prev, nxt = siblings[i - 1] if i else None, siblings[i + 1] if i + 1 < len(siblings) else None
    pager = ''.join(f'<a class="{c}" href="/{s["id"]}/"><span>{w}</span>{esc(s["title"])}</a>'
                    for c, w, s in (('prev', 'Before', prev), ('next', 'After', nxt)) if s)
    dls = [f'<a class="dl" href="/{m["fseq"]}" download="{esc(m["fseqName"])}">.fseq · {m["fseqBytes"] / 1e6:.1f} MB</a>']
    if m.get('audio'):
        dls.append(f'<a class="dl" href="/{m["audio"]}" download="{esc(m["audioName"])}">.mp3</a>')
    intro = ''
    if m.get('intro'):
        intro = (f'<p>Its spoken intro, to schedule before it: <a href="/{m["intro"]}" download="{esc(m["introName"])}.fseq">.fseq</a>'
                 f' · <a href="/{m["introAudio"]}" download="{esc(m["introName"])}.mp3">.mp3</a></p>')
    set_label = BY_ID[m['playlist']]['label'] if m['playlist'] in BY_ID else pl['label']
    spec = ' · '.join(x for x in (fmt(m['seconds']), KIND_LABEL[m['kind']].lower() if m['kind'] != 'show' else '',
                                  'with a spoken intro' if m.get('intro') else '') if x)
    body = f"""{nav_html}
<section class="intro">
  <p class="kicker">{esc(m['code'])} · {esc(KIND_LABEL[m['kind']])} · <a href="/{m['playlist']}/">{esc(set_label)}</a></p>
  <h1>{esc(m['title'])}</h1>
  <p class="lede">{esc(m['description'])}</p>
  <p class="spec">{spec}</p>
</section>
<section class="watch">
  <div class="watchplayer">{PLAYER}
    {NOW}
  </div>
  <div class="watchlist"><h2><a href="/{m['playlist']}/">{esc(pl['label'])}</a></h2>{rows(siblings, pl['accent'], m['id'], pl['label'])}</div>
</section>
<section class="files">
  <h2>For your own show</h2>
  <p>{esc(KINDS[m['kind']])} The FSEQ (v2, zstd, 40 fps) plays in <a href="https://github.com/FalconChristmas/fpp">Falcon Player</a>
    on a house with the same layout; see <a href="/about/">About</a> for how it is made.</p>
  <p class="dls">{''.join(dls)}</p>
  {intro}
</section>
<nav class="pager" aria-label="Scenes">{pager}</nav>"""
    doc_page(out, f'/{m["id"]}/', f'{m["title"]}, {set_label} · Pixelhome', m['description'], pl['accent'], body,
             built, ld=[ld], home=home, seq=m['id'], player=True)


def _not_found(out, built):
    body = """<section class="intro">
  <p class="kicker">404</p>
  <h1>Nothing here</h1>
  <p class="lede">That page isn't on the house. Try the <a href="/sets/">sets</a>, the <a href="/library/">library</a>
    of every sequence, or what's <a href="/live/">playing live</a>.</p>
</section>"""
    with open(os.path.join(out, '404.html'), 'w') as f:
        f.write(f"""{head('Not found · Pixelhome', 'This page is not on pixelhome.app.', '/404.html', index=False)}
</head>
<body class="page">
{top('')}
<main class="doc">
{body}
{footer(built)}
</main>
</body>
</html>
""")


def _shared_header(out):
    """Static pages from site/ (About, Live) get the same header as the generated ones, in place of <!--sitehead-->."""
    for page, current in (('about/index.html', '/about/'), ('live/index.html', '/live/')):
        f = os.path.join(out, page)
        with open(f) as fh:
            text = fh.read()
        if '<!--sitehead-->' not in text:
            raise SystemExit(f'site/{page}: no <!--sitehead--> for the shared header')
        with open(f, 'w') as fh:
            fh.write(text.replace('<!--sitehead-->', top(current)))


def write(out, cat):
    """Every page of the site into out/, from the catalog the build just wrote. A sequence id belongs to the first
    home that has it."""
    built = cat['built']
    seen, home_of, by_pl = set(), {}, {}
    for h in cat['homes']:
        for m in h['sequences']:
            if m['id'] not in seen:
                seen.add(m['id'])
                home_of[m['playlist']] = home_of.get(m['playlist'], h['id'])
                by_pl.setdefault(m['playlist'], []).append((h['id'], m))
    by_pl = {pl: [m for _, m in v] for pl, v in by_pl.items()}
    first = cat['homes'][0]['id'] if cat['homes'] else ''
    for path in ('/', '/library/'):
        _library(out, path, cat, built, by_pl)
    _sets_index(out, built, by_pl)
    pages = {pl for pl in by_pl} | {PLAYLIST[pl]['occasion'] for pl in by_pl}
    for pl in sorted(pages):
        _playlist(out, pl, home_of.get(pl, first), by_pl, built)
    for pl, seqs in by_pl.items():
        for m in seqs:
            _sequence(out, m, home_of[pl], seqs, built)
    _not_found(out, built)
    _shared_header(out)
    return sum(len(v) for v in by_pl.values()) + len(pages) + 4
