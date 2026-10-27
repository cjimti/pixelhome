"""Gulf Tide: Galveston is an island; the news came in by sea. A slow swell rolls in from the street as
a height field over the yard (four long directional wave trains whose periods divide the loop exactly),
so each crest touches the wing fronts first, runs up the Side, Porch Left and Porch Right as a moving
line of foam, and reaches the porch front last. In the sheltered notch between the wings the water is
shallower: waves slow, bend and lose height. A moonglade glitters where wave slopes catch the moon,
and the tide rises and falls once per loop."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, lerp, Flicker, nframes, looped

CODE = 'JT10'
TITLE = 'Gulf Tide'
KIND = 'ambient'
DESCRIPTION = ('A slow moonlit swell rolls in from the street: crests touch the wings first, run back along the sides '
               'as lines of foam and reach the sheltered porch last, smaller and slower.')

DEEP = hexc('#061a50')
TEAL = hexc('#0a6a8a')
FOAM = hexc('#d8f0ff')
MOON = hexc('#fff0d0')
FLOOR = 0.08
LOOP = 160.0


def render(G, seed=10):
    rng = np.random.default_rng(seed)

    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        X, Z = G.pos[G.path, 0], G.pos[G.path, 2]
        # shelter: inside the porch notch (between the wings, behind their fronts)
        inside = smoothstep(-200, -170, -np.abs(X + 22) + 152) * smoothstep(-190, -260, Z)
        depth_in = smoothstep(-200, -560, Z) * inside           # 0 at the notch mouth, 1 at the porch
        # long trains from the street; m cycles per loop keeps every train exactly periodic
        trains = [(11, 0.0, 520, 1.0), (13, 0.30, 430, 0.6), (16, -0.35, 380, 0.45), (7, 0.12, 700, 0.5)]
        glint_fl = Flicker(rng, n, 0.15, 0.6)
        moon_x = 330.0

        for f in range(len(out)):
            t = f * DT
            H = np.zeros(n)
            Hz = np.zeros(n)
            for m, ang, lam, a in trains:
                k = 2 * np.pi / lam
                dx, dz = np.sin(ang), -np.cos(ang)          # travelling away from the street
                # shallow water in the notch: extra phase lag (slower) that grows toward the porch
                lag = 2.6 * depth_in
                ph = k * (X * dx + Z * dz) - 2 * np.pi * m * t / LOOP + lag
                amp = a * (1 - 0.55 * depth_in)
                H += amp * np.sin(ph)
                Hz += amp * np.cos(ph) * k * dz
            norm = sum(a for *_, a in trains)
            h = H / norm                                     # about -1..1
            tide = 0.5 - 0.5 * np.cos(2 * np.pi * t / LOOP)
            # crests: sharpened so foam is a line, not a wash; high tide carries more of it
            crest = smoothstep(0.35 - 0.12 * tide, 0.8, h) ** 1.5
            body = 0.17 + 0.07 * h
            col = lerp(DEEP, TEAL, smoothstep(-0.6, 0.6, h)[:, None])
            I_foam = 0.36 * crest * (1 - 0.4 * depth_in)
            # moonglade: slope facing the street glitters near the moon's line of sight
            glade = np.exp(-((X - moon_x) / 170) ** 2) * (1 - inside)
            glint = smoothstep(0.004, 0.012, -Hz) * glade * np.clip(0.5 + 0.5 * glint_fl(t), 0, 1)
            fr = light(col, body) + light(FOAM, I_foam) + light(MOON, 0.22 * glint)
            out[f][G.path] = fr
        return out
    return looped(draw, LOOP, floor=(FLOOR, DEEP))
