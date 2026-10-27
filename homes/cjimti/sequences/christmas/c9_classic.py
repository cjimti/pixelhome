"""C9 Classic: An old-fashioned string of big C9 bulbs, one every twelve-odd units, set on every
second or third pixel (by each run's spacing) so the string reads as glass bulbs with dark gaps.
Each bulb is a tungsten filament behind painted glass: its own temperature and wear, colour from blackbody light through the glass filter, brightness rising with
roughly the fourth power of temperature. Now and then the furnace kicks on and the whole string sags
warmer and dimmer with filament lag; the odd loose bulb wavers. Seamless for all night."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, lerp, Flicker, nframes, looped

CODE = 'XM09'
TITLE = 'C9 Classic'
KIND = 'ambient'
DESCRIPTION = ('A string of old-fashioned C9 bulbs: warm filaments behind red, green, blue, orange and '
               'yellow glass, each bulb slightly different, the string sagging when the furnace kicks on.')

# painted glass transmission
GLASS = [np.array(c) for c in ((1.0, 0.07, 0.03), (0.12, 0.85, 0.16), (0.14, 0.3, 1.0),
                                (1.0, 0.42, 0.04), (1.0, 0.86, 0.45))]
GLASS_GAIN = np.array([1.0, 1.05, 1.45, 0.95, 0.8])  # blue glass passes little of a warm filament
FLOOR = 0.05
FLOOR_COLOR = hexc('#ff6a18')
LOOP = 150.0


def blackbody(T):
    """Approximate normalised RGB of a filament at T kelvin (2000..3200)."""
    T = np.asarray(T, float)
    g = np.interp(T, [2000, 2400, 2700, 3000, 3200], [0.45, 0.58, 0.67, 0.74, 0.78])
    b = np.interp(T, [2000, 2400, 2700, 3000, 3200], [0.1, 0.24, 0.36, 0.48, 0.55])
    return np.stack([np.ones_like(T), g, b], -1)


def render(G, seed=29):
    rng = np.random.default_rng(seed)
    n = G.N
    x = G.pd[G.path]
    # one bulb every 3rd pixel on the close-spaced runs, every 2nd on Side and Porch Right, so every
    # bulb sits on a pixel (no beating against the pixel pitch) at roughly 12-15 units
    bp = []
    for name, pidx in G.path_segments():
        pidx = np.sort(pidx)
        step = 2 if np.diff(x[pidx]).mean() > 5.5 else 3
        bp.extend(pidx[step // 2::step])
    bp = np.array(bp)
    bx = x[bp]
    nb = len(bx)
    kind = np.arange(nb) % 5
    filt = np.array([GLASS[k] * GLASS_GAIN[k] for k in kind])
    T0 = rng.normal(2650, 70, nb)                    # each filament runs at its own temperature
    wear = rng.uniform(0.85, 1.05, nb)               # blackened glass, thinner filament
    core = np.zeros((n, nb))
    core[bp, np.arange(nb)] = 1.0
    halo = np.zeros((n, nb))
    for o, w in ((-1, 0.14), (1, 0.14)):
        q = np.clip(bp + o, 0, n - 1)
        same = np.abs(x[q] - bx) < 9
        halo[q[same], np.arange(nb)[same]] += w

    def draw(D):
        F = nframes(D)
        out = np.zeros((F, n, 3), np.float32)
        hum = Flicker(rng, nb, 0.03, 0.12)
        # furnace sags: (start, length); a loose bulb or two: (bulb, start, length)
        sags, t = [], rng.uniform(15, 30)
        while t < D:
            sags.append((t, rng.uniform(5, 9)))
            t += rng.uniform(40, 65)
        loose = [(int(rng.integers(nb)), rng.uniform(0, D - 10), rng.uniform(5, 9)) for _ in range(int(D / 30))]
        wob = Flicker(rng, 1, 0.8, 1.6)
        Tf = T0.copy()                               # filament temperature with thermal lag
        for f in range(F):
            t = f * DT
            volt = 1.0
            for ts, dur in sags:
                volt -= 0.06 * smoothstep(ts, ts + 0.8, t) * (1 - smoothstep(ts + dur, ts + dur + 1.5, t))
            target = T0 * volt ** 0.42 * (1 + 0.004 * hum(t))
            for b, ts, dur in loose:
                if ts < t < ts + dur:
                    env = np.sin(np.pi * (t - ts) / dur) ** 2
                    target[b] *= 1 - 0.07 * env * (0.5 + 0.5 * wob(t)[0])
            Tf += (target - Tf) * (1 - np.exp(-DT / 0.12))
            lum = 0.32 * wear * (Tf / 2650) ** 4
            col = blackbody(Tf) * filt
            I = perc(lum)[:, None] * col
            buf = core @ I + halo @ I * 0.35
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
