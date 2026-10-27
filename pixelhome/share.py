"""Share images for the site: the og:image card (the house lit by a real frame) and the touch icon."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from . import catalog

W, H = 1200, 630
FEATURE = 'halloween/wildfire'           # the sequence the card shows, if the first home has it
BG = np.array([6, 5, 4]) / 255
WALL = np.array([0x2b, 0x25, 0x21]) / 255
MOON = np.array([-0.6, 1.4, 0.8]) / np.linalg.norm([-0.6, 1.4, 0.8])
GLOWS = [(150, 0.22, 0.16), (40, 0.55, 0.14), (8, 1.0, 0.35)]   # world size, opacity, gaussian sigma / size


def _camera(pos, az=-0.62, el=0.34, dist=1.35, fov=38):
    """The site's Corner view (app.js VIEWS.corner), as a projector from layout units to card pixels."""
    x0, x1 = pos[:, 0].min(), pos[:, 0].max()
    z0, z1 = pos[:, 2].min(), pos[:, 2].max()
    span = max(x1 - x0, z1 - z0, 1)
    target = np.array([(x0 + x1) / 2, pos[:, 1].mean() - 40 * span / 1224, (z0 + z1) / 2 - 0.08 * (z1 - z0)])
    d = dist * span
    eye = target + d * np.array([np.cos(el) * np.sin(az), np.sin(el), np.cos(el) * np.cos(az)])
    fwd = (target - eye) / np.linalg.norm(target - eye)
    right = np.cross(fwd, [0, 1, 0])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    f = (H / 2) / np.tan(np.radians(fov) / 2)

    def project(p):
        v = np.atleast_2d(p) - eye
        z = v @ fwd
        return np.stack([W / 2 + f * (v @ right) / z, H / 2 - f * (v @ up) / z], 1), z, f
    return project


def _frame(home, png):
    """The most colourful, most fully lit frame of a rendered sequence, as (N,3) PWM in node order."""
    data = np.asarray(Image.open(png), float).reshape(-1, home.N, 3) / 255
    p = data ** (1 / 2.2)
    score = (p.max(axis=2) > 0.15).mean(axis=1) * ((p.max(axis=2) - p.min(axis=2)) ** 2).mean(axis=1)
    return data[int(np.argmax(score))]


def card(home, png, path):
    """1200x630 og:image: the house from the Corner view with its roofline lit by one frame."""
    project = _camera(home.pos)
    img = np.empty((H, W, 3))
    img[:] = BG
    # the house: painter's algorithm over the mesh, flat shaded by the moon like the 3D view
    mv, mt = home.mesh()
    if mt:
        v = np.array(mv).reshape(-1, 3)
        t = np.array(mt).reshape(-1, 3)
        xy, z, _ = project(v)
        n = np.cross(v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        shade = 0.25 + 0.35 * np.abs(n @ MOON)
        canvas = Image.new('RGB', (W, H))
        mask = Image.new('L', (W, H))
        draw, mdraw = ImageDraw.Draw(canvas), ImageDraw.Draw(mask)
        for k in np.argsort(-z[t].mean(axis=1)):
            poly = [tuple(xy[i]) for i in t[k]]
            draw.polygon(poly, fill=tuple((WALL * shade[k] * 255).astype(int)))
            mdraw.polygon(poly, fill=255)
        a = np.asarray(mask, float)[..., None] / 255
        img = img * (1 - a) + np.asarray(canvas, float) / 255 * a
    # the lights: additive glows sized like the site's three point sprites
    rgb = _frame(home, png)
    xy, z, f = project(home.pos)
    glow = np.zeros((H, W, 3))
    for k in np.argsort(-z):
        c = rgb[k]
        if c.max() < 1 / 255:
            continue
        for size, opacity, sig in GLOWS:
            s = max(size * f / z[k] * sig, 0.7)
            r = int(np.ceil(3 * s))
            cx, cy = int(round(xy[k, 0])), int(round(xy[k, 1]))
            ys, xs = slice(max(cy - r, 0), min(cy + r + 1, H)), slice(max(cx - r, 0), min(cx + r + 1, W))
            if ys.start >= ys.stop or xs.start >= xs.stop:
                continue
            gy, gx = np.mgrid[ys, xs]
            w = np.exp(-((gx - xy[k, 0]) ** 2 + (gy - xy[k, 1]) ** 2) / (2 * s * s)) * opacity
            glow[ys, xs] += w[..., None] * c
    img = 1 - (1 - img) * np.exp(-glow * 1.6)          # soft additive, so dense runs don't clip to flat white
    out = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
    d = ImageDraw.Draw(out)
    d.text((64, 56), 'Pixelhome', font=ImageFont.load_default(72), fill=(242, 234, 224))
    d.text((66, 140), 'Light sequences for a house roofline, previewed in 3D',
           font=ImageFont.load_default(28), fill=(168, 156, 144))
    d.text((W - 64, H - 48), 'pixelhome.app', font=ImageFont.load_default(26), fill=(255, 106, 31), anchor='rs')
    out.save(path, optimize=True)


def touch_icon(path, size=180):
    """apple-touch-icon: the favicon mark (site/favicon.svg) drawn at 4x and scaled down, without the rounded
    corners iOS adds itself."""
    s = size * 4 / 32
    im = Image.new('RGB', (size * 4, size * 4), (0x15, 0x11, 0x0e))
    d = ImageDraw.Draw(im)
    pts = [(6, 17), (11, 12.5), (16, 8), (21, 12.5), (26, 17)]
    d.line([(x * s, y * s) for x, y in (pts[0], pts[2], pts[4])], fill=(0x3a, 0x32, 0x2b), width=int(2 * s), joint='curve')
    d.rounded_rectangle([9 * s, 19 * s, 23 * s, 26 * s], radius=s, fill=(0x2b, 0x25, 0x21))
    for x, y in pts:
        d.ellipse([(x - 2) * s, (y - 2) * s, (x + 2) * s, (y + 2) * s], fill=(0xff, 0x6a, 0x1f))
    im.resize((size, size), Image.LANCZOS).save(path, optimize=True)


def write(out, homes, origin='https://pixelhome.app'):
    """og.png, apple-touch-icon.png, sitemap.xml and robots.txt into the built site."""
    if homes and homes[0]['sequences']:
        h = homes[0]
        seqs = h['sequences']
        meta = next((m for m in seqs if m['id'] == FEATURE), next((m for m in seqs if m['kind'] == 'show'), seqs[0]))
        card(catalog.load_home(h['id']), os.path.join(out, meta['data']), os.path.join(out, 'og.png'))
    touch_icon(os.path.join(out, 'apple-touch-icon.png'))
    pages = sorted(os.path.relpath(os.path.join(d, 'index.html'), out) for d, _, files in os.walk(out) if 'index.html' in files)
    urls = ''.join(f'  <url><loc>{origin}/{os.path.dirname(p) + "/" if os.path.dirname(p) else ""}</loc></url>\n' for p in pages)
    with open(os.path.join(out, 'sitemap.xml'), 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    with open(os.path.join(out, 'robots.txt'), 'w') as f:
        f.write(f'User-agent: *\nAllow: /\n\nSitemap: {origin}/sitemap.xml\n')
