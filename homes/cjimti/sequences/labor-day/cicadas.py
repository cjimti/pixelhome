"""Cicadas: The late-summer drone, as an excitable chorus.

Sixty cicadas sit in trees along the roofline. A quiet cicada may start calling on its own, rarely,
but it is far more likely to start when it hears others: each listens to every caller within
earshot, by true 3-D distance, so a chorus can jump the gap from one porch side to the other or
from a wing to the porch. A call swells over a few seconds, holds with the slow pulsing "ree-ree"
of the song, and fades; then that cicada rests before it can call again. The result is the real
late-August pattern: choruses that rise in one part of the yard, roll through the trees, die out
and start again somewhere else. Each caller is a soft warm-green glow over a dusky olive night.
Dim, slow and seamless all night."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, smooth_noise, Flicker, nframes, looped

CODE = 'LB09'
TITLE = 'Cicadas'
KIND = 'ambient'
DESCRIPTION = ('The late-summer cicada drone: choruses rise where the cicadas hear each other, roll through the '
               'trees along the roof, jump across the porch, die out and start again elsewhere.')

DUSK = hexc('#2a3418')
SONG = hexc('#b8e04a')
HOT = hexc('#ffd24a')
FLOOR_COLOR = hexc('#2c3010')
FLOOR = 0.1
LOOP = 160.0


def render(G, seed=32):
    rng = np.random.default_rng(seed)

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        s = G.pd[G.path]
        P = G.pos[G.path]
        n = 60
        at = np.sort(rng.choice(G.N, n, replace=False))
        xs = s[at]
        dist = np.linalg.norm(P[at][:, None] - P[at][None], axis=2)
        hear = np.exp(-(dist / 110) ** 2)
        np.fill_diagonal(hear, 0)
        song_len = rng.uniform(9, 15, n)
        rest = rng.uniform(14, 55, n)
        song_hz = rng.uniform(0.55, 0.9, n)
        start = np.full(n, -1e9)                         # when each last began to call
        seeds_on = rng.choice(n, 4, replace=False)
        start[seeds_on] = -rng.uniform(0, 6, 4)
        haze = smooth_noise(rng, s, 160)
        leaf = Flicker(rng, G.N, 0.05, 0.2)
        width = rng.uniform(18, 30, n)

        def loud(t):
            u = t - start
            env = smoothstep(0, 3.5, u) * smoothstep(song_len, song_len - 3.5, u)
            return np.where((u >= 0) & (u <= song_len), env, 0.0)

        for f in range(len(out)):
            t = f * DT
            lv = loud(t)
            # who starts calling: quiet, rested, and hearing enough
            ready = (t - start) > (song_len + rest)
            heard = hear @ lv
            p = (0.012 + 0.16 * heard) * DT
            go = ready & (rng.random(n) < p)
            start[go] = t
            lv = loud(t)
            pulse = 0.85 + 0.15 * np.sin(2 * np.pi * song_hz * t + xs * 0.01) ** 2
            w = np.exp(-((s[None] - xs[:, None]) / width[:, None]) ** 2) * (lv * pulse)[:, None]
            I = np.clip(w.sum(0), 0, 1.3)
            buf = np.zeros((G.N, 3))
            buf += light(DUSK, 0.16 * (1 + 0.15 * haze + 0.05 * leaf(t)))
            hot = smoothstep(0.7, 1.2, I)[:, None]
            buf += perc(0.38 * np.clip(I, 0, 1.15))[:, None] * (SONG * (1 - hot) + HOT * hot)
            out[f][G.path] = buf
        return out

    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
