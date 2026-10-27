"""Missing Man: Four aircraft lights in finger-four formation fly real 3-D paths over the roof. The first
pass crosses the front of the house left to right; each light's glow falls on whatever roof is beneath
it, so the formation reads as a staggered quartet climbing each receding run at its own depth. On the
second pass they come in from the street straight down the Side and the two porch runs; halfway there
the number-three light pulls up and away to the right, its glow widening, dimming and turning gold as
it climbs out past the free end of the Right wing, while the other three fly on into the dark. The run
it left stays faintly lit."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, keys, lerp, nframes

CODE = 'MM05'
TITLE = 'Missing Man'
KIND = 'show'
DESCRIPTION = ('Four lights fly over the house in formation. On the second pass, one pulls up and away '
               'into the sky while the others fly on.')

SILVER = hexc('#e4ebf7')
GOLD = hexc('#ffc870')
NAVY = hexc('#0b1d4a')


def render(G, seed=5):
    rng = np.random.default_rng(seed)
    D = 62.0
    out = np.zeros((nframes(D), G.N, 3))
    xz = G.pos[:, [0, 2]]
    trail = np.zeros(G.N)
    trail_g = np.zeros(G.N)
    memory = np.zeros(G.N)
    pr = G.seg['Porch Right']

    # pass 1: east to west across the house; (dx behind the lead, z). Flying west, right is away from
    # the street: number two rides the wing fronts, three and four step back toward the porch front
    p1 = [(0, -300), (90, -165), (90, -440), (180, -575)]
    # pass 2: from the street toward the back; (x, dz behind the lead)
    p2 = [(-196, 0), (-596, 90), (152, 90), (430, 180)]

    def planes(t):
        """[(x, z, altitude, colour weight gold 0..1, strength)] for the four aircraft at time t."""
        res = []
        if 4 < t < 20:
            xl = lerp(1000, -1250, (t - 4) / 16)
            for dx, z in p1:
                res.append((xl + dx, z, 40.0, 0.0, 1.0))
        if 25 < t < 46:
            zl = lerp(260, -1100, (t - 25) / 21)
            for k, (x, dz) in enumerate(p2):
                z = zl + dz
                alt, gold, s = 40.0, 0.0, 1.0
                if k == 2 and t > 35.0:             # number three pulls up and away, climbing right
                    u = smoothstep(35.0, 44.0, t)
                    z0 = lerp(260, -1100, 10 / 21) + dz
                    z = lerp(z0, -200, smoothstep(35.0, 40.0, t)) + (z - z0) * (1 - smoothstep(35, 37, t))
                    x = x + 760 * u ** 1.3
                    alt = 40 + 700 * u ** 1.5
                    gold = smoothstep(36, 40, t)
                res.append((x, z, alt, gold, s))
        return res

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        sky = keys(t, [(0, 0), (3, 0.08), (D - 4, 0.08), (D, 0)])
        fr += perc(sky) * NAVY
        now = np.zeros(G.N)
        now_g = np.zeros(G.N)
        for x, z, alt, gold, s in planes(t):
            # the glow under an aircraft widens and fades as it climbs
            sig = 85.0 + 0.3 * (alt - 40)
            amp = s * (85.0 / sig) ** 0.75
            r2 = (xz[:, 0] - x) ** 2 + (xz[:, 1] - z) ** 2
            g = amp * np.exp(-r2 / sig ** 2)
            now = np.maximum(now, g * (1 - gold))
            now_g = np.maximum(now_g, g * gold)
        trail = np.maximum(trail * np.exp(-DT / 0.9), now * 0.45)
        trail_g = np.maximum(trail_g * np.exp(-DT / 1.6), now_g * 0.5)
        I = np.maximum(now, trail)
        fr += perc(0.85 * I)[:, None] * SILVER + perc(0.85 * np.maximum(now_g, trail_g))[:, None] * GOLD
        # the run the missing aircraft left keeps a faint gold glow until the end
        mem = keys(t, [(38, 0), (44, 0.22), (D - 8, 0.22), (D - 1, 0)])
        u = (G.pos[pr, 2] + 196) / (-565 + 196)
        fr[pr] += perc(mem * (0.6 + 0.4 * (1 - u)))[:, None] * GOLD
    return out
