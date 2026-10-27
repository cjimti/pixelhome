"""Lamplight: Late night at a great white house. Every run is a wall with tall windows set between
piers (spaced in real distance, so they are even on every run, with solid piers at the corners).
The walls hold a faint moonlit white; behind the windows, lamps come on and go out across the
evening, a fire burns low in one room, and people cross the rooms: a passing silhouette darkens a
window edge to edge, and one carries a lamp from room to room, glimpsed only through the glass.
The lantern hangs in the middle of the portico."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, Flicker, nframes, looped

CODE = 'PR08'
TITLE = 'Lamplight'
KIND = 'ambient'
DESCRIPTION = ('Late night at a great white house: moonlit walls, windows between piers, lamps coming on and '
               'going out, figures crossing the rooms and one lamp carried from window to window.')

MOON = hexc('#c8d0ff')
LAMP = hexc('#ff9030')
SHADE = hexc('#ffb868')
FIRE = hexc('#ff4a0c')
BRASS = hexc('#ffa030')
FLOOR_COLOR = hexc('#a8b4f0')
FLOOR = 0.07
LOOP = 150.0


def render(G, seed=28):
    rng = np.random.default_rng(seed)
    s = G.pd[G.path]

    # windows between piers on every run
    win = np.full(G.N, -1)
    wmask = np.zeros(G.N)
    centers = []
    for name, idx in G.path_segments():
        a, b = s[idx.min()], s[idx.max()]
        n = int((b - a - 40) // 62)
        cs = np.linspace(a + 20 + 31, b - 20 - 31, n) if n > 1 else [0.5 * (a + b)]
        for c in cs:
            k = len(centers)
            centers.append(c)
            m = smoothstep(13, 9, np.abs(s - c))
            sel = m > wmask
            win[sel] = k
            wmask = np.maximum(wmask, m)
    K = len(centers)
    centers = np.array(centers)
    s_portico = 0.5 * (s[261] + s[331])

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        # a schedule per window: levels change every 20-70 s with slow fades
        levels = np.array([0.0, 0.18, 0.27, 0.32])
        sched = []
        for k in range(K):
            pts, t = [], -10.0
            lv = rng.choice(levels, p=[0.3, 0.25, 0.3, 0.15])
            while t < D + 10:
                pts.append((t, lv))
                t += rng.uniform(20, 70)
                pts.append((t, lv))
                lv = rng.choice(levels, p=[0.3, 0.25, 0.3, 0.15])
                t += rng.uniform(3, 6)
            sched.append((np.array([p[0] for p in pts]), np.array([p[1] for p in pts])))
        kind = rng.choice(3, K, p=[0.6, 0.3, 0.1])        # lamp, curtained, fire
        kind[np.argmin(np.abs(centers - s_portico))] = 1
        wcol = np.array([LAMP, SHADE, FIRE])[kind]
        # people crossing rooms: (time, position) keyframes, slow walks with pauses
        walkers = []
        for j in range(4):
            pts, t, p = [], -20.0, rng.uniform(0, s[-1])
            while t < D + 20:
                pts.append((t, p))
                t += rng.uniform(4, 14)                    # pause
                pts.append((t, p))
                q = np.clip(p + rng.choice([-1, 1]) * rng.uniform(120, 500), 0, s[-1])
                t += abs(q - p) / rng.uniform(35, 55)
                p = q
            walkers.append((np.array([a for a, _ in pts]), np.array([b for _, b in pts])))
        moon = Flicker(rng, G.N, 0.01, 0.04)
        fire = Flicker(rng, G.N, 0.5, 2.0)
        lamp_fl = Flicker(rng, G.N, 0.1, 0.5)
        wk = np.where(win >= 0, win, 0)
        for f in range(len(out)):
            t = f * DT
            lv = np.array([np.interp(t, ts, vs) for ts, vs in sched])
            lv = lv * (1 - 0.15 * (kind == 2)) + 0.0
            I = lv[wk] * wmask
            I = I * (1 + np.where(kind[wk] == 2, 0.25 * fire(t), 0.03 * lamp_fl(t)))
            carried = np.zeros(G.N)
            for j, (ts, ps) in enumerate(walkers):
                p = np.interp(t, ts, ps)
                if j == 0:                                  # this one carries a lamp
                    carried += 0.3 * np.exp(-((s - p) / 16) ** 2)
                else:                                       # silhouettes against lit windows
                    I *= 1 - 0.75 * np.exp(-((s - p) / 7) ** 2)
            I = np.sqrt(I ** 2 + (carried * wmask) ** 2)
            col = wcol[wk] * (I > 0)[:, None]
            buf = light(MOON, 0.1 * (1 - wmask) * (0.9 + 0.1 * moon(t)) + 0.04 * wmask)
            buf += col * (np.clip(I, 0, 1) ** 2.2)[:, None]
            buf += light(LAMP, 0.06 * carried * (1 - wmask))
            buf += light(BRASS, 0.3 * np.exp(-((s - s_portico) / 6) ** 2) + 0.08 * np.exp(-((s - s_portico) / 30) ** 2))
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
