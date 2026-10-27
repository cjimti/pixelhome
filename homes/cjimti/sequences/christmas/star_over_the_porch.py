"""Star over the Porch: A point of light appears low behind the porch, twinkling. It rises and comes
forward until it hangs in the air over the middle of the U, and its diffraction spikes (four long,
four short, white at the core and fringed gold and blue at the edges) are cast out across the roof by
angle from the star's real 3-D position, so as the star turns each spike sweeps over wings, porch
sides and corners. Three travellers' lanterns set out from the two free ends and follow it along the
roofline to the porch; when they arrive the spikes fold down and the porch fills with light."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, Flicker, colormap, nframes

CODE = 'XM04'
TITLE = 'Star over the Porch'
KIND = 'show'
DESCRIPTION = ('A star rises behind the porch and hangs over the house, its eight diffraction spikes sweeping '
               'the roof as it turns. Three lanterns follow it from the far ends to the porch.')

NIGHT = hexc('#060c30')
CORE = hexc('#fff4e0')
GOLD = hexc('#ffb030')
GLORY = hexc('#ffc860')
TRAVELLERS = [hexc('#ffb020'), hexc('#ff7010'), hexc('#ff4070')]


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    D = 64.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    P = G.pos
    x = G.pd
    scint = Flicker(rng, 3, 2.0, 6.0)
    sway = Flicker(rng, 3, 0.8, 1.6)
    fringe = colormap([(0, (1.0, 0.95, 0.85)), (0.5, (1.0, 0.62, 0.18)), (0.85, (0.55, 0.45, 0.6)),
                       (1.2, (0.15, 0.3, 1.0)), (2.0, (0.1, 0.2, 0.8))])
    pf = G.seg['Porch Front']
    centre_pd = G.pd[pf[len(pf) // 2]]
    porch_dist = np.abs(x - centre_pd)
    # three lanterns: two from the back of Side, one from the end of Right, arriving at the porch
    trips = [(0.0, centre_pd - 26, 14.0, 47.0), (0.0, centre_pd - 52, 16.5, 47.5),
             (G.length, centre_pd + 30, 18.0, 47.0)]

    for f in range(F):
        t = f * DT
        fr = out[f]
        sky = keys(t, [(0, 0), (2, 0.07), (58, 0.07), (63.5, 0)])
        fr += light(NIGHT, np.full(G.N, sky))

        # the star's position: low and far behind the porch, rising and coming forward over the U
        sz = keys(t, [(2, -1150), (9, -1000), (22, -400), (46, -380), (50, -470)])
        sy = keys(t, [(2, 170), (9, 230), (22, 330), (46, 320), (50, 250)])
        sx = keys(t, [(2, 0), (22, -20), (46, -20), (50, -20)])
        s3 = np.array([sx, sy, sz])
        rel = P - s3
        rxz = np.hypot(rel[:, 0], rel[:, 2])
        d3 = np.linalg.norm(rel, axis=1)
        ang = np.arctan2(rel[:, 2], rel[:, 0])
        bright = keys(t, [(2, 0), (4, 0.6), (9, 0.75), (22, 1.0), (55, 1.0), (60, 0.5), (63.5, 0)])
        tw = 1 + 0.12 * scint(t)[0]

        # the pin-prick: before the spikes can reach, the star is a point seen just over the porch roof
        if t < 14:
            pin = keys(t, [(2, 0), (4, 1), (11, 1), (14, 0)])
            fr += light(CORE, 0.85 * pin * tw * np.exp(-(porch_dist / 4.5) ** 2) * (G.seg_of == 'Porch Front'))
            fr += light(hexc('#a0b8ff'), 0.25 * pin * np.exp(-(porch_dist / 18) ** 2) * (G.seg_of == 'Porch Front'))

        # diffraction spikes cast by angle from the star
        theta = 0.25 * np.pi + 2 * np.pi * keys(t, [(9, 0), (46, 0.55), (52, 0.625)]) + 0.02 * np.sin(t * 0.7)
        reach = keys(t, [(8, 0), (20, 1.0), (46, 1.0), (49, 1.25), (54, 0.35), (60, 0)])
        spike = np.zeros(G.N)
        off = np.full(G.N, 9.0)
        for k in range(8):
            main = k % 2 == 0
            w = (0.065 if main else 0.04)
            a = wrap(ang - theta - k * np.pi / 4)
            length = (900 if main else 420) * reach
            amp = (1.0 if main else 0.55) * np.exp(-(rxz / max(length, 1)) ** 2)
            s = amp * np.exp(-(a / w) ** 2)
            better = s > spike
            spike = np.where(better, s, spike)
            off = np.where(better, np.abs(a) / w, off)
        I = bright * tw * spike * (0.4 + 0.6 * np.exp(-rxz / 700))
        fr += perc(I)[:, None] * fringe(off)

        # halo: the star's glow on the roof nearest to it, by true 3-D distance
        halo = bright * 0.5 * np.exp(-(d3 / 300) ** 2) * smoothstep(8, 18, t)
        fr += light(GOLD, halo)

        # the travellers' lanterns
        for j, (a0, a1, t0, t1) in enumerate(trips):
            if t < t0 - 1:
                continue
            u = smoothstep(t0, t1, t) * 0.25 + 0.75 * np.clip((t - t0) / (t1 - t0), 0, 1)
            p = lerp(a0, a1, u)
            gait = 1 + 0.18 * sway(t)[j]
            e = keys(t, [(t0 - 1, 0), (t0, 0.6), (t1, 0.6), (t1 + 1.5, 0.35), (58, 0.35), (63, 0)])
            bob = 1.5 * np.sin(2 * np.pi * 1.1 * t + j)
            fr += light(TRAVELLERS[j], e * gait * np.exp(-((x - p - bob) / 5) ** 2))
            fr += light(TRAVELLERS[j], 0.35 * e * np.exp(-((x - p) / 22) ** 2))

        # arrival: the porch fills with light that spills round the corners and along the wings
        g = keys(t, [(47.5, 0), (49.5, 1), (55, 0.8), (63.5, 0)])
        if g > 0:
            spread = 60 + 900 * smoothstep(47.5, 56, t)
            fr += light(GLORY, 0.55 * g * np.exp(-(porch_dist / spread) ** 2) *
                        (0.85 + 0.15 * np.cos(porch_dist / 30 - 3 * t)))
    return out
