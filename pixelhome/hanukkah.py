"""Hanukkah: the hanukkiah on Porch Front, and the candle-lighting shows built on it. Shared by the shows in
homes/<home>/sequences/hanukkah/ (HN01..HN08, one a night) and by the Judas Maccabaeus scenes, which carry its steady
glow under them.

Porch Front, the far horizontal line in the street view, holds nine places: eight lights in two groups of four, about
38 layout units apart, and the shamash in the middle, set apart by a wider gap on each side. Each flame is about four
pixels of light with dark between. Facing the house from the street, night one's light is the rightmost place, and
each night adds one to its left; the lights are kindled left to right, newest first, by the shamash, which is lit
first.

The scenes are rendered ahead of time and play on all eight nights, so they cannot know which night it is: only a
night's own candle-lighting show shows that night's lights. Under the Judas scenes the porch carries a generic glow
(Glow), the same every night.

    H = Hanukkiah(G, seed)          H.frame(t, levels) -> (N, 3): flames at levels[0..8] (8 is the shamash)
    lit(n)                          the places lit on night n, in kindling order
    Glow(G, seed).frame(t, level)   the steady porch glow under a Judas scene
    Night(n, module_file)           a candle-lighting show: .D, .render(G, seed), .score(M, G)

The candle-lighting shows play Ma'oz Tzur, the hymn sung after the lights are kindled: its traditional melody as the
Union Hymnal (1897) prints it, transcribed into maoz_tzur.musicxml beside the shows and timed by
scripts/score_excerpt.py into maoz_tzur.score.json. The melody is played on an oboe; the strings' plain harmony under
it (CHORDS) is ours. The voiceovers leave out the Hebrew blessings: they are said over kindling a real hanukkiah.
"""
import os

import numpy as np

from .fx import DT, Flicker, hexc, light, nframes, smoothstep
from .ring import Orchestra, excerpt

OIL = hexc('#ffb33a')               # the Temple light and the hanukkiah: olive-oil gold
TIP = hexc('#fff1c0')               # flame tips
NIGHT = hexc('#0c2a8a')             # the low blue the house dims to before the lights
WARM = hexc('#ffcf8a')              # the glow the lights spread over the house

SHAMASH = 8
GAP = 57.0                          # layout units from the shamash to the nearest light
STEP = 38.0                         # between lights in a group
WIDTH = 344.0                       # Porch Front's length the places were laid out on


def lit(n):
    """The places lit on night n (1..8), in the order they are kindled: the n rightmost lights, left to right."""
    return list(range(8 - n, 8))


def places(G):
    """x of the nine places on Porch Front: lights 0..7 left to right, then the shamash (8) in the middle."""
    x = G.pos[G.seg['Porch Front'], 0]
    x0, x1 = float(x.min()), float(x.max())
    mid, k = 0.5 * (x0 + x1), (x1 - x0) / WIDTH
    off = [GAP + STEP * i for i in range(4)]
    return np.array([mid - k * o for o in off[::-1]] + [mid + k * o for o in off] + [mid])


class Hanukkiah:
    """Flames on Porch Front: frame(t, levels) for levels (9,) in 0..1, each place's flame from out to full."""

    def __init__(self, G, seed=0):
        rng = np.random.default_rng(seed)
        self.G = G
        self.x = places(G)
        pf = np.zeros(G.N, bool)
        pf[G.seg['Porch Front']] = True
        dx = G.pos[:, 0][None, :] - self.x[:, None]               # (9, N)
        self.body = np.exp(-(dx / 8.0) ** 2) * pf                   # about four pixels of flame
        self.body[SHAMASH] = np.exp(-(dx[SHAMASH] / 10.0) ** 2) * pf  # the shamash a little larger
        self.core = np.exp(-(dx / 3.0) ** 2) * pf                   # the bright middle of it
        self.flick = Flicker(rng, 9, 1.5, 6.0)
        self.slow = Flicker(rng, 9, 0.2, 0.7)

    def frame(self, t, levels):
        lv = np.asarray(levels, float)
        f = 0.85 + 0.1 * self.flick(t) + 0.05 * self.slow(t)
        a = lv * f
        tip = np.where(np.arange(9) == SHAMASH, 1.0, 0.75) * a         # the shamash a little whiter and brighter
        body = np.where(np.arange(9) == SHAMASH, 1.0, 0.9) * a
        return light(OIL, body @ self.body) + light(TIP, tip @ self.core)

    def spark(self, x, level):
        """The shamash's flame carried along Porch Front to a light: a small bright point at x."""
        pf = np.zeros(self.G.N, bool)
        pf[self.G.seg['Porch Front']] = True
        return light(TIP, level * np.exp(-((self.G.pos[:, 0] - x) / 4.0) ** 2) * pf)


class Glow:
    """The steady glow of the lights on Porch Front under the Judas scenes, the same on every night."""

    def __init__(self, G, seed=0):
        rng = np.random.default_rng(seed)
        self.pf = np.zeros(G.N)
        self.pf[G.seg['Porch Front']] = 1.0
        x = G.pos[:, 0]
        xs = places(G)
        self.shape = self.pf * (0.75 + 0.25 * np.exp(-((x - xs[SHAMASH]) / 90.0) ** 2))
        self.flick = Flicker(rng, G.N, 0.3, 1.2)

    def frame(self, t, level=1.0):
        return light(OIL, 0.22 * level * self.shape * (0.92 + 0.08 * self.flick(t)))


def reach(G):
    """How far each pixel is from the porch: 0 on Porch Front and the porch runs, 1 at the house's free ends."""
    d = G.pd
    l0 = float(d[G.seg['Porch Left']].min())
    r1 = float(d[G.seg['Porch Right']].max())
    out = np.zeros(G.N)
    out[d < l0] = (l0 - d[d < l0]) / l0
    out[d > r1] = (d[d > r1] - r1) / (d.max() - r1)
    return out


# the strings' harmony under the melody, two chords a bar (a single chord holds the bar); ours, plain and in F
CHORDS = ['F F', 'F Bb', 'F C7', 'F', 'F Bb', 'C F', 'F/C C7', 'F'] * 2 + \
         ['F F', 'Bb C', 'F', 'F', 'F C', 'Bb F', 'F F', 'C', 'F', 'F', 'C', 'C7', 'F C', 'Dm Bb', 'F/C C7', 'F']
TONES = {'F': (41, [57, 60, 65]), 'Bb': (46, [58, 62, 65]), 'C': (48, [55, 60, 64]), 'C7': (48, [55, 58, 64]),
         'F/C': (48, [57, 60, 65]), 'Dm': (50, [57, 62, 65])}

LEAD = 6.0                          # the house dims and the shamash is lit before the hymn
TAIL = 5.5                          # the lights settle after it
T_SHAMASH = 3.4
CARRY = 0.7                         # seconds the shamash's flame takes to reach a light


class Night:
    """The candle-lighting show for night n: the house dims to low blue, the shamash kindles in the middle of Porch
    Front, then lights the night's flames newest first, one on each of the hymn's phrases, its flame carried along
    the porch to each; then a warm glow spreads from the porch out along Left and Right, and the lights settle."""

    def __init__(self, n, module_file):
        self.n = n
        ex = excerpt(os.path.join(os.path.dirname(module_file), 'maoz_tzur.py'))
        self.ex = ex
        self.bar = {int(m): LEAD + t for m, t in ex['bars']}
        self.melody = [[LEAD + t, d, m, v] for t, d, m, v, *_ in ex['notes']]
        self.end = LEAD + ex['seconds']
        self.D = round(self.end + TAIL, 2)
        self.phrases = [self.bar[b] for b in range(1, 33, 4)]
        self.order = lit(n)
        self.kindle = self.phrases[:n]                                 # each light lands on a phrase
        self.last = self.kindle[-1] + 1.0

    def levels(self, t):
        """The nine flames at time t."""
        lv = np.zeros(9)
        lv[SHAMASH] = smoothstep(T_SHAMASH, T_SHAMASH + 1.2, t)
        for k, tk in zip(self.order, self.kindle):
            lv[k] = smoothstep(tk, tk + 0.9, t)
        return lv

    def render(self, G, seed=0):
        rng = np.random.default_rng(seed)
        F = nframes(self.D)
        out = np.zeros((F, G.N, 3))
        H = Hanukkiah(G, seed)
        far = reach(G)
        porch = np.isin(G.seg_of, ['Porch Left', 'Porch Right', 'Porch Front'])
        runs = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
        shimmer = Flicker(rng, G.N, 0.2, 0.8)
        flick = Flicker(rng, G.N, 0.8, 2.5)
        x = H.x
        for f in range(F):
            t = f * DT
            # the house dims from a warm evening to a low blue, then the lights' warmth comes back over it
            dusk = smoothstep(0.0, 2.6, t)
            spread = smoothstep(self.last, self.end + 1.0, t) * 1.15     # how far the glow has reached from the porch
            edge = smoothstep(spread, spread - 0.15, far) * ~porch
            done = sum(smoothstep(tk, tk + 1.5, t) for tk in self.kindle) / self.n   # of the night's lights
            fr = light(WARM, 0.3 * (1 - dusk) * np.ones(G.N))
            fr += light(NIGHT, (0.1 + 0.18 * dusk) * (0.9 + 0.1 * shimmer(t)) * (1 - 0.75 * edge)
                        * (1 - 0.7 * runs * done))
            # the porch runs warm a little with every light, and the glow spreads out over the house after the last
            fr += light(OIL, (0.05 + 0.37 * done) * dusk * runs * (0.9 + 0.1 * flick(t)))
            fr += light(OIL, 0.42 * edge * (0.9 + 0.1 * flick(t)))
            # the shamash struck: a white flash at its place before its flame grows
            a = t - T_SHAMASH
            if 0 <= a < 1.0:
                fr += H.spark(x[SHAMASH], 0.9 * np.exp(-a / 0.25))
            # its flame carried along the porch to each light, landing on the phrase
            for k, tk in zip(self.order, self.kindle):
                a = (t - (tk - CARRY)) / CARRY
                if 0 <= a < 1:
                    p = smoothstep(0, 1, a)
                    fr += H.spark(x[SHAMASH] + (x[k] - x[SHAMASH]) * p, 0.8)
                b = t - tk
                if 0 <= b < 1.2:                                       # the light catching
                    fr += H.spark(x[k], 0.7 * np.exp(-b / 0.3))
            fr += H.frame(t, self.levels(t))
            out[f] = fr
        return np.clip(out, 0, 1)

    def score(self, M, G):
        """Ma'oz Tzur on an oboe from the middle of the porch over plain strings; a harp chord for the shamash, a
        harp note as each light catches, from where it is on the porch; the last chord held under the settling."""
        o = Orchestra(M, level=3.6)
        H = places(G)
        x0, x1 = float(G.pos[:, 0].min()), float(G.pos[:, 0].max())
        pan = lambda xx: float(0.8 * (2 * (xx - x0) / (x1 - x0) - 1))
        # before the hymn: a soft F chord on the strings as the house dims, a harp spread as the shamash is lit
        for m in (41, 53, 57, 60):
            o.play('cellos' if m < 55 else 'violas', m, 0.6, LEAD - 0.6, 46, None, 0.5)
        for i, m in enumerate((53, 57, 60, 65, 69, 72)):
            o.play('harp', m, T_SHAMASH + 0.09 * i, 1.5, 70, pan(H[SHAMASH]) + 0.1 * (i - 2.5) / 2.5, 0.7)
        # the melody, and the strings under it, two chords a bar
        for t, d, m, v in self.melody:
            o.play('oboes', m, t, d * 0.97, 60 + 0.3 * v, pan(H[SHAMASH]), 0.8)
        for b, spec in enumerate(CHORDS, start=1):
            names = spec.split()
            t0, t1 = self.bar[b], self.bar.get(b + 1, self.end)
            step = (t1 - t0) / len(names)
            for i, c in enumerate(names):
                root, upper = TONES[c]
                ta, dd = t0 + i * step, step * (1.6 if b == 32 else 1.0)
                if b == 32:
                    dd = self.D - ta - 0.4                              # the last chord held under the settling
                o.play('basses', root, ta, dd, 50, None, 0.45)
                o.play('cellos', root + 12, ta, dd, 52, None, 0.45)
                for m in upper:
                    o.play('violas', m, ta, dd, 50, None, 0.32)
        # each light catching: a harp note from its place, the melody's note an octave up
        mel_t = np.array([n[0] for n in self.melody])
        for k, tk in zip(self.order, self.kindle):
            j = int(np.searchsorted(mel_t, tk + 0.01)) - 1
            m = self.melody[max(j, 0)][2] + 12
            o.play('harp', m, tk, 1.5, 80, pan(H[k]), 0.8)
            o.play('glock', m, tk, 1.0, 50, pan(H[k]), 0.12)
        # the lights settling: a last spread on the harp
        for i, m in enumerate((53, 57, 60, 65, 69, 72, 77)):
            o.play('harp', m, self.end + 0.3 + 0.12 * i, 2.5, 60, 0.6 * (i - 3) / 3, 0.55)
