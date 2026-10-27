"""Shells: A physically simulated Fourth of July display seen from the roofline.

Every shell is launched from a real point in space (the street in front, the yard behind), climbs as
a comet, and breaks at its own height and depth. Its stars fly out with drag and fall under gravity.
The house is lit two ways: by the burst as a point light (1/d^2 from the cloud, so near pixels glow
far more than far ones and depth reads as falloff), and directly when stars, trails or crackle
drift down through the roof itself. Each break's report travels at a (slowed) speed of sound and
rattles the roof as the wavefront passes, after a delay set by the distance.

Shell types: peony, chrysanthemum (spark trails), willow (long drooping gold), crossette (stars
split in four), crackle (stars die in a fizz of pops), ring (a flat ring at roof height racing out
around the U), palm (a few heavy comet arms), brocade crown and salutes for the finale.
"""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, nframes

CODE = 'IN01'
TITLE = 'Shells'
KIND = 'show'
DESCRIPTION = ('A real fireworks display in 3D: shells launched from the street and the yard, breaking at '
               'different heights and depths, lighting the roof by distance. Peony, willow, crossette, '
               'crackle, ring, palm, then the grand finale, every break followed by its boom.')

RED = hexc('#ff2a14')
PINK_RED = hexc('#ff3a40')
WHITE = hexc('#e8eeff')
SILVER = hexc('#c8d4ff')
BLUE = hexc('#2850ff')
GOLD = hexc('#ff8a20')
AMBER = hexc('#ff6a10')
GREEN = hexc('#40ff60')
VIOLET = hexc('#a040ff')
NIGHT = hexc('#0a1440')

G_ACC = 981.0          # gravity, units are centimetres
CS = 5200.0            # speed of sound, slowed so the report visibly lags and rolls across the house
REF = 1500.0           # reference distance for illumination
FALL = 2.5             # exponent on (REF^2/d^2): steeper than physical so depth reads from the street


def fall(d2, soft):
    x = (REF ** 2 / (d2 + soft ** 2)) ** FALL
    return x / (1 + x / 5)                     # a burst right on the roof saturates rather than explodes
ROOF_Y = 150.0


class Shell:
    def __init__(self, rng, kind, tb, c, colors, size=1.0, launch=None):
        self.kind, self.tb, self.c = kind, tb, np.asarray(c, float)
        self.colors = [np.asarray(x, float) for x in colors]
        self.size = size
        self.grav = 0.12 if kind == 'ring' else 1.0      # the ring is a flat-flying hummer star
        self.launch = np.asarray(launch if launch is not None else (c[0] * 0.8, 0.0, c[2] + 600), float)
        self.rise = 0.0 if kind == 'salute_low' else 1.1 + self.c[1] / 3200.0
        K = {'peony': 90, 'chrys': 80, 'willow': 120, 'cross': 28, 'crackle': 60, 'ring': 48, 'palm': 8,
             'brocade': 90, 'salute': 0, 'salute_low': 0}[kind]
        if kind == 'ring':
            a = np.linspace(0, 2 * np.pi, K, endpoint=False)
            tilt = rng.uniform(-0.15, 0.15)
            self.dirs = np.stack([np.cos(a), tilt * np.sin(a), np.sin(a)], 1)
            self.dirs /= np.linalg.norm(self.dirs, axis=1, keepdims=True)
        elif K:
            g = rng.normal(size=(K, 3))      # a fibonacci sphere would be too even; jitter a real one
            i = np.arange(K) + 0.5
            phi = np.arccos(1 - 2 * i / K)
            th = np.pi * (1 + 5 ** 0.5) * i
            d = np.stack([np.cos(th) * np.sin(phi), np.cos(phi), np.sin(th) * np.sin(phi)], 1)
            d += 0.12 * g
            self.dirs = d / np.linalg.norm(d, axis=1, keepdims=True)
        else:
            self.dirs = np.zeros((0, 3))
        # per type: speed, drag, burn time, trail length (s), trail samples
        spec = {'peony': (3600, 2.2, 1.7, 0.10, 2), 'chrys': (3600, 2.0, 2.0, 0.55, 7),
                'willow': (2600, 3.4, 5.0, 1.6, 10), 'cross': (3000, 1.8, 0.9, 0.25, 4),
                'crackle': (3200, 2.2, 1.3, 0.25, 3), 'ring': (750, 0.55, 3.2, 0.4, 4),
                'palm': (5200, 1.4, 2.4, 0.9, 10), 'brocade': (3000, 2.8, 4.2, 1.4, 10),
                'salute': (0, 1, 0.0, 0, 1), 'salute_low': (0, 1, 0.0, 0, 1)}[kind]
        v, self.k, self.burn, self.trail, self.M = spec
        self.v0 = v * size * rng.uniform(0.9, 1.1, len(self.dirs))
        self.cdirs = None
        self.foot = 50.0 if kind in ('willow', 'brocade') else 34.0   # how far a star's glint reaches
        if kind == 'cross':                              # each star splits into four at 0.9 s
            self.split = self.burn
            ch = []
            for d in self.dirs:
                a = np.cross(d, [0, 1, 0]) + 1e-6
                a /= np.linalg.norm(a)
                b = np.cross(d, a)
                ch += [a, -a, b, -b]
            self.cdirs = np.array(ch)
            self.cv = 1700 * size
        if kind == 'crackle':                            # a fizz of pops where each star dies
            n = len(self.dirs) * 6
            self.pop_star = rng.integers(0, len(self.dirs), n)
            self.pop_t = self.burn + rng.uniform(0.0, 0.7, n)
            self.pop_off = rng.normal(0, 70 * size, (n, 3))
        self.flash = {'salute': 5.0, 'salute_low': 4.0, 'crackle': 1.2, 'brocade': 1.4, 'ring': 0.4}.get(kind, 1.0)
        self.end = self.tb + max(self.burn + 1.2, 1.5) + (1.0 if kind == 'crackle' else 0) + 0.8
        self.start = self.tb - self.rise
        self.dist = None

    def motion(self, tau, v0, k):
        s = v0 / k * (1 - np.exp(-k * tau))
        sag = self.grav * G_ACC / k * (tau - (1 - np.exp(-k * tau)) / k)
        return s, sag

    def color(self, u):
        cs = self.colors
        if len(cs) == 1:
            return cs[0]
        x = np.clip(u, 0, 0.999) * (len(cs) - 1)
        i = int(x)
        f = np.clip((x - i - 0.4) / 0.2, 0, 1)            # colour-changing stars switch quickly
        return cs[i] * (1 - f) + cs[i + 1] * f

    def star_points(self, tau):
        """(positions (M,3), brightness (M,), colour) for stars and their trails at time tau."""
        if len(self.dirs) == 0:
            return None
        pts, wts = [], []
        k = self.k
        life = np.clip(tau / max(self.burn, 1e-3), 0, 1)
        for j in range(self.M):
            tj = tau - j * self.trail / max(self.M - 1, 1)
            if tj <= 0:
                break
            if self.kind == 'cross' and tj > self.split:
                s, sag = self.motion(self.split, self.v0, k)
                base = self.c + self.dirs * s[:, None]
                cs, csag = self.motion(tj - self.split, self.cv, 3.0)
                _, sag2 = self.motion(tj, self.v0, k)
                p = np.repeat(base, 4, 0) + self.cdirs * cs
                p[:, 1] -= sag2
                b = 1.0 - np.clip((tj - self.split - 0.7) / 0.4, 0, 1)
            else:
                s, sag = self.motion(tj, self.v0, k)
                p = self.c + self.dirs * s[:, None]
                p[:, 1] -= sag
                lt = tj / max(self.burn, 1e-3)
                b = np.clip(tj / 0.06, 0, 1) * (1 - np.clip((lt - 0.7) / 0.3, 0, 1))
                if self.kind == 'cross':
                    b = np.clip(tj / 0.06, 0, 1)
            w = (1.0 if j == 0 else 0.55 * (1 - j / self.M) ** 1.5)
            if self.kind in ('willow', 'brocade', 'chrys', 'palm') and j > 0:
                w *= 0.8                                   # trails are charcoal sparks: warmer, dimmer
            pts.append(p)
            wts.append(np.full(len(p), b * w))
        if not pts:
            return None
        return np.concatenate(pts), np.concatenate(wts), self.color(life)

    def contrib(self, t, P, rng):
        out = np.zeros((len(P), 3))
        tau = t - self.tb
        if tau < 0:                                        # the climbing comet
            u = 1 - (-tau / self.rise)
            ease = 1 - (1 - u) ** 1.6
            pos = self.launch + (self.c - self.launch) * ease
            d2 = ((P - pos) ** 2).sum(1)
            out += GOLD[None] * (0.008 * fall(d2, 250))[:, None]
            near = np.exp(-d2 / 30 ** 2)
            out += GOLD[None] * (0.9 * near)[:, None]
            return out
        # burst as a point light from the cloud
        s_mean, sag = self.motion(tau, 3300 * self.size, self.k)
        cen = self.c - np.array([0, sag, 0])
        d2 = ((P - cen) ** 2).sum(1)
        life = tau / max(self.burn, 0.3)
        flash = self.flash * np.exp(-tau / 0.07)
        sustain = (np.clip(tau / 0.1, 0, 1) * (1 - np.clip((life - 0.5) / 0.5, 0, 1)) *
                   {'willow': 0.22, 'brocade': 0.4}.get(self.kind, 1.0))
        col = self.color(life) if len(self.dirs) else WHITE
        flashcol = 0.8 * col + 0.2 * WHITE
        E = self.size ** 2 * fall(d2, 0.25 * s_mean + 150) * (0.15 if self.kind == 'ring' else 1.0)
        out += flashcol[None] * (0.3 * flash * E)[:, None]
        out += col[None] * (0.11 * sustain * E)[:, None]

        # stars and trails passing through the roof
        sp = self.star_points(tau)
        if sp is not None:
            pts, wts, scol = sp
            m = (np.abs(pts[:, 1] - ROOF_Y) < 70) & (wts > 0.01)
            if m.any():
                q, w = pts[m], wts[m]
                dd = ((P[:, None, [0, 2]] - q[None, :, [0, 2]]) ** 2).sum(-1) + (q[None, :, 1] - ROOF_Y) ** 2
                I = (w[None] * np.exp(-dd / self.foot ** 2)).sum(1)
                out += scol[None] * (1.6 * I)[:, None]
            if self.kind == 'crackle':
                tp = tau - self.pop_t
                live = (tp > 0) & (tp < 0.05)
                if live.any():
                    s, sg = self.motion(self.pop_t[live], self.v0[self.pop_star[live]], self.k)
                    q = (self.c + self.dirs[self.pop_star[live]] * s[:, None] + self.pop_off[live])
                    q[:, 1] -= sg
                    dq = ((P[:, None] - q[None]) ** 2).sum(-1)
                    out += hexc('#fff0c0')[None] * (0.01 * self.size ** 2 * fall(dq, 300)).sum(1)[:, None]
                    near = np.exp(-(((P[:, None, [0, 2]] - q[None, :, [0, 2]]) ** 2).sum(-1) +
                                    (q[None, :, 1] - ROOF_Y) ** 2) / 26 ** 2).sum(1)
                    out += hexc('#fff0c0')[None] * (1.5 * near)[:, None]

        # the report: a pressure front that rattles the roof as it passes
        if self.dist is None:
            self.dist = np.sqrt(((P - self.c) ** 2).sum(1))
        tb = tau - self.dist / CS
        loud = (1.0 + 3.0 * (self.kind.startswith('salute'))) * self.size ** 2 * (REF / self.dist.mean()) ** 2
        thump = np.where(tb > 0, np.exp(-tb / 0.09) * (0.6 + 0.4 * np.cos(2 * np.pi * 11 * tb)), 0)
        out += hexc('#ffd8b0')[None] * (0.06 * loud * thump)[:, None]
        return out


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    D = 90.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    P = G.pos.copy()
    cx = 16.0

    S = []

    def add(kind, tb, c, colors, size=1.0, launch=None):
        S.append(Shell(rng, kind, tb, c, colors, size, launch))

    # Act 1: introductions, one type at a time, each at its own place in space
    add('peony', 5.0, (-1300, 1000, 250), [RED, PINK_RED], 1.1)                        # high, front left
    add('chrys', 10.5, (500, 1100, -1500), [WHITE, SILVER], 1.1, (600, 0, -2600))        # behind the house
    add('willow', 16.0, (-150, 800, -400), [GOLD], 1.0, (-100, 0, 900))                # over the porch, drips through
    add('cross', 24.0, (750, 750, -150), [WHITE], 0.6, (900, 0, 1200))                  # low, over the right wing
    add('crackle', 29.0, (-750, 600, -650), [RED, WHITE], 0.5, (-1300, 0, -2400))       # low, by the side
    add('ring', 34.5, (cx, ROOF_Y + 25, -390), [BLUE, SILVER], 0.9, (cx, 0, 900))       # a flat ring at roof height
    add('palm', 39.5, (1000, 1200, -300), [GOLD, AMBER], 0.8, (1000, 0, 700))           # over the right wing
    # Act 2: conversations: pairs, mirror images, a sweep across, a sweep in depth
    add('peony', 45.0, (-1200, 1100, 200), [BLUE, WHITE], 1.0)
    add('peony', 45.0, (1230, 1100, 200), [RED, WHITE], 1.0)
    for i, x in enumerate(np.linspace(-1800, 1800, 6)):
        add('chrys' if i % 2 else 'peony', 48.5 + i * 0.45, (x, 1000 + 200 * (i % 2), 300),
            [[RED, WHITE, BLUE][i % 3]], 0.75)
    for i, z in enumerate((1500, 400, -700, -1800)):
        add('ring' if i == 2 else 'peony', 53.0 + i * 0.7, (cx + 200 * (-1) ** i, 1000 + 150 * i, z),
            [[WHITE], [RED], [BLUE, SILVER], [GOLD]][i][::1], 0.85)
    add('willow', 56.5, (-600, 1000, -250), [GOLD], 0.85, (-900, 0, 900))
    add('willow', 56.5, (650, 1000, -250), [GOLD], 0.85, (950, 0, 900))
    add('cross', 59.0, (cx, 900, -380), [RED, WHITE], 0.8, (cx, 0, 900))
    add('peony', 50.0, (-400, 650, -160), [RED], 0.4, (-400, 0, 900))                  # low mines that rain on a wing
    add('peony', 51.6, (430, 650, -190), [BLUE, WHITE], 0.4, (430, 0, 900))
    # Act 3: the grand finale, gathering pace
    t, rate = 62.0, 1.1
    kinds = ['peony', 'chrys', 'crackle', 'peony', 'ring', 'cross', 'palm', 'chrys', 'peony']
    pal = [[RED], [WHITE, SILVER], [BLUE, WHITE], [RED, WHITE], [GOLD], [PINK_RED, WHITE], [SILVER], [BLUE]]
    i = 0
    while t < 79.0:
        kind = kinds[i % len(kinds)]
        x = rng.uniform(-1800, 1800)
        z = rng.choice([rng.uniform(200, 1100), rng.uniform(-2200, -1100)])
        y = rng.uniform(900, 1700)
        if kind == 'ring':
            y = rng.uniform(250, 600)
            x, z = rng.uniform(-500, 500), rng.uniform(-500, -250)
        size = rng.uniform(0.55, 0.9)
        if kind in ('peony', 'chrys', 'crackle') and rng.random() < 0.35:      # low breaks right over the roof
            x, y, z, size = rng.uniform(-650, 650), rng.uniform(450, 800), rng.uniform(-600, -150), 0.42
        add(kind, t, (x, y, z), pal[i % len(pal)], size, (x * 0.9, 0, 900))
        i += 1
        t += rate * rng.uniform(0.6, 1.2)
        rate = max(0.16, rate * 0.9)
    for j, x in enumerate((-1500, 0, 1500)):                                            # brocade crown canopy
        add('brocade', 78.4 + 0.15 * j, (x, 950, -350 + 200 * (j == 1)), [GOLD], 1.25, (x, 0, 900))
    for j, tt in enumerate((82.6, 83.1, 83.6)):                                         # bang, bang, BANG
        add('salute', tt, ((-900, 900, 0)[j], 1700, 600), [WHITE], 0.9 + 0.25 * j)
    add('salute', 84.4, (cx, 1600, -400), [WHITE], 1.5)

    for f in range(F):
        t = f * DT
        fr = out[f]
        sky = keys(t, [(0, 0.0), (2.5, 0.05), (85, 0.05), (90, 0.0)])
        haze = keys(t, [(60, 0.0), (80, 0.07), (90, 0.03)])               # smoke left hanging by the finale
        fr += light(NIGHT, sky * (1 + 0.15 * np.sin(G.pd / 200 + t * 0.3))) + light(AMBER, haze)
        for sh in S:
            if sh.start <= t < sh.end:
                fr += sh.contrib(t, P, rng)
    m = out.max(axis=2, keepdims=True)                     # keep hue when a pixel overflows
    out = np.where(m > 1, out / np.maximum(m, 1e-9), out)
    return out
