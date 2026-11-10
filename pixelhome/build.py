"""Render sequences into the static site (dist/) and local previews."""
import glob, hashlib, json, os, re, shutil, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from PIL import Image
from . import catalog, intro, pages, rendering, schedule, share
from .fx import DT
from .occasions import BY_ID, OCCASIONS, KINDS, PLAYLIST, playlists

# Rendered output is cached by the files it depends on (rendering.deps), so a build only renders what changed. A full
# build drops entries it didn't use once they've gone KEEP_DAYS without use, so switching branches keeps both caches.
CACHE = os.environ.get('PIXELHOME_RENDER_CACHE', os.path.join(catalog.ROOT, 'build', 'render-cache'))
KEEP_DAYS = 14
THUMB_VERSION = hashlib.sha256(open(os.path.join(os.path.dirname(__file__), 'share.py'), 'rb').read()).hexdigest()[:10]


def _matches(s, want):
    return not want or any(w.lower() in f'{s.id} {s.code} {s.title}'.lower() for w in want)


def render(s):
    """Render one sequence -> float frames (F, N, 3), checked."""
    return rendering.frames(s, catalog.load_home(s.home))


def _home_json(s):
    return os.path.join(catalog.HOMES, s.home, 'home.json')


def _key(s):
    return rendering.key('render', s.path, rendering.__file__, os.path.join(rendering.PKG, 'home.py'), _home_json(s))


def _intro_key(s, js):
    return rendering.key('intro', intro.__file__, s.path, js, _home_json(s))


def _cached(key, make):
    """The cache entry for key, made by make(dir) if it isn't there yet -> (its path, whether it was there)."""
    cached = os.path.join(CACHE, key)
    hit = os.path.exists(os.path.join(cached, 'meta.json'))
    if not hit:
        tmp = f'{cached}.tmp{os.getpid()}'
        shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp)
        with open(os.path.join(tmp, 'meta.json'), 'w') as f:
            json.dump(make(tmp), f)
        shutil.rmtree(cached, ignore_errors=True)
        os.replace(tmp, cached)
    os.utime(cached)                        # last used, for the pruning
    return cached, hit


def _build_one(args):
    s, out, key = args
    home = catalog.load_home(s.home)
    cached, hit = _cached(key, lambda d: rendering.write(s, home, d))
    for sub in ('fseq', 'data'):
        os.makedirs(os.path.join(out, sub, s.home, s.playlist), exist_ok=True)
    shutil.copyfile(os.path.join(cached, 'seq.fseq'), os.path.join(out, 'fseq', s.home, s.id + '.fseq'))
    shutil.copyfile(os.path.join(cached, 'seq.png'), os.path.join(out, 'data', s.home, s.id + '.png'))
    with open(os.path.join(cached, 'meta.json')) as f:
        meta = json.load(f)
    meta['cached'] = hit
    # its thumbnail and share card's picture, cached beside the render and redrawn when share.py changes
    th = os.path.join(cached, f'thumb-{THUMB_VERSION}.webp')
    base = os.path.join(cached, f'card-{THUMB_VERSION}.png')
    score = os.path.join(cached, f'thumb-{THUMB_VERSION}.json')
    if not (os.path.exists(score) and os.path.exists(base)):
        for old in glob.glob(os.path.join(cached, 'thumb-*')) + glob.glob(os.path.join(cached, 'card-*')):
            os.remove(old)
        sc = share.thumb(home, os.path.join(cached, 'seq.png'), th, base)
        with open(score, 'w') as f:
            json.dump(sc, f)
    for sub in ('thumbs', 'cards'):
        os.makedirs(os.path.join(out, sub, s.home, s.playlist), exist_ok=True)
    shutil.copyfile(th, os.path.join(out, 'thumbs', s.home, s.id + '.webp'))
    # the share card: the picture with its title and set, cached by those words and colour
    set_label = BY_ID[s.playlist]['label'] if s.playlist in BY_ID else PLAYLIST[s.playlist]['label']
    kind = {'ambient': 'All-night loop', 'intermission': 'Intermission'}.get(s.kind)
    words = (s.title, ' · '.join(x for x in (set_label, kind) if x), PLAYLIST[s.playlist]['accent'])
    card = os.path.join(cached, 'label-' + hashlib.sha256(json.dumps([THUMB_VERSION, *words]).encode()).hexdigest()[:16]
                        + '.jpg')
    if not os.path.exists(card):
        for old in glob.glob(os.path.join(cached, 'label-*')):
            os.remove(old)
        share.label(base, card, *words)
    shutil.copyfile(card, os.path.join(out, 'cards', s.home, s.id + '.jpg'))
    with open(score) as f:
        meta.update(thumb=f'thumbs/{s.home}/{s.id}.webp', thumbScore=round(json.load(f), 5),
                    card=f'cards/{s.home}/{s.id}.jpg', _base=base)
    meta.update(occasion=s.occasion, playlist=s.playlist)     # set here: cached renders predate playlists
    mp3 = os.path.join(catalog.HOMES, s.home, 'audio', s.id + '.mp3')     # rendered locally by `pixelhome music`
    if os.path.exists(mp3):
        os.makedirs(os.path.join(out, 'audio', s.home, s.playlist), exist_ok=True)
        shutil.copyfile(mp3, os.path.join(out, 'audio', s.home, s.id + '.mp3'))
        meta.update(audio=f'audio/{s.home}/{s.id}.mp3', audioName=f'{s.code} {s.title}.mp3')
    mp3, js = intro.paths(s)                # spoken intro, rendered locally by `pixelhome intro`
    meta['_keys'] = [key]
    if os.path.exists(js):
        ikey = 'intro-' + _intro_key(s, js)
        lit, _ = _cached(ikey, lambda d: dict(frames=intro.write_lights(s, home, js, d)))
        meta['_keys'].append(ikey)
        os.makedirs(os.path.join(out, 'intros', s.home, s.playlist), exist_ok=True)
        dest = os.path.join(out, 'intros', s.home, s.id)
        shutil.copyfile(os.path.join(lit, 'intro.fseq'), dest + '.fseq')
        shutil.copyfile(os.path.join(lit, 'intro.png'), dest + '.png')   # for the web player
        shutil.copyfile(mp3, dest + '.mp3')
        with open(os.path.join(lit, 'meta.json')) as f:
            frames = json.load(f)['frames']
        meta.update(intro=f'intros/{s.home}/{s.id}.fseq', introAudio=f'intros/{s.home}/{s.id}.mp3',
                    introData=f'intros/{s.home}/{s.id}.png', introFrames=frames, introName=f'{s.code} {s.title} intro')
    return meta


def _prune(used):
    """Drop cache entries this full build didn't use and nothing has used for KEEP_DAYS, and stale half-made ones."""
    now = time.time()
    for d in os.listdir(CACHE):
        p = os.path.join(CACHE, d)
        age = now - os.path.getmtime(p)
        if ('.tmp' in d and age > 86400) or (d not in used and age > KEEP_DAYS * 86400):
            shutil.rmtree(p, ignore_errors=True)


def _stamp(out):
    """Point each page at its own scripts and styles with ?v=<content hash>, so a browser never runs an old copy.
    Paths are relative to the page's folder, or to the site's root when they start with /."""
    for page in glob.glob(os.path.join(out, '**', '*.html'), recursive=True):
        base = os.path.dirname(page)

        def tag(m):
            p = m.group(2)
            f = os.path.join(out, p.lstrip('/')) if p.startswith('/') else os.path.join(base, p)
            if not os.path.isfile(f):
                return m.group(0)
            return f'{m.group(1)}="{m.group(2)}?v={hashlib.sha256(open(f, "rb").read()).hexdigest()[:10]}"'
        with open(page) as fh:
            html = fh.read()
        with open(page, 'w') as fh:
            fh.write(re.sub(r'(src|href)="([^":?#]+\.(?:js|css))"', tag, html))


def _git(*args):
    try:
        return subprocess.run(['git', *args], cwd=catalog.ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ''


def version():
    """The release this build is, from git: a tag (v1.2.0), the last tag and commits since (v1.2.0-3-gabc1234), or dev.

    Returns (label, link): a tag links to its GitHub release, anything else to its commit."""
    repo = 'https://github.com/cjimti/pixelhome'
    tag = _git('describe', '--tags', '--exact-match', '--match', 'v*', 'HEAD')
    if tag:
        return tag, f'{repo}/releases/tag/{tag}'
    sha = _git('rev-parse', 'HEAD')
    if not sha:
        return 'dev', repo
    return _git('describe', '--tags', '--match', 'v*', 'HEAD') or sha[:7], f'{repo}/commit/{sha}'


def _stamp_version(out, label, link):
    """Fill each page's <span class="version"></span> with a quiet link to the release it was built from."""
    for page in glob.glob(os.path.join(out, '**', '*.html'), recursive=True):
        with open(page) as fh:
            html = fh.read()
        if '<span class="version"></span>' in html:
            with open(page, 'w') as fh:
                fh.write(html.replace('<span class="version"></span>',
                                      f'<a class="version" href="{link}" title="The release this site was built from">{label}</a>'))


def _has_music(s):
    return os.path.exists(os.path.join(catalog.HOMES, s.home, 'audio', s.id + '.mp3'))


def build(out, want):
    site = os.path.join(catalog.ROOT, 'site')
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(site, out)
    ver, ver_link = version()
    homes, jobs, quiet = [], [], 0
    for h in catalog.homes():
        home = catalog.load_home(h)
        seqs = [s for s in catalog.sequences(h) if _matches(s, want)]
        quiet += sum(not _has_music(s) for s in seqs)
        seqs = [s for s in seqs if _has_music(s)]      # the site only carries sequences that have their soundtrack
        os.makedirs(os.path.join(out, 'fseq', h))
        os.makedirs(os.path.join(out, 'data', h))
        mv, mt = home.mesh()
        with open(os.path.join(out, 'data', h, 'layout.json'), 'w') as f:
            json.dump(dict(pixels=np.round(home.pos, 1).ravel().tolist(), meshVerts=mv, meshTris=mt),
                      f, separators=(',', ':'))
        homes.append(dict(id=h, name=home.name, description=home.spec.get('description', ''), pixels=home.N,
                          channels=home.channels, segments=len(home.seg), controller=home.spec.get('controller'),
                          layout=f'data/{h}/layout.json', sequences=[]))
        jobs += [(s, out, _key(s)) for s in seqs]
    by_home = {h['id']: h for h in homes}
    os.makedirs(CACHE, exist_ok=True)
    hits, bases, used = 0, {}, set()
    with ProcessPoolExecutor() as pool:
        for (s, _, _), meta in zip(jobs, pool.map(_build_one, jobs)):
            hit = meta.pop('cached')
            used.update(meta.pop('_keys'))
            bases[(s.home, s.id)] = meta.pop('_base')         # for the set pages' share cards
            hits += hit
            by_home[s.home]['sequences'].append(meta)
            print(f"{s.home}/{s.id}: {meta['seconds']:.0f}s, {meta['fseqBytes'] / 1e6:.1f} MB fseq, "
                  + ('cached' if hit else f"rendered in {meta['renderSeconds']}s"))
    if not want:                     # a full build drops cache entries nothing has used for a while
        _prune(used)
    used = {m['playlist'] for h in homes for m in h['sequences']}
    occasions = []
    for o in OCCASIONS:                 # each occasion with the playlists under it that have sequences
        pls = [dict(id=p, label=PLAYLIST[p]['label'], accent=PLAYLIST[p]['accent'], desc=PLAYLIST[p].get('desc', ''))
               for p in playlists(o['id']) if p in used]
        if pls:
            occasions.append(dict({k: v for k, v in o.items() if k not in ('prefix', 'desc', 'set')}, playlists=pls))
    cat = dict(occasions=occasions, kinds=KINDS, homes=homes, version=ver,
               built=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    with open(os.path.join(out, 'data', 'catalog.json'), 'w') as f:
        json.dump(cat, f, separators=(',', ':'))
    for h in homes:                     # show times for the Live page, from the home's schedule.py
        try:
            nights = schedule.nights(h['id'], h['sequences'])
        except SystemExit as e:
            if not want:
                raise
            print(f"{h['id']}: no show times in a partial build ({e})")
            continue
        if nights:
            with open(os.path.join(out, 'data', h['id'], 'schedule.json'), 'w') as f:
                json.dump(nights, f, separators=(',', ':'))
    n = pages.write(out, cat, bases)
    share.write(out, homes)       # after the pages: its sitemap lists them
    _stamp(out)
    _stamp_version(out, ver, ver_link)
    print(f'{out}: {n} pages, {len(jobs)} sequences across {len(homes)} home(s), {len(jobs) - hits} rendered, {hits} from cache, '
          f'{quiet} left out until they have music')


# ---------------------------------------------------------------------------
W, H = 960, 440


def _splat(home):
    """Top-down splat of every pixel into a W x H image, fitted to the layout."""
    x, z = home.pos[:, 0], home.pos[:, 2]
    pad = 30
    scale = min((W - 2 * pad) / np.ptp(x), (H - 2 * pad) / np.ptp(z))
    sx = W / 2 + (x - (x.max() + x.min()) / 2) * scale
    sy = H / 2 + (z - (z.max() + z.min()) / 2) * scale
    r = 14
    oy, ox = np.mgrid[-r:r + 1, -r:r + 1]
    idx, wts, node = [], [], []
    for k in range(home.N):
        cx, cy = int(round(sx[k])), int(round(sy[k]))
        d2 = (ox + (cx - sx[k])) ** 2 + (oy + (cy - sy[k])) ** 2
        w = np.exp(-d2 / (2 * 1.6 ** 2)) + 0.18 * np.exp(-d2 / (2 * 6 ** 2))
        px, py = (ox + cx).ravel(), (oy + cy).ravel()
        ok = (px >= 0) & (px < W) & (py >= 0) & (py < H)
        idx.append((py * W + px)[ok]); wts.append(w.ravel()[ok]); node.append(np.full(ok.sum(), k))
    return np.concatenate(idx), np.concatenate(wts), np.concatenate(node)


def stills(home, frames, path, gain, n=12):
    """n evenly spaced frames of the top-down splat in a grid, each labelled with its time.
    Top-down: x across, the street at the bottom; the porch is the notch set back in the middle."""
    from PIL import ImageDraw
    idx, wts, node = _splat(home)
    outline = np.zeros(H * W)
    np.add.at(outline, idx, wts * 0.01)
    cols, sw, sh = 3, W // 2, H // 2
    sheet = Image.new('RGB', (cols * sw, -(-n // cols) * sh))
    for j, f in enumerate(np.linspace(0, len(frames) - 1, n).astype(int)):
        img = np.empty((H * W, 3))
        for c in range(3):
            img[:, c] = gain * np.bincount(idx, weights=wts * frames[f][node, c], minlength=H * W) + outline
        tile = Image.fromarray((np.clip(img, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8).reshape(H, W, 3)).resize((sw, sh))
        ImageDraw.Draw(tile).text((8, 6), f'{f * DT:.1f}s', fill=(160, 150, 140))
        sheet.paste(tile, ((j % cols) * sw, (j // cols) * sh))
    sheet.save(path)


def preview(want, out, occasion=None, video=False):
    """Per matching sequence: timeline PNG (time down at 10 rows/s, roofline path across), stills PNG,
    optional MP4, and a line of numbers."""
    os.makedirs(out, exist_ok=True)
    for h in catalog.homes():
        home = catalog.load_home(h)
        for s in catalog.sequences(h, occasion):
            if not _matches(s, want):
                continue
            frames = render(s)
            gain = 5 if s.kind == 'ambient' else 1
            name = os.path.join(out, f'{h} {s.code} {s.title}')
            rows = np.clip(frames[::4][:, home.path] * gain, 0, 1) ** (1 / 2.2)     # 10 rows/s, path order
            img = (rows * 255).astype(np.uint8)
            Image.fromarray(img).resize((img.shape[1] * 2, img.shape[0] * 2), Image.NEAREST).save(name + ' timeline.png')
            stills(home, frames, name + ' stills.png', gain)
            if video:
                idx, wts, node = _splat(home)
                outline = np.zeros(H * W)
                np.add.at(outline, idx, wts * 0.01)
                every = 2
                ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                                       '-s', f'{W}x{H}', '-r', str(int(round(1 / DT / every))), '-i', '-',
                                       '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', name + ' preview.mp4'],
                                      stdin=subprocess.PIPE)
                for fr in frames[::every]:
                    img = np.empty((H * W, 3))
                    for c in range(3):
                        img[:, c] = gain * np.bincount(idx, weights=wts * fr[node, c], minlength=H * W) + outline
                    ff.stdin.write((np.clip(img, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8).tobytes())
                ff.stdin.close()
                ff.wait()
            p = np.clip(frames, 0, 1) ** (1 / 2.2)
            step = np.abs(np.diff(np.concatenate([p, p[:1]]), axis=0))
            lit = (p.max(axis=2) > 0.02).mean()
            print(f'{name}: {len(frames) * DT:.0f}s  peak {p.max():.2f}  mean {p.mean():.3f}  lit {lit:.0%}  '
                  f'max pixel step {step.max():.3f}  max whole-house step {step.mean(axis=(1, 2)).max():.4f}  '
                  f'loop seam {np.abs(p[0] - p[-1]).max():.3f}')
