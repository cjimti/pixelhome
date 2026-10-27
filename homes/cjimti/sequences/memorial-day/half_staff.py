"""Half-Staff: From the street the Side and the two porch runs recede, so they read as tall poles.
At first light three flags are run briskly to the peak, pause at the finial, then are lowered slowly
to half-staff and stay there, rippling in a light wind, the empty upper half of each pole left dark."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'MM02'
TITLE = 'Half-Staff'
KIND = 'show'
DESCRIPTION = ('The Side and porch runs become three flagpoles. The flags are run briskly to the peak, '
               'then lowered slowly to half-staff, where they stay and ripple in the wind.')

RED = hexc('#d0141e')
WHITE = hexc('#f4f1ea')
BLUE = hexc('#2440b0')
NAVY = hexc('#0b1d4a')
SILVER = hexc('#c9d4e8')
GOLD = hexc('#ffc060')

FH = 0.30          # flag height as a fraction of the pole
CANTON = 0.45      # top share of the flag that is the blue field
STRIPES = 5


def render(G, seed=2):
    rng = np.random.default_rng(seed)
    D = 64.0
    out = np.zeros((nframes(D), G.N, 3))
    z = G.pos[:, 2]
    poles = []
    for name, z0, z1 in [('Porch Left', -151, -565), ('Porch Right', -196, -565), ('Side', -146, -637)]:
        idx = G.seg[name]
        poles.append((idx, (z0 - z[idx]) / (z0 - z1)))      # 0 at the street end, 1 at the far end
    horiz = np.concatenate([G.seg['Left'], G.seg['Right']])
    uh = G.pos[horiz, 0]
    front = G.seg['Porch Front']
    stars = Flicker(rng, G.N, 0.15, 0.5)
    sparkle = rng.random(G.N) < 0.35

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        dawn = keys(t, [(0, 0), (5, 1), (58, 1), (63, 0)])
        top = keys(t, [(0, 0.0), (10, FH * 0.35), (16, 1.0), (22, 1.0), (38, 0.57), (40, 0.55)])
        present = keys(t, [(4, 0), (8, 1), (60, 1), (63.5, 0)])
        wind = keys(t, [(9, 0.2), (16, 1.0), (40, 0.7), (50, 1.0)])
        # ground: the wing fronts are the crowd at the foot of the poles, a quiet silver line
        salute = keys(t, [(15, 0), (17, 1), (22, 1), (26, 0.35)])
        fr[horiz] += light(lerp(NAVY, SILVER, 0.35 + 0.4 * salute), dawn * (0.12 + 0.14 * salute) * np.ones(len(horiz)))
        fr[front] += light(NAVY, dawn * 0.14 * np.ones(len(front)))
        for idx, h in poles:
            # the pole itself, faint; a gold finial at the very top glints when the flag reaches it
            fr[idx] += light(SILVER, dawn * 0.07 * np.ones(len(idx)))
            fin = np.exp(-((h - 1.0) / 0.025) ** 2)
            glint = 0.15 + 0.6 * np.exp(-((t - 16.3) / 1.2) ** 2)
            fr[idx] += light(GOLD, dawn * glint * fin)
            # flag coordinate v: 0 at the top (hoist), 1 at the bottom edge, with a travelling ripple
            ripple = 0.018 * wind * np.sin(2 * np.pi * (h * 3.5 - 0.55 * t))
            v = (top - h + ripple) / FH
            mask = smoothstep(-0.04, 0.03, v) * (1 - smoothstep(0.97, 1.04, v)) * present
            sv = (v - CANTON) / (1 - CANTON) * STRIPES
            frac = sv - np.floor(sv)
            # anti-aliased stripe boundaries: blend red/white over a soft edge
            red_w = np.where(np.floor(sv) % 2 == 0, 1 - smoothstep(0.65, 1.0, frac), smoothstep(0.65, 1.0, frac))
            red_w = np.where(sv < 0, 1.0, red_w)
            stripe_col = lerp(WHITE * 0.72, RED, red_w[:, None])
            in_canton = 1 - smoothstep(-0.25, 0.1, sv)
            st = sparkle[idx] * np.clip(stars(t)[idx], 0, 1) ** 2
            canton_col = BLUE + (WHITE - BLUE) * 0.55 * st[:, None]
            col = lerp(stripe_col, canton_col, in_canton[:, None])
            shade = 1 + 0.22 * wind * np.sin(2 * np.pi * (h * 3.5 - 0.55 * t) + 1.2)
            fr[idx] = fr[idx] * (1 - mask[:, None]) + perc(0.8 * mask * shade)[:, None] * col
    return out
