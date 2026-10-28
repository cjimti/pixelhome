"""Render sequences into the static site (dist/) and local previews."""
import glob, hashlib, json, os, shutil, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from PIL import Image
from . import catalog, fseq, intro, share
from .fx import DT, to_bytes, to_bytes_dithered
from .occasions import OCCASIONS, KINDS

WEB_MAX_SECONDS = 120        # longer sequences go to the web player at half frame rate
MAX_SECONDS = 15 * 60
# Rendered output is cached by a hash of everything it depends on, so a build only renders what changed.
CACHE = os.environ.get('PIXELHOME_RENDER_CACHE', os.path.join(catalog.ROOT, 'build', 'render-cache'))


def _matches(s, want):
    return not want or any(w.lower() in f'{s.id} {s.code} {s.title}'.lower() for w in want)


def render(s):
    """Render one sequence -> float frames (F, N, 3), checked."""
    home = catalog.load_home(s.home)
    frames = np.asarray(s.load().render(home))
    if frames.ndim != 3 or frames.shape[1:] != (home.N, 3):
        raise ValueError(f'{s.path}: render returned {frames.shape}, expected (frames, {home.N}, 3)')
    if not np.isfinite(frames).all():
        raise ValueError(f'{s.path}: render returned NaN or inf')
    if not 1 <= len(frames) * DT <= MAX_SECONDS:
        raise ValueError(f'{s.path}: {len(frames) * DT:.1f}s is outside 1s..{MAX_SECONDS}s')
    return frames


def _engine_hash():
    """The code and locked dependencies every render goes through (not music, intros, share images or command line)."""
    h = hashlib.sha256()
    pkg = os.path.join(catalog.ROOT, 'pixelhome')
    for p in sorted(glob.glob(os.path.join(pkg, '*.py'))) + [os.path.join(catalog.ROOT, 'uv.lock')]:
        if os.path.basename(p) not in ('audio.py', 'intro.py', 'share.py', '__main__.py'):
            h.update(os.path.relpath(p, catalog.ROOT).encode() + b'\0' + open(p, 'rb').read())
    return h.hexdigest()


def _key(s, engine):
    h = hashlib.sha256(f'{engine}\0{s.home}\0{s.id}\0'.encode())
    h.update(open(os.path.join(catalog.HOMES, s.home, 'home.json'), 'rb').read())
    h.update(open(s.path, 'rb').read())
    return h.hexdigest()[:40]


def _render_one(s, dest):
    """Render a sequence into dest/ as seq.fseq, seq.png and meta.json."""
    t0 = time.time()
    frames = render(s)
    data = to_bytes_dithered(frames) if s.kind == 'ambient' else to_bytes(frames)
    step = int(round(DT * 1000))
    fseq.write(os.path.join(dest, 'seq.fseq'), data, step)
    every = 2 if len(data) * DT > WEB_MAX_SECONDS else 1
    web = data[::every]
    Image.fromarray(web.reshape(len(web), -1, 3), 'RGB').save(os.path.join(dest, 'seq.png'), optimize=True)
    meta = dict(id=s.id, code=s.code, title=s.title, occasion=s.occasion, kind=s.kind, description=s.description,
                seconds=round(len(data) * DT, 2), fps=round(1000 / (step * every)), frames=len(web),
                fseq=f'fseq/{s.home}/{s.id}.fseq', fseqName=f'{s.code} {s.title}.fseq',
                fseqBytes=os.path.getsize(os.path.join(dest, 'seq.fseq')),
                data=f'data/{s.home}/{s.id}.png', renderSeconds=round(time.time() - t0, 2))
    with open(os.path.join(dest, 'meta.json'), 'w') as f:
        json.dump(meta, f)


def _build_one(args):
    s, out, key = args
    cached = os.path.join(CACHE, key)
    hit = os.path.exists(os.path.join(cached, 'meta.json'))
    if not hit:
        tmp = f'{cached}.tmp{os.getpid()}'
        shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp)
        _render_one(s, tmp)
        shutil.rmtree(cached, ignore_errors=True)
        os.replace(tmp, cached)
    for sub in ('fseq', 'data'):
        os.makedirs(os.path.join(out, sub, s.home, s.occasion), exist_ok=True)
    shutil.copyfile(os.path.join(cached, 'seq.fseq'), os.path.join(out, 'fseq', s.home, s.id + '.fseq'))
    shutil.copyfile(os.path.join(cached, 'seq.png'), os.path.join(out, 'data', s.home, s.id + '.png'))
    with open(os.path.join(cached, 'meta.json')) as f:
        meta = json.load(f)
    meta['cached'] = hit
    mp3 = os.path.join(catalog.HOMES, s.home, 'audio', s.id + '.mp3')     # rendered locally by `pixelhome music`
    if os.path.exists(mp3):
        os.makedirs(os.path.join(out, 'audio', s.home, s.occasion), exist_ok=True)
        shutil.copyfile(mp3, os.path.join(out, 'audio', s.home, s.id + '.mp3'))
        meta.update(audio=f'audio/{s.home}/{s.id}.mp3', audioName=f'{s.code} {s.title}.mp3')
    mp3, js = intro.paths(s)                # spoken intro, rendered locally by `pixelhome intro`
    if os.path.exists(js):
        with open(js) as f:
            env = json.load(f)['env']
        d = os.path.join(out, 'intros', s.home, s.occasion)
        os.makedirs(d, exist_ok=True)
        data = to_bytes(intro.frames(catalog.load_home(s.home), env))
        base = os.path.join(out, 'intros', s.home, s.id)
        fseq.write(base + '.fseq', data, int(round(DT * 1000)))
        Image.fromarray(data.reshape(len(data), -1, 3), 'RGB').save(base + '.png', optimize=True)   # for the web player
        shutil.copyfile(mp3, base + '.mp3')
        meta.update(intro=f'intros/{s.home}/{s.id}.fseq', introAudio=f'intros/{s.home}/{s.id}.mp3',
                    introData=f'intros/{s.home}/{s.id}.png', introFrames=len(data), introName=f'{s.code} {s.title} intro')
    return meta


def build(out, want):
    site = os.path.join(catalog.ROOT, 'site')
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(site, out)
    homes, jobs = [], []
    engine = _engine_hash()
    for h in catalog.homes():
        home = catalog.load_home(h)
        seqs = [s for s in catalog.sequences(h) if _matches(s, want)]
        os.makedirs(os.path.join(out, 'fseq', h))
        os.makedirs(os.path.join(out, 'data', h))
        mv, mt = home.mesh()
        with open(os.path.join(out, 'data', h, 'layout.json'), 'w') as f:
            json.dump(dict(pixels=np.round(home.pos, 1).ravel().tolist(), meshVerts=mv, meshTris=mt),
                      f, separators=(',', ':'))
        homes.append(dict(id=h, name=home.name, description=home.spec.get('description', ''), pixels=home.N,
                          channels=home.channels, segments=len(home.seg), controller=home.spec.get('controller'),
                          layout=f'data/{h}/layout.json', sequences=[]))
        jobs += [(s, out, _key(s, engine)) for s in seqs]
    by_home = {h['id']: h for h in homes}
    os.makedirs(CACHE, exist_ok=True)
    hits = 0
    with ProcessPoolExecutor() as pool:
        for (s, _, _), meta in zip(jobs, pool.map(_build_one, jobs)):
            hit = meta.pop('cached')
            hits += hit
            by_home[s.home]['sequences'].append(meta)
            print(f"{s.home}/{s.id}: {meta['seconds']:.0f}s, {meta['fseqBytes'] / 1e6:.1f} MB fseq, "
                  + ('cached' if hit else f"rendered in {meta['renderSeconds']}s"))
    if not want:                     # a full build drops cache entries nothing uses any more
        keep = {k for _, _, k in jobs}
        for d in os.listdir(CACHE):
            if d not in keep:
                shutil.rmtree(os.path.join(CACHE, d), ignore_errors=True)
    used = {m['occasion'] for h in homes for m in h['sequences']}
    cat = dict(occasions=[o for o in OCCASIONS if o['id'] in used], kinds=KINDS, homes=homes,
               built=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    with open(os.path.join(out, 'data', 'catalog.json'), 'w') as f:
        json.dump(cat, f, separators=(',', ':'))
    share.write(out, homes)
    print(f'{out}: {len(jobs)} sequences across {len(homes)} home(s), {len(jobs) - hits} rendered, {hits} from cache')


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
