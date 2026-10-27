"""Mill at 3 A.M.: The night shift's machinery, as one gear train turning around the house.

Each run is a gear rim or a belt with its own tooth pitch, and they are geared to one shaft at
fixed ratios: neighbours turn opposite ways, the small pitches race, the big ones crawl. The teeth
are drawn with sub-pixel, anti-aliased edges in path distance, so every run moves smoothly even
where the pixel spacing changes, and the different pitches beat against each other at the corners.
Every fifteen seconds the press on the Porch Front takes its stroke: the whole train slows under
the load, the ram glows warm as it closes, a few sparks flick off the die, then the flywheel pulls
the train back up to speed. Work lamps hang in pools at the corners. Dim and slow; the ratios are
chosen so every rim comes back to exactly where it started at the end of the loop."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, smooth_noise, nframes, looped

CODE = 'LB08'
TITLE = 'Mill at 3 A.M.'
KIND = 'ambient'
DESCRIPTION = ('The night shift\'s machinery: every run is a gear or belt in one train, turning at its own ratio, '
               'slowing each time the press on the porch takes its stroke, then pulling back up to speed.')

STEEL = hexc('#8ea6c0')
EDGE = hexc('#d8e4f0')
SODIUM = hexc('#ff8a2a')
RAM = hexc('#ff6a14')
SPARK = hexc('#ffc870')
FLOOR_COLOR = hexc('#1c2430')
FLOOR = 0.09
LOOP = 150.0
STROKE = 15.0                     # ten strokes per loop
SPEED = 24.0                      # master pitch-line speed, 3600 units per loop


def render(G, seed=33):
    rng = np.random.default_rng(seed)

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        s = G.pd[G.path]
        pi = np.arange(G.N)
        # (path index range, tooth pitch, gear ratio, direction); ratio * 3600 / pitch is a whole number
        runs = [((0, 80), 48.0, 1.0, +1), ((81, 178), 36.0, 0.5, -1), ((179, 260), 60.0, 1.5, +1),
                ((261, 331), 40.0, 1.0, -1), ((332, 380), 45.0, 0.75, +1), ((381, 500), 24.0, 2 / 3, -1)]
        corners = np.array([(s[a] + s[a + 1]) / 2 for a in (80, 178, 260, 331, 380)])
        lamp = np.exp(-((s[None] - corners[:, None]) / 70) ** 2).sum(0)
        press = (pi >= 261) & (pi <= 331)
        mid = s[296]
        grime = smooth_noise(rng, s, 40)
        spark_seeds = rng.uniform(-1, 1, (64, 3))

        for f in range(len(out)):
            t = f * DT
            # master displacement: steady speed, held back periodically by the press stroke
            ph = 2 * np.pi * t / STROKE
            U = SPEED * t - 0.55 * SPEED * STROKE / (2 * np.pi) * np.sin(ph)
            load = 0.5 + 0.5 * np.cos(ph)                 # 1 at the bottom of the stroke
            buf = np.zeros((G.N, 3))
            for (a, b), pitch, ratio, d in runs:
                m = (pi >= a) & (pi <= b)
                x = (s[m] - s[a]) - d * ratio * U
                u = np.mod(x / pitch, 1.0)
                # a tooth: flat top with soft anti-aliased flanks, a bright leading edge
                w = 3.0 / pitch
                tooth = smoothstep(0.08, 0.08 + w, u) * smoothstep(0.55 + w, 0.55, u)
                lead = np.exp(-((u - 0.1) / (2.5 / pitch)) ** 2)
                I = 0.06 + 0.24 * tooth * (0.85 + 0.15 * grime[m])
                buf[m] += light(STEEL, I) + light(EDGE, 0.13 * lead * tooth)
            buf += light(SODIUM, 0.13 * np.clip(lamp, 0, 1))

            # the press: the ram glows as it closes, sparks off the die
            ram = smoothstep(0.75, 1.0, load)
            buf += light(RAM, 0.3 * ram * press * np.exp(-((s - mid) / 120) ** 2))
            k = int(np.floor(t / STROKE))
            u = t - k * STROKE
            if u < 1.6:
                sd = spark_seeds[k % 10]
                sp = np.zeros(G.N)
                env = smoothstep(0.0, 0.25, u) * np.exp(-u / 0.5)
                for j in range(5):
                    v = 30 + 18 * j * (1 + 0.3 * sd[j % 3])
                    for sg in (-1, 1):
                        xs = mid + sg * v * u * (1 + 0.2 * sd[(j + 1) % 3])
                        sp = np.maximum(sp, np.exp(-((s - xs) / 3.0) ** 2))
                buf += light(SPARK, 0.36 * env * sp * press)
            out[f][G.path] = buf
        return out

    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
