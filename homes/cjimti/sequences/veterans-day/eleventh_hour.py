"""The Eleventh Hour: A bell on the porch strikes eleven times. Each strike is an impulse in a damped
wave equation simulated along the whole roofline: two wavefronts run out from the porch, turn the
corners and reflect off the two free ends, so the echoes cross the house and interfere. After the
eleventh the house falls silent, then a slow gold remembrance gathers at the corners."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, lerp, smoothstep, Flicker, nframes

CODE = 'VT01'
TITLE = 'The Eleventh Hour'
KIND = 'show'
DESCRIPTION = ('A bell on the porch tolls eleven times; each stroke rings out along the roof, round the corners '
               'and back off the free ends. Then silence, and a gold remembrance gathers at the corners.')

NAVY = hexc('#1c34ff')
SILVER = hexc('#a8b8ff')
GOLD = hexc('#ff9a24')
WARM = hexc('#ffe2b0')


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    D = 78.0
    out = np.zeros((nframes(D), G.N, 3))
    pd = G.pd
    pf = G.seg['Porch Front']
    d0 = pd[pf].mean()

    # 1-D damped wave equation on a uniform grid along the path (distance units)
    dx = 4.0
    xs = np.arange(0, G.length + dx, dx)
    n = len(xs)
    c = 330.0
    sub = 5
    dt = DT / sub
    k2 = (c * dt / dx) ** 2
    u = np.zeros(n)
    v = np.zeros(n)
    damp = 0.3
    strike = np.exp(-((xs - d0) / 55) ** 2)

    T0, gap = 6.0, 3.9
    strikes = [T0 + i * gap for i in range(11)]
    last = strikes[-1]
    shimmer = Flicker(rng, G.N, 0.05, 0.25)
    # corners and free ends (the five turns and the two ends) for the remembrance
    corner_pd = [pd[G.path[i]] for i in (0, 80, 178, 260, 331, 380, 500)]
    cdist = np.min([np.abs(pd - p) for p in corner_pd], axis=0)
    hit = set(int(round(s / DT)) for s in strikes)

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        if f in hit:
            v += 1.0 * strike
        damp = keys(t, [(last + 2, 0.3), (last + 8, 1.4)])     # the ringing dies into silence
        for _ in range(sub):
            lap = np.empty(n)
            lap[1:-1] = u[2:] - 2 * u[1:-1] + u[:-2]
            lap[0] = 2 * (u[1] - u[0])          # free (reflecting) ends
            lap[-1] = 2 * (u[-2] - u[-1])
            v += k2 * lap / dt - damp * v * dt
            u += v * dt
        # energy envelope: smooth, sign-free brightness of the travelling rings
        grad = np.gradient(u, dx) * c
        e = np.sqrt((v ** 2 + grad ** 2) * 0.5) * 1.6
        amp = np.interp(pd, xs, e)

        # night: navy outline, slowly dimming through the strikes, nearly dark in the silence
        bg = keys(t, [(0, 0), (4, 0.2), (last, 0.15), (last + 4, 0.05), (last + 14, 0.035),
                      (last + 22, 0.12), (D - 4, 0.12), (D, 0)])
        fr += light(NAVY, bg * (1 + 0.15 * shimmer(t)))
        a = np.clip(amp, 0, 1.2)
        col = lerp(SILVER, WARM, np.clip(a, 0, 1)[:, None])
        fr += light(col, 0.95 * a)
        # the bell itself: a bright strike and a long gold hum with a slow beat
        bell = sum(np.exp(-(t - s) / 0.12) + 0.5 * np.exp(-(t - s) / 2.2) * (0.8 + 0.2 * np.cos(2 * np.pi * 1.3 * (t - s)))
                   for s in strikes if t >= s)
        near = np.exp(-((pd - d0) / 45) ** 2)
        fr[pf] += light(GOLD, np.clip(bell, 0, 1.1) * near[pf])

        # after the silence: remembrance gathers at the seven points, then joins along the roof
        g = keys(t, [(last + 16, 0), (last + 24, 1), (D - 6, 1), (D, 0)])
        if g > 0:
            reach = keys(t, [(last + 16, 10), (last + 30, 150), (D - 6, 175)])
            glow = np.exp(-(cdist / reach) ** 2) * (0.42 + 0.06 * shimmer(t))
            fr += light(GOLD, g * glow)
    return out
