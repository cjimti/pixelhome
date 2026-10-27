"""Spiders: The roof glows like a lit window; spiders are silhouettes that scurry, pause, leave silk.
Then something much bigger walks across the house."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, Flicker, nframes

CODE = 'SC4'
TITLE = 'Spiders'
KIND = 'show'
DESCRIPTION = 'Silhouette spiders scurry, pause and leave silk across a glowing roof. Then something much bigger walks across.'

ORANGE = hexc('#ff3000')
RED = hexc('#ff0000')


class _Spider:
    def __init__(self, rng, pos, size, born, speed=(25, 60)):
        self.rng, self.p, self.size, self.born = rng, float(pos), size, born
        self.target, self.wait, self.speed = self.p, rng.uniform(0.3, 1.2), speed
        self.v, self.dir, self.phase, self.flee = 0.0, 1, 0.0, None

    def step(self, n):
        if self.flee is not None:
            target, v = self.flee, 90.0
        else:
            if self.wait > 0:
                self.wait -= DT
                return
            if abs(self.target - self.p) < 0.5:
                self.wait = self.rng.uniform(0.4, 2.5)
                self.target = float(np.clip(self.p + self.rng.uniform(-90, 90), 3, n - 4))
                self.v = self.rng.uniform(*self.speed)
                return
            target, v = self.target, self.v
        delta = target - self.p
        step = np.sign(delta) * min(abs(delta), v * DT)
        self.dir = 1 if step >= 0 else -1
        self.p += step
        self.phase += abs(step) / (1.5 * self.size)

    def draw(self, idx, dark, eyes):
        s = self.size
        d = idx - self.p
        dark[:] = np.maximum(dark, np.clip(1.5 - np.abs(d) / s, 0, 1))
        alt = int(self.phase) % 2
        for k in range(1, 5):
            if (k + alt) % 2 == 0:
                for sgn in (-1, 1):
                    dark[:] = np.maximum(dark, 0.85 * np.clip(1 - np.abs(d - sgn * (s + k * s)) / max(1, s * 0.6), 0, 1))
        e = self.p + self.dir * (s + 0.2)
        eyes[:] = np.maximum(eyes, np.clip(1 - np.abs(idx - e) / max(0.8, s * 0.3), 0, 1))


def render(G, seed=4):
    rng = np.random.default_rng(seed)
    D = 61.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    idx = np.arange(n, dtype=float)
    cand = Flicker(rng, n, 0.5, 3)
    silk = np.zeros(n)
    pf0 = G.pi[G.seg['Porch Front'][0]]
    crew = [_Spider(rng, pf0, 1.0, 3.0)]
    for b in (14, 17, 20, 23):
        crew.append(_Spider(rng, rng.uniform(20, n - 20), 1.0, b))
    giant = _Spider(rng, -40, 6.0, 45.0)
    giant.flee = n + 60

    for f in range(len(out)):
        t = f * DT
        bgI = keys(t, [(0, 0), (3, 0.42), (53, 0.42), (57, 0)])
        bg = light(ORANGE, bgI * (1 + 0.08 * cand(t)))
        dark = np.zeros(n)
        eyes = np.zeros(n)
        for sp in crew:
            if t < sp.born:
                continue
            if t > 35 and sp.flee is None:
                sp.flee = -20.0 if sp.p < n / 2 else n + 20.0
            sp.step(n)
            k = int(round(sp.p))
            if 0 <= k < n:
                silk[k] = max(silk[k], 1.0)
            grow = smoothstep(sp.born, sp.born + 0.5, t)
            dk, ey = np.zeros(n), np.zeros(n)
            sp.draw(idx, dk, ey)
            dark = np.maximum(dark, dk * grow)
            eyes = np.maximum(eyes, ey * grow * 0.5)
        if t >= giant.born and giant.p < n + 50:
            giant.target = n + 60
            giant.p += 52 * DT * (0.6 + 0.4 * abs(np.sin(np.pi * t * 0.9)))
            giant.phase = t * 1.8
            if 0 <= giant.p < n:
                silk[max(0, int(giant.p) - 3):int(giant.p) + 3] = 1.0
            giant.draw(idx, dark, eyes)
        silk *= 0.997
        buf = (bg + light(hexc('#d0d8ff'), 0.2 * silk)) * (1 - dark)[:, None]
        buf += light(RED, eyes * keys(t, [(0, 0.5), (55, 0.5), (55.5, 1.0)]))
        if t > 53:                                          # only the giant's eyes remain, blinking twice
            ge = np.zeros(n)
            gpos = min(giant.p, n - 3)
            for o in (-1.5, 1.5):
                ge = np.maximum(ge, np.clip(1 - np.abs(idx - (gpos + o)), 0, 1))
            blink = 0 if any(abs(t - b) < 0.1 for b in (57.5, 58.4)) else 1
            buf = buf * (1 - smoothstep(53, 55, t)) + light(RED, ge * blink * keys(t, [(53, 0), (54, 1), (60, 1), (60.5, 0)]))
        out[f][G.path] = buf
    return out
