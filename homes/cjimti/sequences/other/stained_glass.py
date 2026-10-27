"""Stained Glass: The roofline is the leading of a great church window. Every run is cut into panes of
jewel-coloured glass (mostly deep blue and gold, with ruby, green and violet), separated by dark lead
lines, and every corner is a lead joint. The pattern is mirror-symmetric like a real window: the Left
and Right wings carry the same panes, as do Porch Left and Porch Right, and the Porch Front is a rose
laid out symmetrically about its middle. Each pane has its own seedy-glass texture.

Light comes from behind: a broad soft sun moves slowly on a closed path in the plane of the roof, so
the bright patch it makes travels through the panes in real 3-D, hottest panes washing toward white,
while slow clouds dim and return the whole window. Seamless all-night loop."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, smooth_noise, nframes, looped

CODE = 'OT07'
TITLE = 'Stained Glass'
KIND = 'ambient'
DESCRIPTION = ('The roof becomes a church window: panes of blue, gold and ruby glass between dark lead lines, '
               'with a slow sun moving behind them.')

JEWELS = [('#1830ff', 4), ('#ff9a20', 3), ('#e02040', 2), ('#20a048', 1), ('#6020d0', 2), ('#ff6a10', 1)]
WHITE = hexc('#ffd8b0')
FLOOR_COLOR = hexc('#101c90')
FLOOR = 0.07
LOOP = 170.0


def render(G, seed=31):
    rng = np.random.default_rng(seed)
    cols = np.array([hexc(c) for c, _ in JEWELS])
    wts = np.array([w for _, w in JEWELS], float)
    wts /= wts.sum()

    # each pixel's position within its run, measured from the axis of symmetry outward
    frac = np.zeros(G.N)
    group = {}
    for name in G.seg:
        idx = G.seg[name]
        u = np.linspace(0, 1, len(idx))                 # in channel order = first -> last in home.json
        if name == 'Left':
            f = 1 - u                                   # from the porch corner outward
        elif name == 'Right':
            f = u
        elif name == 'Porch Left':
            f = u                                       # from the wing corner back
        elif name == 'Porch Right':
            f = 1 - u
        elif name == 'Porch Front':
            f = np.abs(2 * u - 1)                       # rose: symmetric about the middle
        else:
            f = u
        frac[idx] = f
        group[name] = {'Left': 'W', 'Right': 'W', 'Porch Left': 'P', 'Porch Right': 'P'}.get(name, name)

    def panes(n_min, n_max):
        k = int(rng.integers(n_min, n_max + 1))
        cuts = np.sort(rng.uniform(0.04, 0.96, k - 1))
        cuts = np.concatenate([[0.0], cuts, [1.0]])
        return cuts, rng.choice(len(cols), k, p=wts), rng.uniform(0, 1000, k)

    spec = {'W': panes(9, 12), 'P': panes(8, 11), 'Porch Front': panes(6, 7), 'Side': panes(9, 12)}
    colour = np.zeros((G.N, 3))
    lead = np.zeros(G.N)
    tex = np.zeros(G.N)
    for name, idx in G.seg.items():
        cuts, ci, seeds = spec[group[name]]
        f = frac[idx]
        length = G.pd[idx].max() - G.pd[idx].min()
        k = np.clip(np.searchsorted(cuts, f, side='right') - 1, 0, len(ci) - 1)
        colour[idx] = cols[ci[k]]
        edge = np.min(np.abs(f[:, None] - cuts[None, :]), axis=1) * length
        lead[idx] = smoothstep(1.5, 5.0, edge)
        for j in range(len(ci)):
            m = k == j
            if m.any():
                r2 = np.random.default_rng(int(seeds[j]))
                tex[idx[m]] = smooth_noise(r2, f[m] * length, 9.0, octaves=2)
    lead[np.abs(frac - 1) < 1e-9] = 0.0            # outer ends of each run are lead too

    xz = G.pos[:, [0, 2]]

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        for fr in range(len(out)):
            t = fr * DT
            w = 2 * np.pi * t / LOOP
            sun = np.array([16 + 620 * np.sin(w), -390 + 260 * np.sin(2 * w + 0.7)])
            d = np.linalg.norm(xz - sun, axis=1)
            beam = np.exp(-(d / 330) ** 2)
            cloud = 0.88 + 0.12 * np.sin(3 * w + 1.3) * np.sin(5 * w)
            I = (0.15 + 0.24 * beam) * cloud * (1 + 0.14 * tex) * lead
            hot = smoothstep(0.55, 1.0, beam)[:, None] * 0.35
            c = colour * (1 - hot) + WHITE * hot
            out[fr] = perc(I)[:, None] * c
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
