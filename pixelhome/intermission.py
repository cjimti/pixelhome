"""The countdown every intermission is built on: five minutes between shows with the whole house lit.

A bed colour holds the house while a second colour fills it toward the porch, so anyone on the street can see how
long is left: first the wings from their outer ends (Side alongside Left), then the porch's side runs from the front,
then Porch Front closing in on its middle. A bright front leads the fill, a wave runs over the filled part on every
minute, and when the fill meets in the middle the house swells for the finale and settles back to the bed, ready for
the show. An intermission's render() calls countdown() and draws its own touches on top; its score() takes its
timings from MARKS (or marks() for another length).

    frames = countdown(G, bed=hexc('#401060'), fill=hexc('#ff6a1f'), seed=seed)
"""
import numpy as np
from .fx import DT, light, nframes, smoothstep

SECONDS = 300.0
FINALE = 15.0


def marks(seconds=SECONDS, finale=FINALE):
    """Times for the score: each minute's wave, when the fill meets in the middle, the finale and the end."""
    full = seconds - finale
    return dict(minutes=[float(m) for m in np.arange(60, full, 60)], full=full, finale=full, end=seconds)


MARKS = marks()


def reach(t, seconds=SECONDS, finale=FINALE):
    """The fill's front at time(s) t: pixels whose order() is above it are filled (sweeps from 1.04 to -0.04)."""
    return 1.04 - 1.08 * np.clip(np.asarray(t, float) / (seconds - finale), 0, 1)


def order(G):
    """Per node, 1 for the first pixels to fill down to 0 for the last (the middle of Porch Front)."""
    v = np.zeros(G.N)
    span = lambda name: (G.pd[G.seg[name]] - G.pd[G.seg[name]].min()) / np.ptp(G.pd[G.seg[name]])
    v[G.seg['Left']] = 1 - 0.45 * span('Left')                 # outer end -> the porch corner
    v[G.seg['Side']] = 1 - 0.45 * (1 - span('Side'))           # with Left, from the front corner back
    v[G.seg['Right']] = 0.55 + 0.45 * span('Right')            # the free end fills first
    v[G.seg['Porch Left']] = 0.55 - 0.15 * span('Porch Left')  # front -> back
    v[G.seg['Porch Right']] = 0.4 + 0.15 * span('Porch Right')
    u = span('Porch Front')
    v[G.seg['Porch Front']] = 0.4 * np.abs(2 * u - 1)           # both ends -> the middle
    return v


def countdown(G, bed, fill, edge=np.array([1.0, 0.95, 0.85]), seconds=SECONDS, finale=FINALE,
              level=(0.34, 0.62), seed=0):
    """(F, N, 3) PWM frames. bed and fill are PWM colours (hexc); level is the perceptual (bed, fill) intensity."""
    rng = np.random.default_rng(seed)
    F = nframes(seconds)
    t = np.arange(F) * DT
    v = order(G)
    d = G.pd / G.length
    full = seconds - finale
    p = np.clip(t / full, 0, 1)                                 # how much has filled
    front_at = reach(t, seconds, finale)
    sparkle_phase = rng.uniform(0, 2 * np.pi, G.N)
    out = np.empty((F, G.N, 3), np.float32)
    mins = marks(seconds, finale)['minutes']
    for f0 in range(0, F, 400):
        tt = t[f0:f0 + 400, None]
        pp = p[f0:f0 + 400, None]
        rr = front_at[f0:f0 + 400, None]
        filled = smoothstep(-0.012, 0.012, v[None] - rr)                 # 1 where the fill has reached
        front = np.exp(-((v[None] - rr) / 0.018) ** 2) * (pp < 1)        # the leading edge
        drift = 0.5 + 0.5 * np.sin(2 * np.pi * (d[None] * 3 - tt / 9))   # slow travelling shimmer
        bed_i = level[0] * (0.82 + 0.18 * drift)
        fill_i = level[1] * (0.85 + 0.15 * np.sin(2 * np.pi * (d[None] * 5 + tt / 6)))
        wave = np.zeros_like(filled)
        for m in mins:                                          # a wave over the filled part, toward the front
            age = tt - m
            pos = 1.05 - age / 3.0                              # sweeps v from the outer ends toward the front
            wave += np.exp(-((v[None] - pos) / 0.08) ** 2) * (age >= 0) * (age < 4) * filled
        sparkle = front * (0.7 + 0.3 * np.sin(sparkle_phase[None] + tt * 23))
        # the finale: a swell that chases in toward the porch, then settles to the bed for the show
        fin = np.clip((tt - full) / finale, 0, 1)
        chase = 0.5 + 0.5 * np.sin(2 * np.pi * (v[None] * 4 + (tt - full) * 1.2))
        swell = smoothstep(0, 0.75, fin) * (1 - smoothstep(0.82, 0.97, fin))
        settle = smoothstep(0.85, 1.0, fin)                     # fill gives the house back to the bed
        k = filled * (1 - settle)
        col = (light(bed, bed_i * (1 - k)) + light(fill, (fill_i + swell * (0.2 + 0.25 * chase) + 0.35 * wave) * k)
               + light(edge, 0.85 * sparkle + 0.4 * wave * k + 0.3 * swell * chase * k))
        out[f0:f0 + 400] = np.clip(col, 0, 1)
    return out
