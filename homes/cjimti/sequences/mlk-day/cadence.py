"""Cadence: The roof is a string and the middle of the Porch Front is the pulpit. Every syllable of a
speech strikes the string there, and the waves (a damped 1-D wave equation along the whole path) run
out both ways, turn the corners, bounce back from the two free ends and cross each other. Wave speed
follows each run's pixel spacing, so a little of every wave reflects at the corners where the spacing
changes.

The speech has a shape: measured opening phrases, then a refrain with the same rhythm that comes back
again and again, each time louder, and the wings answer it from the crowd. At the climax the refrain
comes faster and faster until the pulpit holds one long swell and the whole house rings in a standing
wave. Then it lets go and a warm after-glow, built up from everything that was said, remains."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, Flicker, nframes

CODE = 'MK03'
TITLE = 'Cadence'
KIND = 'show'
DESCRIPTION = ('The porch is a pulpit and every syllable sends a wave along the roof. A refrain returns, '
               'louder each time, the wings answer, and at the climax the whole house rings.')

GOLD = hexc('#ffa030')
WARM = hexc('#ffc890')
BLUE = hexc('#1838ff')
NIGHT = hexc('#0c18a0')
EMBER = hexc('#ff7020')


def script(rng):
    """[(start, amplitude, duration)] syllable strikes, plus crowd answers [(time, place, amp)]."""
    syl, crowd = [], []
    t = 3.0
    for k in range(4):                                   # measured opening
        for j in range(int(rng.integers(6, 10))):
            d = rng.uniform(0.12, 0.24)
            stress = 1.0 if j % 3 == 0 else 0.6
            syl.append((t, (0.45 + 0.08 * k) * stress * rng.uniform(0.8, 1.1), d))
            t += d + rng.uniform(0.08, 0.2)
        t += rng.uniform(0.9, 1.4)
    motif = [(0.0, 0.55, 0.16), (0.24, 0.5, 0.14), (0.48, 1.0, 0.34), (1.0, 0.6, 0.14), (1.24, 1.0, 0.5)]
    t += 0.6
    for k in range(10):                                  # the refrain
        g = lerp(0.6, 1.5, k / 9)
        for o, a, d in motif:
            syl.append((t + o, a * g, d))
        t += 1.9
        # answers from the crowd on the wings
        for _ in range(int(rng.integers(2, 4 + k // 2))):
            crowd.append((t + rng.uniform(-0.3, 0.6), rng.uniform(0.05, 0.38) if rng.random() < 0.5
                          else rng.uniform(0.66, 0.98), rng.uniform(0.3, 0.6) * g))
        if k < 6:                                        # the rest of the sentence
            for j in range(int(rng.integers(4, 8))):
                d = rng.uniform(0.12, 0.22)
                syl.append((t, 0.35 * g * rng.uniform(0.7, 1.1), d))
                t += d + rng.uniform(0.07, 0.16)
            t += rng.uniform(0.7, 1.0)
        else:
            t += 0.15 * (9 - k)
    return syl, crowd, t


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    syl, crowd, t_end = script(rng)
    T_SWELL = t_end + 0.4                      # the long held note
    D = T_SWELL + 22.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    L = G.length
    dx = 4.0
    x = np.arange(0, L + dx, dx)
    n = len(x)
    pf = G.seg['Porch Front']
    pulpit = 0.5 * (G.pd[pf].min() + G.pd[pf].max())

    # wave speed per run, following the pixel spacing (corners become partial mirrors)
    starts, speeds = [], []
    for name, pidx in G.path_segments():
        a, b = G.pd[G.path[pidx.min()]], G.pd[G.path[pidx.max()]]
        starts.append(a)
        speeds.append(120 * (b - a) / (len(pidx) - 1))
    c = np.array(speeds)[np.clip(np.searchsorted(starts, x, side='right') - 1, 0, None)]
    c2 = c ** 2
    sub = int(np.ceil(DT / (0.7 * dx / c.max())))
    h = DT / sub
    gamma = 0.75
    src = np.exp(-((x - pulpit) / 10) ** 2)
    u = np.zeros(n)
    v = np.zeros(n)
    glow = np.zeros(n)
    shimmer = Flicker(rng, G.N, 0.15, 0.6)
    s_t = np.array([s[0] for s in syl])
    s_a = np.array([s[1] for s in syl])
    s_d = np.array([s[2] for s in syl])

    def drive(t):
        ph = (t - s_t) / s_d
        on = (ph >= 0) & (ph <= 1)
        f = float((s_a[on] * np.sin(2 * np.pi * ph[on])).sum()) * 900   # push-pull: no net drift
        # the held swell: a slow push-pull at the pulpit that builds a standing wave
        if t > T_SWELL:
            ts = t - T_SWELL
            env = smoothstep(0, 2.5, ts) * (1 - smoothstep(8.0, 10.0, ts))
            f += 1100 * env * np.sin(2 * np.pi * 1.1 * ts)
        return f

    for fi in range(F):
        t = fi * DT
        for k in range(sub):
            tt = t + k * h
            lap = np.empty(n)
            lap[1:-1] = u[2:] - 2 * u[1:-1] + u[:-2]
            lap[0] = 2 * (u[1] - u[0])
            lap[-1] = 2 * (u[-2] - u[-1])
            acc = c2 * lap / dx ** 2 - gamma * v - 0.15 * u + drive(tt) * src
            for tc, place, amp in crowd:
                if 0 <= tt - tc < 0.25:
                    acc += 1600 * amp * np.sin(2 * np.pi * (tt - tc) / 0.25) * np.exp(-((x - place * L) / 16) ** 2)
            v += h * acc
            u += h * v
        e = np.abs(u)
        glow = glow * np.exp(-DT / 9.0) + DT * 0.04 * np.minimum(e, 2.5)
        up = np.interp(pdp, x, u)
        gp = np.interp(pdp, x, glow)

        settle = keys(t, [(T_SWELL + 9, 0), (T_SWELL + 13, 1)])
        fade = keys(t, [(0, 0), (1.5, 1), (D - 4, 1), (D, 0)])
        buf = light(NIGHT, 0.08 * (1 - settle * 0.5) * np.ones(G.N))
        pos = np.clip(up, 0, None)
        neg = np.clip(-up, 0, None)
        buf += light(GOLD, 0.95 * (1 - np.exp(-1.1 * pos)))
        buf += light(lerp(BLUE, WARM, 0.15), 0.5 * (1 - np.exp(-1.0 * neg)))
        hold = np.clip(gp, 0, 0.42) * (1 + 0.05 * shimmer(t)[G.path])
        hold = hold * (1 + keys(t, [(T_SWELL + 9, 0), (T_SWELL + 14, 0.25)]))
        col = lerp(EMBER[None], WARM[None], np.clip(gp / 0.45, 0, 1)[:, None])
        buf += perc(hold)[:, None] * col
        # the pulpit itself: a steady small light that brightens with each word
        pul = np.exp(-((pdp - pulpit) / 8) ** 2) * (0.35 + 0.5 * min(1, abs(drive(t)) / 900))
        buf += light(WARM, pul * keys(t, [(1, 0), (2.5, 1)]))
        out[fi][G.path] = buf * fade
    return out
