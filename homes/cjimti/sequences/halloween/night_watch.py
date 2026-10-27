"""Night Watch: The Watcher, asleep. Half-closed red eyes drift and slowly blink; now and then they open,
look around the street, and settle back. The mouth smoulders; the rest of the house is candlelight."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, keys, lerp, nframes, looped, candle_bed

CODE = 'NT4'
TITLE = 'Night Watch'
KIND = 'ambient'
DESCRIPTION = 'The Watcher asleep. Half-closed eyes drift and blink, and three times a loop they open and look around.'

EMBER_RED = hexc('#ff0800')
DEEP_ORANGE = hexc('#ff2800')
ORANGE = hexc('#ff4a00')
FLOOR_COLOR = hexc('#ff4a08')
FLOOR = 0.13
LOOP = 300.0


def render(G, seed=14):
    rng = np.random.default_rng(seed)
    eyes = [(G.seg['Left'], G.span_u(G.seg['Left'])), (G.seg['Right'], G.span_u(G.seg['Right']))]
    M, uM = G.seg['Porch Front'], G.span_u(G.seg['Porch Front'])
    O = np.concatenate([G.seg['Side'], G.seg['Porch Left'], G.seg['Porch Right']])
    teeth = (1 - np.abs(2 * (((uM + 1) / 2 * 9) % 1) - 1)) ** 1.3

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        bed = candle_bed(rng, G.N, 0.2)
        gaze_keys, t = [(0, 0.0)], 0.0
        while t < D:
            t += rng.uniform(12, 28)
            gaze_keys += [(t, gaze_keys[-1][1]), (t + rng.uniform(3, 6), float(rng.uniform(-0.8, 0.8)))]
        blinks = np.cumsum(rng.uniform(22, 45, int(D / 20)))
        wakes = [w for w in (70.0, 165.0, 250.0) if w < D]
        for f in range(len(out)):
            t = f * DT
            fr = out[f]
            o = 0.22
            for w in wakes:
                o += keys(t, [(w, 0), (w + 5, 0.55), (w + 16, 0.55), (w + 23, 0)])
            o *= 1 - max([0.0] + [float(smoothstep(0.9, 0, abs(t - b))) for b in blinks])
            gaze = keys(t, gaze_keys)
            for w in wakes:
                if w + 5 < t < w + 16:
                    gaze = lerp(gaze, 0.7 * np.sin(2 * np.pi * (t - w - 5) / 11), smoothstep(w + 5, w + 7, t) *
                                (1 - smoothstep(w + 14, w + 16, t)))
            I = bed(t)
            fr[O] = perc(I[O])[:, None] * DEEP_ORANGE
            for idx, u in eyes:
                lid = np.clip((o - np.abs(u)) / 0.3, 0, 1)
                pupil = np.clip((np.abs(u - gaze * 0.5) - 0.05) / 0.05, 0, 1)
                e = 0.36 * lid * (0.6 + 0.4 * (1 - u ** 2)) * (0.15 + 0.85 * pupil)
                fr[idx] = perc(np.maximum(I[idx] * 0.75, e))[:, None] * lerp(DEEP_ORANGE, EMBER_RED, lid[:, None])
            m = 0.18 + 0.1 * teeth * (1 + 0.25 * np.sin(2 * np.pi * t / 9))
            fr[M] = perc(np.maximum(I[M] * 0.8, m))[:, None] * lerp(EMBER_RED, ORANGE, teeth[:, None])
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
