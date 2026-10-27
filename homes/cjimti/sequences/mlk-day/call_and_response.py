"""Call and Response: Freedom songs passed between the two wings. Pitch becomes position: each wing
front is a keyboard of a pentatonic scale, lowest note at its outer end, highest at the porch corner.
The Left wing sings a slow phrase, each note blooming where its pitch lies and sustaining as it fades;
then the Right wing answers with the same phrase in mirror image, so the two melodies are reflections
of each other across the porch. Every fourth phrase both wings sing together in unison and the Porch
Front, which hums quietly under everything, rises with them. The flanks (Side, Porch Left, Porch
Right) carry a faint echo of whatever was just sung. Seamless all-night loop."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, Flicker, nframes, looped

CODE = 'MK10'
TITLE = 'Call and Response'
KIND = 'ambient'
DESCRIPTION = ('The two wings sing to each other. The left sings a slow phrase, note by note, and the right '
               'answers it in mirror image; now and then they sing together and the porch joins in.')

CALL = hexc('#a0b4ff')
ANSWER = hexc('#ffa840')
UNISON = hexc('#ffd0a0')
HUM = hexc('#ff8a30')
NIGHT = hexc('#1424c0')
FLOOR_COLOR = hexc('#1424c0')
FLOOR = 0.09
LOOP = 168.0


def render(G, seed=32):
    rng = np.random.default_rng(seed)
    Lw, Rw = G.seg['Left'], G.seg['Right']
    pfr = G.seg['Porch Front']
    flank = np.concatenate([G.seg['Side'], G.seg['Porch Left'], G.seg['Porch Right']])
    # keyboard coordinate: 0 at the outer end, 1 at the porch corner
    kL = (G.pos[Lw, 0] - G.pos[Lw, 0].min()) / np.ptp(G.pos[Lw, 0])
    kR = (G.pos[Rw, 0].max() - G.pos[Rw, 0]) / np.ptp(G.pos[Rw, 0])
    lenL, lenR = np.ptp(G.pos[Lw, 0]), np.ptp(G.pos[Rw, 0])
    hum_tex = Flicker(rng, len(pfr), 0.04, 0.15)
    SCALE = np.array([0.06, 0.2, 0.33, 0.47, 0.6, 0.74, 0.88])

    def phrase():
        n = int(rng.integers(5, 8))
        p = [int(rng.integers(0, 7))]
        for _ in range(n - 1):
            p.append(int(np.clip(p[-1] + rng.choice([-2, -1, 1, 1, 2]), 0, len(SCALE) - 1)))
        durs = rng.choice([1.0, 1.0, 1.5, 2.0], n)
        durs[-1] = 2.5
        return p, durs

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        notes = []                      # (start, wing 'L'/'R', key, length)
        t, k = 2.0, 0
        while t < D:
            p, durs = phrase()
            span = durs.sum()
            if k % 4 == 3:
                for wing in 'LR':
                    s = t
                    for q, d in zip(p, durs):
                        notes.append((s, wing, SCALE[q], d, 'U'))
                        s += d
                t += span + 3.0
            else:
                for wing, off in (('L', 0.0), ('R', span + 1.2)):
                    s = t + off
                    for q, d in zip(p, durs):
                        notes.append((s, wing, SCALE[q], d, wing))
                        s += d
                t += 2 * span + 3.5
            k += 1
        echo = np.zeros(len(flank))
        for f in range(len(out)):
            t = f * DT
            fr = out[f]
            eL = np.zeros(len(Lw))
            eR = np.zeros(len(Rw))
            cL = np.zeros((len(Lw), 3))
            cR = np.zeros((len(Rw), 3))
            unison = 0.0
            energy = 0.0
            for s, wing, key, d, kind in notes:
                u = t - s
                if u < -0.5 or u > d + 3.0:
                    continue
                env = smoothstep(-0.1, 0.45, u) * np.exp(-max(0.0, u - 0.45) / (0.55 * d + 0.6))
                col = UNISON if kind == 'U' else (CALL if wing == 'L' else ANSWER)
                if kind == 'U':
                    unison = max(unison, env)
                energy += env
                if wing == 'L':
                    g = env * np.exp(-((kL - key) * lenL / 30) ** 2)
                    eL += g
                    cL += g[:, None] * col
                else:
                    g = env * np.exp(-((kR - key) * lenR / 30) ** 2)
                    eR += g
                    cR += g[:, None] * col
            for idx, e, c in ((Lw, eL, cL), (Rw, eR, cR)):
                col = c / np.maximum(e, 1e-6)[:, None]
                fr[idx] = perc(0.12 + 0.28 * np.clip(e, 0, 1.1))[:, None] * (
                    col * np.clip(e, 0, 1)[:, None] + NIGHT * (1 - np.clip(e, 0, 1))[:, None])
            hum = 0.17 + 0.03 * hum_tex(t) + 0.14 * unison
            fr[pfr] = perc(hum)[:, None] * HUM
            echo = echo * np.exp(-DT / 3.0) + DT * 0.022 * min(energy, 1.5)
            fr[flank] = perc(0.11 + np.clip(echo, 0, 0.12))[:, None] * NIGHT + \
                perc(np.clip(echo, 0, 0.12))[:, None] * HUM
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
