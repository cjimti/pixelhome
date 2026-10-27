"""Rain on Dry Land: Dry, cracked ochre earth shimmers in the heat. Cloud shadows drift in from the
back of the house toward the street and lightning flickers far behind it. Then the first drops: each
one lands at a real spot in the yard or on the house and sends a ring outward across the ground; where
the ring crosses a run of the roof it shows as two lights running apart, and where it crosses a corner
it turns it. The rain builds to a downpour of overlapping rings, the ground darkens where water has
passed, the rain eases, the clouds part, sunlight crosses the wet ground and green comes up where the
water soaked in deepest."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'IP04'
TITLE = 'Rain on Dry Land'
KIND = 'show'
DESCRIPTION = ('Cracked dry earth, clouds from behind the house, then rain: every drop sends a ripple '
               'ring across the yard that the roofline crosses. The ground drinks, and green comes up.')

DRY = hexc('#d08a3a')
CRACK = hexc('#7a3a12')
SHADE = hexc('#6a6a80')
WET = hexc('#7a4420')
SHEEN = hexc('#8ab0c8')
RIPPLE = hexc('#b0d8f0')
BOLT = hexc('#c8c0ff')
SUN = hexc('#ffc878')
SPROUT = hexc('#5abf3a')


def noise2(rng, scale, n=24):
    """2-D value noise on a periodic lattice; returns f(x, z) in [-1, 1]."""
    lat = rng.uniform(-1, 1, (n, n))

    def f(x, z):
        u, v = x / scale, z / scale
        i, j = np.floor(u).astype(int), np.floor(v).astype(int)
        fu, fv = u - i, v - j
        fu, fv = fu * fu * (3 - 2 * fu), fv * fv * (3 - 2 * fv)
        a = lat[i % n, j % n]
        b = lat[(i + 1) % n, j % n]
        c = lat[i % n, (j + 1) % n]
        d = lat[(i + 1) % n, (j + 1) % n]
        return lerp(lerp(a, b, fu), lerp(c, d, fu), fv)
    return f


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    D = 78.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x, z = G.pos[:, 0], G.pos[:, 2]
    cloud1, cloud2 = noise2(rng, 420), noise2(rng, 190)
    crack_n = noise2(rng, 26)
    cracks = smoothstep(0.35, 0.6, np.abs(crack_n(x + 3000, z + 3000)) + 0.0)
    shimmer = Flicker(rng, G.N, 0.6, 2.0)
    sparkle = Flicker(rng, G.N, 0.3, 1.2)
    soak_bias = 0.25 * noise2(rng, 90)(x + 500, z + 500)

    # the drops: a Poisson stream whose rate follows the storm
    def rate(t):
        return keys(t, [(19.5, 0), (20, 0.6), (26, 3), (34, 10), (42, 18), (50, 12), (56, 3), (61, 0.4), (63, 0)])
    drops = []
    t = 20.0
    first = [(20.0, -60.0, -390.0, 1.0), (22.6, -420.0, -147.0, 0.9), (24.3, 380.0, -191.0, 0.9)]
    drops += first
    t = 25.0
    while t < 63:
        r = max(rate(t), 0.05)
        t += rng.exponential(1 / r)
        if rate(t) > 0:
            drops.append((t, rng.uniform(-700, 760), rng.uniform(-760, -40), rng.uniform(0.55, 1.0)))
    drops = np.array(drops)
    flashes = [(11.5, -300.0), (16.8, 350.0), (18.2, 330.0)]

    wet = np.zeros(G.N)
    sprouts = None
    for f in range(F):
        t = f * DT
        fr = out[f]
        master = keys(t, [(0, 0), (2.5, 1), (75, 1), (78, 0)])
        cover = keys(t, [(6, 0), (22, 0.8), (50, 1), (58, 0.6), (66, 0.0)])
        cz = z - 55 * t                                       # clouds move toward the street
        c = 0.5 + 0.35 * cloud1(x + 7000, cz + 9000) + 0.2 * cloud2(x + 1000 + 8 * t, cz + 4000)
        shadow = smoothstep(0.55 - cover, 0.95 - cover, c)    # 1 = under cloud
        dry_heat = keys(t, [(0, 1), (18, 0.3), (24, 0)])

        # ground colour: dry ochre with cracks -> dark wet loam where water has been
        wsat = np.clip(wet, 0, 1)[:, None]
        ground = lerp(lerp(DRY, CRACK, 0.75 * cracks[:, None]), WET, wsat)
        g_I = 0.24 - 0.04 * wsat[:, 0]
        g_I = g_I * (1 + 0.06 * dry_heat * shimmer(t)) * (1 - 0.32 * shadow)
        col = light(lerp(ground, SHADE, 0.45 * shadow[:, None]), g_I)

        # distant lightning behind the house: lights the back of the roof more than the front
        for tf, xf in flashes:
            u = t - tf
            if 0 <= u < 0.6:
                strokes = np.exp(-u / 0.05) + 0.7 * np.exp(-max(u - 0.12, 0) / 0.06) * (u > 0.12) + \
                    0.4 * np.exp(-max(u - 0.3, 0) / 0.1) * (u > 0.3)
                dist = np.hypot(x - xf, z + 1500)
                col += light(BOLT, 0.42 * strokes * (900 / dist) ** 2.5)

        # rain: rings on the ground, crossed by the roofline
        if len(drops):
            act = drops[(drops[:, 0] <= t) & (drops[:, 0] > t - 2.6)]
            if len(act):
                age = t - act[:, 0]
                dist = np.hypot(x[None, :] - act[:, 1:2], z[None, :] - act[:, 2:3])
                r = 170 * age[:, None]
                ring = np.exp(-((dist - r) / 14) ** 2) * np.exp(-age[:, None] / 1.0) / np.sqrt(1 + r / 160)
                hit = np.exp(-(dist / 9) ** 2) * np.exp(-age[:, None] / 0.12)
                I = act[:, 3:4] * (1.0 * ring + 1.0 * hit)
                I_r = np.clip(I.sum(0), 0, 1.2)
                col += light(RIPPLE, I_r)
                wet += 0.6 * I_r * DT + 0.0015 * (rate(t) / 18) ** 1.5
        # the sky clears: sunlight crosses the wet ground from the right
        sun = keys(t, [(56, 0), (64, 1), (74, 1), (78, 0.6)])
        if sun > 0:
            sweep = (t - 56) * 160 - 700
            # the edge of the clearing travels from the Right wing's end toward the Side
            beam = smoothstep(0, 1, np.clip((sweep - (640 - x)) / 400 + 0.5, 0, 1))
            col += light(SUN, 0.16 * sun * beam * (1 - shadow))
            glint = smoothstep(1.1, 1.6, sparkle(t)) * wsat[:, 0] * beam
            col += light(SHEEN, 0.4 * sun * glint)
            # green comes up in sprouts, first and most where the water soaked in deepest
            if sprouts is None:
                soak = wet + soak_bias
                cand = rng.permutation(G.N)[:220]
                cand = cand[rng.random(len(cand)) < np.clip(soak[cand] - 0.3, 0, 1)][:80]
                sprouts = (G.pd[cand], rng.uniform(4, 9, len(cand)),
                           60 + 8 * (1 - np.clip(soak[cand] - 0.3, 0, 1)) + rng.uniform(0, 3, len(cand)))
            sp_d, sp_w, sp_t = sprouts
            age = np.clip((t - sp_t) / 4, 0, 1)[:, None]
            g = (np.exp(-((G.pd[None, :] - sp_d[:, None]) / (sp_w[:, None] * (0.3 + 0.7 * age))) ** 2) * age).max(0)
            col = lerp(col, light(SPROUT, 0.5 * g), np.clip(1.3 * g, 0, 1)[:, None])
        fr[:] = col * master
    return out
