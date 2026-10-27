"""Stargazing: Dad and the telescope on the front lawn, looking north over the roof. Every pixel is
a line of sight from the lawn through its real 3-D position into the sky, so the roofline is a thin
slit cut through a real star field. The sky turns about the pole (one full turn per loop): below the
pole the stars move sideways, so they glide along the wing fronts and the far porch, and they cross
the runs that recede from the street. The far porch sits lower in the sky, nearer the glow of the
horizon. The Milky Way drifts through, and Jupiter goes by, warm and steady, now and then caught in
the eyepiece's red-dot finder."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, lerp, Flicker, nframes, looped

CODE = 'FA09'
TITLE = 'Stargazing'
KIND = 'ambient'
DESCRIPTION = ('Each pixel is a line of sight from the lawn into a real star field turning about the pole: '
               'stars glide along the fronts, the Milky Way drifts through, Jupiter passes.')

NIGHT = hexc('#0a1440')
HORIZON = hexc('#283a70')
STAR = hexc('#e8eeff')
WARM = hexc('#ffe0b0')
MILKY = hexc('#8090c0')
JUPITER = hexc('#ffd8a0')
FINDER = hexc('#ff2010')
FLOOR = 0.1
LOOP = 160.0
LAT = np.radians(40)


def render(G, seed=31):
    rng = np.random.default_rng(seed)
    n = G.N
    P = G.pos[G.path]
    eye = np.array([0.0, 10.0, 260.0])                 # Dad's telescope on the front lawn
    v = P - eye
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    elev = np.arcsin(v[:, 1])
    # equatorial frame: pole up-and-north (north is behind the house, -z)
    pole = np.array([0.0, np.sin(LAT), -np.cos(LAT)])
    e1 = np.array([1.0, 0.0, 0.0])
    e2 = np.cross(pole, e1)
    dec = np.arcsin(v @ pole)                          # constant: the sky turns about the pole
    ra0 = np.arctan2(v @ e2, v @ e1)

    # the strip of sky the roof can ever see, rendered once as an image (dec x ra)
    res = 0.002
    dlo, dhi = dec.min() - 0.04, dec.max() + 0.04
    nd = int((dhi - dlo) / res) + 1
    nr = int(2 * np.pi / res)
    sky = np.zeros((nd, nr))
    warm = np.zeros((nd, nr))
    S = 6000
    sd = np.arcsin(rng.uniform(np.sin(dlo), np.sin(dhi), S))
    sr = rng.uniform(0, 2 * np.pi, S)
    mag = rng.pareto(2.2, S) * 0.08 + 0.03            # mostly faint, a few bright
    mag = np.clip(mag, 0, 0.9)
    tint = rng.uniform(0, 1, S) < 0.25
    sig = 0.0085
    w = int(3 * sig / res) + 1
    di = ((sd - dlo) / res).astype(int)
    ri = (sr / res).astype(int)
    oy, ox = np.mgrid[-w:w + 1, -w:w + 1]
    for k in range(S):
        yy = di[k] + oy
        xx = (ri[k] + ox) % nr
        ok = (yy >= 0) & (yy < nd)
        dd = ((dlo + yy * res - sd[k]) ** 2 + (np.cos(sd[k]) * (ri[k] * res + ox * res - sr[k])) ** 2)
        g = mag[k] * np.exp(-dd / sig ** 2)
        tgt = warm if tint[k] else sky
        np.add.at(tgt, (yy[ok], xx[ok]), g[ok])
    # the Milky Way: a soft lumpy band across part of the turn
    ras = np.arange(nr) * res
    lump = sum(rng.uniform(0.3, 1) * np.exp(-((np.angle(np.exp(1j * (ras - c)))) / rng.uniform(0.1, 0.25)) ** 2)
               for c in rng.normal(2.2, 0.35, 9))
    band = 0.1 * np.clip(lump, 0, 1.4) / 1.4
    jup_ra, jup_dec = 4.6, float(np.median(dec[(G.pi[G.path] >= 381)]))   # crosses the Right wing

    def sample(img, ra):
        fy = (dec - dlo) / res
        fx = (ra % (2 * np.pi)) / res
        y0 = np.clip(fy.astype(int), 0, nd - 2)
        x0 = fx.astype(int) % nr
        x1 = (x0 + 1) % nr
        ay, ax = fy - y0, fx - np.floor(fx)
        return ((img[y0, x0] * (1 - ax) + img[y0, x1] * ax) * (1 - ay) +
                (img[y0 + 1, x0] * (1 - ax) + img[y0 + 1, x1] * ax) * ay)

    horizon = np.clip(1 - (elev - elev.min()) / (elev.max() - elev.min()), 0, 1)

    def draw(D):
        out = np.zeros((nframes(D), n, 3), np.float32)
        scint = Flicker(rng, n, 0.4, 1.5)
        for f in range(len(out)):
            t = f * DT
            ra = ra0 - 2 * np.pi * t / LOOP
            stars = sample(sky, ra)
            warms = sample(warm, ra)
            mw = np.interp(ra % (2 * np.pi), ras, band)
            tw = 1 + (0.1 + 0.15 * horizon) * scint(t)    # more twinkle nearer the horizon
            dj = np.angle(np.exp(1j * (ra - jup_ra)))
            jd = (dj * np.cos(dec)) ** 2 + (dec - jup_dec) ** 2
            jup = 0.34 * np.exp(-jd / 0.011 ** 2)
            finder = 0.25 * np.exp(-((np.sqrt(jd) - 0.035) / 0.007) ** 2)   # the finder's red ring
            I_sky = 0.13 + 0.06 * horizon
            buf = light(lerp(NIGHT, HORIZON, horizon[:, None] * 0.6), I_sky)
            buf += light(MILKY, mw)
            buf += light(STAR, np.clip(stars * tw, 0, 0.3))
            buf += light(WARM, np.clip(warms * tw, 0, 0.3))
            buf += light(JUPITER, jup)
            buf += light(FINDER, finder * (0.6 + 0.4 * np.cos(2 * np.pi * t / 3)))
            out[f][G.path] = np.minimum(buf, perc(0.43))
        return out

    return looped(draw, LOOP, floor=(FLOOR, NIGHT))
