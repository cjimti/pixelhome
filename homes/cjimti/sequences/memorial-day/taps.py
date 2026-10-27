"""Taps: The 24 notes of Taps played as light. Pitch is depth: the low G sounds on the two wing fronts
nearest the street, C and E are bands that stand further back across the Side and porch runs, and the
high G rings on the far Porch Front. Each note is tongued, held with a slight vibrato and leaves a
fading after-glow, so the phrase hangs in the air of the house."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, nframes

CODE = 'MM01'
TITLE = 'Taps'
KIND = 'show'
DESCRIPTION = ('The 24 notes of Taps, played in light. Low notes sound on the wing fronts near the street, '
               'higher notes stand further back, the high G rings on the far porch.')

SILVER = hexc('#dfe7f5')
WARM = hexc('#fff0d8')
NAVY = hexc('#0b1d4a')

# pitch -> depth of the plane that sounds it (z); G3, C4, E4, G4
PLANE_Z = [-160.0, -300.0, -440.0, -569.0]
BEAT = 1.15
TUNE = [  # (pitch, beats); None = rest
    (0, .75), (0, .25), (1, 3.0), (None, 1.0),
    (0, .75), (1, .25), (2, 3.0), (None, 1.0),
    (0, .75), (1, .25), (2, 1.0), (0, .75), (1, .25), (2, 1.0), (0, .75), (1, .25), (2, 2.5), (None, 1.0),
    (1, .75), (2, .25), (3, 3.2), (None, 1.0),
    (2, .75), (1, .25), (0, 2.6), (None, 1.0),
    (0, .75), (0, .25), (1, 4.5),
]
START = 6.0


def render(G, seed=1):
    rng = np.random.default_rng(seed)
    notes, t = [], START
    for p, b in TUNE:
        d = b * BEAT
        if p is not None:
            notes.append((t, d, p))
        t += d
    end_music = t
    D = end_music + 11.0
    out = np.zeros((nframes(D), G.N, 3))
    z = G.pos[:, 2]
    # horizontal runs cover a plane completely; give the receding runs a little more width so the
    # bands read as notes rather than single pixels
    recede = np.isin(np.arange(G.N), np.concatenate([G.seg['Side'], G.seg['Porch Left'], G.seg['Porch Right']]))
    sig = np.where(recede, 58.0, 46.0)
    glow = np.zeros((4, G.N))
    phase = rng.uniform(0, 2 * np.pi, 4)

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        floor = keys(t, [(0, 0), (4, 0.11), (end_music + 3, 0.11), (D - 1, 0)])
        fr += light(NAVY, floor * np.ones(G.N))
        amp = np.zeros(4)
        for t0, d, p in notes:
            u = t - t0
            last = (t0, d, p) == notes[-1]
            relt = 2.8 if last else 0.3
            if -0.05 < u < d + relt + 0.1:
                atk = np.clip(u / 0.07, 0, 1)
                long_ = d > 1.5 * BEAT
                # long notes swell slightly then taper; short ones are crisp
                body = 1.0 if not long_ else 0.92 + 0.08 * np.sin(np.pi * min(u / d, 1))
                if p == 3 or last:
                    body *= keys(u, [(0, 1), (d * 0.6, 1), (d, 0.8)])
                rel = 1 - np.clip((u - d + 0.12) / relt, 0, 1) if u > d - 0.12 else 1.0
                amp[p] = max(amp[p], atk * body * rel * (0.78 if d > 0.5 else 0.7))
        # after-glow: each plane keeps a slow-decaying echo of what it played
        glow = np.maximum(glow * np.exp(-DT / 1.6), amp[:, None] * 0.32)
        tot = np.zeros(G.N)
        col_w = np.zeros(G.N)
        for p in range(4):
            vib = 6.0 * np.sin(2 * np.pi * 5.0 * t + phase[p]) * (amp[p] > 0.5)
            band = np.exp(-((z - PLANE_Z[p] - vib) / sig) ** 2)
            tot += band * amp[p]
            tot += band * glow[p] * (1 - amp[p])
            col_w += band * amp[p] * (p / 3)
        warmth = np.clip(col_w / np.maximum(tot, 1e-6), 0, 1)[:, None]
        col = SILVER * (1 - 0.35 * warmth) + WARM * 0.35 * warmth
        fr += perc(np.clip(tot, 0, 1))[:, None] * col
    return out
