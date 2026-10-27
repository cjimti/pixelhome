"""Render sequences into the static site (dist/) and local previews."""
import json, os, shutil, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from PIL import Image
from . import catalog, fseq
from .fx import DT, to_bytes, to_bytes_dithered
from .occasions import OCCASIONS, KINDS

WEB_MAX_SECONDS = 120        # longer sequences go to the web player at half frame rate
MAX_SECONDS = 15 * 60


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


def _build_one(args):
    s, out = args
    t0 = time.time()
    frames = render(s)
    data = to_bytes_dithered(frames) if s.kind == 'ambient' else to_bytes(frames)
    step = int(round(DT * 1000))
    fseq.write(os.path.join(out, 'fseq', s.home, s.id + '.fseq'), data, step)
    every = 2 if len(data) * DT > WEB_MAX_SECONDS else 1
    web = data[::every]
    Image.fromarray(web.reshape(len(web), -1, 3), 'RGB').save(
        os.path.join(out, 'data', s.home, s.id + '.png'), optimize=True)
    return dict(id=s.id, code=s.code, title=s.title, occasion=s.occasion, kind=s.kind, description=s.description,
                seconds=round(len(data) * DT, 2), fps=round(1000 / (step * every)), frames=len(web),
                fseq=f'fseq/{s.home}/{s.id}.fseq', fseqName=f'{s.code} {s.title}.fseq',
                fseqBytes=os.path.getsize(os.path.join(out, 'fseq', s.home, s.id + '.fseq')),
                data=f'data/{s.home}/{s.id}.png', renderSeconds=round(time.time() - t0, 2))


def build(out, want):
    site = os.path.join(catalog.ROOT, 'site')
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(site, out)
    homes, jobs = [], []
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
        jobs += [(s, out) for s in seqs]
    by_home = {h['id']: h for h in homes}
    with ProcessPoolExecutor() as pool:
        for (s, _), meta in zip(jobs, pool.map(_build_one, jobs)):
            by_home[s.home]['sequences'].append(meta)
            print(f"{s.home}/{s.id}: {meta['seconds']:.0f}s, {meta['fseqBytes'] / 1e6:.1f} MB fseq, "
                  f"rendered in {meta['renderSeconds']}s")
    used = {m['occasion'] for h in homes for m in h['sequences']}
    cat = dict(occasions=[o for o in OCCASIONS if o['id'] in used], kinds=KINDS, homes=homes,
               built=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    with open(os.path.join(out, 'data', 'catalog.json'), 'w') as f:
        json.dump(cat, f, separators=(',', ':'))
    print(f'{out}: {len(jobs)} sequences across {len(homes)} home(s)')


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


def preview(want, out):
    os.makedirs(out, exist_ok=True)
    for h in catalog.homes():
        home = catalog.load_home(h)
        for s in catalog.sequences(h):
            if not _matches(s, want):
                continue
            frames = render(s)
            gain = 5 if s.kind == 'ambient' else 1
            name = os.path.join(out, f'{h} {s.code} {s.title}')
            rows = np.clip(frames[::4][:, home.path] * gain, 0, 1) ** (1 / 2.2)     # 10 rows/s, path order
            img = (rows * 255).astype(np.uint8)
            Image.fromarray(img).resize((img.shape[1] * 2, img.shape[0] * 2), Image.NEAREST).save(name + ' timeline.png')
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
            print(f'{name}: {len(frames) * DT:.0f}s  peak {p.max():.2f}  max pixel step {step.max():.3f}  '
                  f'max whole-house step {step.mean(axis=(1, 2)).max():.4f}')
