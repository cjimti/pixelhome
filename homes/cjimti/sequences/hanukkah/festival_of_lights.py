"""Festival of Lights: the house through the late hours of a Hanukkah night. It rests in a deep blue, the Temple
glow steady on Porch Front where the candle-lighting shows kindle the hanukkiah. In long slow breaths the lights'
warmth spreads from the porch out along the wings and ebbs back, and now and then a few gold sparks drift out from
the porch along the roofline and fade, with a little white stirring in the blue. It plays on all eight nights, so it
shows no night's count of lights: only the glow.

The music is Ma'oz Tzur, the hymn the candle-lighting shows play, far off and slow: soft strings hold its F major in
long chords, and three times a loop a harp plays one of its phrases from the porch, the hymn passed round the loop a
phrase at a time."""
import os

import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, looped, nframes, smooth_noise
from pixelhome.hanukkah import OIL, TIP, WARM, Glow, reach
from pixelhome.ring import Orchestra, excerpt

CODE = 'HN09'
TITLE = 'Festival of Lights'
KIND = 'ambient'
DESCRIPTION = ('The house rests in deep blue through the late hours of a Hanukkah night, the lights\' glow steady on '
               'the porch, their warmth spreading out along the wings in long slow breaths and ebbing back.')

LOOP = 160.0
BLUE = hexc('#1e5bd8')              # the people's blue, as in Judas Maccabaeus
DEEP = hexc('#0c2a8a')              # the low blue of the candle-lighting's dusk
WHITE = hexc('#f2f6ff')
BREATHS = (8.0, 48.0, 92.0, 132.0)  # when each warm breath is fullest
BREATH = 26.0                       # seconds each breath takes to spread and ebb


def breath(t):
    """How far the warmth has spread from the porch at t (0..1), the breaths overlapping round the loop."""
    out = np.zeros_like(np.asarray(t, float))
    for c in BREATHS:
        for k in (-1, 0, 1):                                    # wrapped, so a breath across the seam is whole
            u = (np.asarray(t, float) - c - k * LOOP) / (BREATH / 2)
            out = np.maximum(out, np.where(np.abs(u) < 1, np.cos(np.pi * u / 2) ** 2, 0))
    return out


def render(G, seed=9):
    rng = np.random.default_rng(seed)
    far = reach(G)                                              # 0 at the porch, 1 at the house's free ends
    seg = G.seg_of
    porch = np.isin(seg, ['Porch Left', 'Porch Right', 'Porch Front'])
    front = seg == 'Porch Front'
    d = G.pd
    l0 = float(d[G.seg['Porch Left']].min())
    r1 = float(d[G.seg['Porch Right']].max())
    glow = Glow(G, seed)

    def draw(Dt):
        F = nframes(Dt)
        out = np.zeros((F, G.N, 3), np.float32)
        shimmer = Flicker(rng, G.N, 0.05, 0.3)
        warmth = Flicker(rng, G.N, 0.3, 1.0)
        drift = smooth_noise(rng, np.arange(F) * DT, 20.0)       # the blue's slow swell
        # gold sparks drifting out from the porch: (born, start pd, direction, speed)
        sparks, t = [], rng.uniform(2, 6)
        while t < Dt:
            side = rng.integers(0, 2)
            sparks.append((t, l0 + rng.uniform(0, 40) if side == 0 else r1 - rng.uniform(0, 40),
                           -1 if side == 0 else 1, rng.uniform(14, 24)))
            t += rng.uniform(3.5, 7.0)
        motes = sorted(rng.uniform(0, Dt, 70))
        mote_at = rng.uniform(0, 1, 70)
        for f in range(F):
            t = f * DT
            b = float(breath(t % LOOP))
            reach_now = 0.15 + 0.9 * b                           # how far out the warmth is
            warm = np.clip((reach_now - far) / 0.25, 0, 1) * (~porch) * b
            blue = (0.13 + 0.03 * drift[f]) * (0.9 + 0.1 * shimmer(t)) * (1 - 0.55 * warm)
            fr = light(DEEP, np.full(G.N, 0.1)) + light(BLUE, blue * (~front) * (1 - 0.6 * porch))
            fr += light(OIL, (0.14 + 0.1 * b) * porch * ~front * (0.9 + 0.1 * warmth(t)))
            fr += light(WARM, 0.24 * warm * (0.9 + 0.1 * warmth(t)))
            fr += glow.frame(t, 1.25)
            for tb, s0, sgn, v in sparks:
                a = t - tb
                if 0 <= a < 9:
                    env = np.sin(np.pi * a / 9) ** 1.5
                    fr += light(TIP, 0.32 * env * np.exp(-((d - (s0 + sgn * v * a)) / 5.0) ** 2) * ~front)
            for tm, w in zip(motes, mote_at):
                a = t - tm
                if 0 <= a < 6:
                    c = d.min() + w * (d.max() - d.min())
                    fr += light(WHITE, 0.18 * np.sin(np.pi * a / 6) ** 2 * np.exp(-((d - c) / 4.0) ** 2) * ~porch)
            out[f] = fr
        return out

    return np.clip(looped(draw, LOOP, floor=(0.1, DEEP)), 0, 1)


# the strings' chords round the loop: (from seconds, cello root, viola notes), all in the hymn's F major
CHORDS = [(0.0, 41, (57, 60, 65)), (20.0, 46, (58, 62, 65)), (40.0, 41, (57, 60, 65)), (60.0, 50, (57, 62, 65)),
          (80.0, 46, (58, 62, 65)), (100.0, 41, (57, 60, 64)), (120.0, 48, (55, 58, 64)), (140.0, 41, (57, 60, 65))]
PHRASES = ((26.0, 1), (78.0, 5), (118.0, 9))     # when the harp plays a phrase, and the hymn's bar it starts on


def score(M, G):
    """Soft strings in long chords under the whole loop (the mix wraps the last one round to the start); a harp, far
    off on the porch, plays a phrase of Ma'oz Tzur three times a loop."""
    o = Orchestra(M, level=6.0)
    for i, (t0, root, upper) in enumerate(CHORDS):
        t1 = CHORDS[i + 1][0] if i + 1 < len(CHORDS) else LOOP
        dd = t1 - t0 + 4.0                                       # overlapping into the next, so the change is slow
        o.play('cellos', root, t0, dd, 44, None, 0.4)
        for m in upper:
            o.play('violas', m, t0 + 0.8, dd, 40, None, 0.28)
    ex = excerpt(os.path.join(os.path.dirname(__file__), 'maoz_tzur.py'))
    bar = {int(m): t for m, t in ex['bars']}
    for t0, b0 in PHRASES:
        a, z = bar[b0], bar.get(b0 + 4, ex['seconds'])
        for t, d, m, v, *_ in ex['notes']:
            if a <= t < z:
                tt = t0 + (t - a) * 1.35                         # slower than the candle-lighting's hymn
                o.play('harp', m, tt, max(d * 1.35, 1.2), 58, 0.0, 0.5)
