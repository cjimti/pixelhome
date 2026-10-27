"""Daybreak: One whole Galveston day on the roofline, lit by a real sun. The sun rises in the east, arcs
over the street and sets in the west; each pixel is lit only if it faces the sun and a ray toward the
sun clears the hipped roofs of the three house blocks, so eaves catch first light, the wings throw
moving shadows across the porch notch, and the light's colour follows the sun's height (deep red at
the horizon to warm white at noon) under a sky that goes from indigo to blue and back. At dusk one
star comes out over the porch."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, colormap, Flicker, nframes

CODE = 'OT16'
TITLE = 'Daybreak'
KIND = 'show'
DESCRIPTION = ('A whole day in a minute, lit by a real sun: first light catches the eaves that face east, the wings '
               'throw shadows across the porch, the light warms and whitens, then sets red, and one star comes out.')

STAR = hexc('#fff4e0')

# plan-view house blocks (x0, x1, z0, z1) with hipped roofs rising from the eaves at y = 150
BLOCKS = [(-596, -196, -637, -147), (-196, 152, -900, -569), (152, 629, -900, -191)]
PITCH = 0.62                                 # roof rise per unit run (about 32 degrees)

SUN = colormap([(-6, (0.35, 0.02, 0.0)), (0, (1.0, 0.16, 0.02)), (4, (1.0, 0.36, 0.06)),
                (12, (1.0, 0.58, 0.22)), (25, (1.0, 0.72, 0.42)), (45, (1.0, 0.80, 0.55))])
SKY = colormap([(-14, (0.02, 0.02, 0.10)), (-6, (0.10, 0.04, 0.22)), (-1, (0.50, 0.12, 0.25)),
                (4, (0.45, 0.30, 0.45)), (14, (0.25, 0.40, 0.85)), (65, (0.22, 0.45, 1.0))])


def roof_height(x, z):
    h = np.full(x.shape, -1e9)
    for x0, x1, z0, z1 in BLOCKS:
        inside = (x > x0 + 0.5) & (x < x1 - 0.5) & (z > z0 + 0.5) & (z < z1 - 0.5)
        d = np.minimum(np.minimum(x - x0, x1 - x), np.minimum(z - z0, z1 - z))
        h = np.where(inside, np.maximum(h, 150 + PITCH * d), h)
    return h


def render(G, seed=6):
    rng = np.random.default_rng(seed)
    D = 72.0
    out = np.zeros((nframes(D), G.N, 3))
    P = G.pos[G.path]
    pdp = G.pd[G.path]
    segs = dict(G.path_segments())
    # outward normals of each run, in plan
    normal = np.zeros((G.N, 3))
    for name, n in (('Side', (-1, 0, 0)), ('Left', (0, 0, 1)), ('Porch Left', (1, 0, 0)),
                    ('Porch Front', (0, 0, 1)), ('Porch Right', (-1, 0, 0)), ('Right', (0, 0, 1))):
        normal[segs[name]] = n
    steps = np.geomspace(2, 900, 40)
    RISE, SET = 10.0, 58.0
    pf = segs['Porch Front']
    cstar = pdp[pf].mean()
    tw = Flicker(rng, 1, 1.5, 4.0)
    shade = np.ones(G.N)

    for f in range(len(out)):
        t = f * DT
        u = (t - RISE) / (SET - RISE)
        ph = u - 0.12 * np.sin(2 * np.pi * u)                 # linger at sunrise and sunset
        el = 44 * np.sin(np.pi * np.clip(ph, -0.25, 1.25))
        az = np.radians(lerp(105, -105, ph))
        e = np.radians(el)
        s = np.array([np.cos(e) * np.sin(az), np.sin(e), np.cos(e) * np.cos(az)])

        # shadows: march from every pixel toward the sun through the roofs
        if el > -3:
            rz = P[:, 2, None] + s[2] * steps[None, :]
            ry = 150 + s[1] * steps[None, :]
            rx = P[:, 0, None] + s[0] * steps[None, :]
            blocked = (ry < roof_height(rx, rz)).any(1)
            lit = ~blocked
        else:
            lit = np.zeros(G.N, bool)
        shade = shade * 0.85 + lit * 0.15                     # soft shadow edges in time
        face = np.clip(normal @ s, 0, None)
        top = max(s[1], 0) * 0.45                             # the gutter also sees the sun from above
        direct = (0.15 + 0.85 * face + top) * shade
        horizon = smoothstep(-4, 2, el)
        I = 0.66 * direct * horizon * keys(t, [(0, 1), (D - 4, 1), (D, 0)])
        sky = keys(el, [(-14, 0.07), (-3, 0.14), (4, 0.2), (30, 0.22)]) * keys(t, [(0, 0), (2, 1), (D - 4, 1), (D, 0)])
        # sky light comes more from the side the sun is on (scattering)
        scatter = 1 + 0.6 * np.clip(normal @ np.array([s[0], 0, s[2]]), -1, 1)
        buf = light(SKY(np.full(G.N, el)), sky * scatter) + light(SUN(np.full(G.N, el)), I)

        # dusk: the evening star over the porch
        if t > SET + 3:
            k = keys(t, [(SET + 3, 0), (SET + 7, 0.85), (D - 3, 0.85), (D, 0)])
            k *= 0.9 + 0.1 * tw(t)[0]
            buf += light(STAR, k * np.exp(-((pdp - cstar) / 7) ** 2))
        out[f][G.path] = buf
    return out
