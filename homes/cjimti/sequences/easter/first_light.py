"""First Light: A sunrise that travels through the house from back to front. Night first: deep
indigo and a few stars. The porch, set far back, is sealed dark until a seam of light shows at its
back corners and the dark slides aside like a stone rolled away; warm light pours out of it and
runs forward along the porch sides toward the street. Then the dawn itself arrives from behind the
house: a line of sky colour sweeps forward in depth (z), so the Side, Porch Left and Porch Right,
which run away from the street, show the whole gradient at once (violet, rose, coral, gold),
while the sun's halo rises behind the porch, shifting from red to gold. Birds wake on the wings."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, Flicker, nframes

CODE = 'EA04'
TITLE = 'First Light'
KIND = 'show'
DESCRIPTION = 'Night, then light pours out of the set-back porch like a stone rolled aside, and dawn sweeps from the back of the house to the street: violet, rose, coral, gold.'


def lin(h):
    return hexc(h) ** 2.2


NIGHT = lin('#2a2f7a')
STAR = lin('#dfe6ff')
INNER = lin('#ffe6b4')
BIRD = lin('#fffbe8')

# dawn ramp by "how long ago the dawn line passed" (in units of depth/300): colour and perceptual level
RAMP = [(-2.0, '#3442b8', 0.19), (-1.1, '#6a46c0', 0.24), (-0.45, '#c05aa8', 0.3), (0.0, '#ff7a90', 0.42),
        (0.5, '#ff8a4c', 0.52), (1.1, '#ffb048', 0.6), (1.9, '#ffd27a', 0.62), (3.0, '#ffe7b8', 0.6), (4.0, '#c8dcff', 0.52)]


def blackbody(u):
    """Sun colour from just-risen red (u=0) to high gold-white (u=1), as linear PWM."""
    return np.array([1.0, 0.12 + 0.6 * u ** 0.8, 0.02 + 0.32 * u ** 1.6])


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    D = 70.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    P = G.pos
    z, x = P[:, 2], P[:, 0]
    n = G.N
    tw = Flicker(rng, n, 0.2, 0.9)
    stars = rng.random(n) < 0.06
    ra = np.array([r[0] for r in RAMP])
    rc = np.array([perc(r[2]) * lin(r[1]) for r in RAMP])
    pf = G.seg['Porch Front']
    porch_sides = np.concatenate([G.seg['Porch Left'], G.seg['Porch Right']])
    in_pf = np.zeros(n, bool); in_pf[pf] = True
    in_ps = np.zeros(n, bool); in_ps[porch_sides] = True
    wings = np.concatenate([G.seg['Left'], G.seg['Right']])
    seam = np.exp(-((x - (-194)) / 10) ** 2) + np.exp(-((x - 150) / 10) ** 2)
    chirps = []
    for _ in range(26):
        k = G.pi[wings[rng.integers(len(wings))]]
        k = int(np.clip(k, 84, 497)) if k < 300 else int(np.clip(k, 384, 497))
        t0 = rng.uniform(49, 63)
        chirps += [(G.path[k], t0), (G.path[k], t0 + 0.16), (G.path[k + rng.choice([-2, 2])], t0 + 0.34)]

    for f in range(F):
        t = f * DT
        # night sky with a few slow stars, fading as the dawn comes
        night_I = keys(t, [(0, 0), (3, 1), (60, 1)])
        dawn_line = keys(t, [(14, -1350.0), (58, 560.0)])          # z of the dawn line
        a = (dawn_line - z) / 300.0
        sky = np.stack([np.interp(a, ra, rc[:, c]) for c in range(3)], -1) * night_I
        starI = 0.35 * stars * np.clip(tw(t), 0, 1) ** 2 * smoothstep(-0.6, -1.6, a) * night_I
        sky += light(STAR, starI)

        # the sealed porch: darker than the sky, then a seam, then the stone slides aside
        seal = keys(t, [(0, 1), (13, 1), (15, 0)])
        roll = keys(t, [(8.5, -260.0), (13.5, 190.0)])               # occluder's trailing edge in x
        opening = np.where(in_pf, smoothstep(roll + 20, roll - 20, x), 0) if t >= 8.5 else np.zeros(n)
        sky[in_pf] *= 1 - 0.85 * seal
        seamI = keys(t, [(4, 0), (7, 0.55), (8.5, 0.7), (11, 0.4), (15, 0)]) * seam * in_pf
        sky += light(INNER, seamI)
        pour = keys(t, [(9, 0), (12.5, 1), (24, 1), (36, 0.0)])
        inner = np.where(in_pf, opening * 0.7, 0.0)
        # light runs forward from the porch along its sides toward the street, and spills onto the wings
        front = keys(t, [(11.5, -569.0), (16.0, -150.0)])
        run = in_ps * smoothstep(front + 30, front - 30, z) * (0.35 + 0.35 * smoothstep(-180, -569, z))
        dist_corner = np.minimum(np.abs(x + 196), np.abs(x - 152))
        spill = np.isin(np.arange(n), wings) * smoothstep(15.0, 18.5, t) * np.exp(-dist_corner / 120)
        inner = inner + run + 0.35 * spill
        sky += light(INNER, pour * inner)

        # the sun's halo rises behind the porch and grows
        sun_u = smoothstep(22, 58, t)
        sz = -1150 + 480 * sun_u
        d = np.hypot(x - 16, (z - sz) * 0.8)
        R = 320 + 650 * sun_u
        halo = keys(t, [(18, 0), (30, 0.6), (55, 0.5), (64, 0.35)]) * np.exp(-(d / R) ** 2)
        sky += light(blackbody(sun_u), halo)

        # dawn chorus: short bright double chirps on the wings
        for k, t0 in chirps:
            if 0 <= t - t0 < 0.12:
                sky[k] += BIRD * perc(0.7 * np.sin(np.pi * (t - t0) / 0.12))

        out[f] = sky * keys(t, [(64, 1), (69.5, 0)])
    return out
