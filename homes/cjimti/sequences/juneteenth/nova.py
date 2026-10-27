"""Nova: The Juneteenth flag drawn in plan view and rasterised through the roofline. A curved horizon
rises from the street, red below and blue beyond; a five-pointed star is born over the porch and
turns; its bursting twelve-point outline flares out through the wings again and again. Every shape is
a signed distance field in the x-z plane, so the house samples the flag wherever its pixels stand."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'JT02'
TITLE = 'Nova'
KIND = 'show'
DESCRIPTION = ('The Juneteenth flag laid over the house from above: a curved horizon rises from the street, '
               'a white star is born over the porch and turns, and its bursting outline flares out through the wings.')

BLUE = hexc('#1c34c8')
RED = hexc('#e0102a')
WHITE = hexc('#fff6f0')
DAWN = hexc('#ff9a50')


def star5(px, py, r, rf):
    """Signed distance to a five-pointed star (point toward +py), outer radius r, inner ratio rf."""
    k1 = np.array([0.809016994375, -0.587785252292])
    k2 = np.array([-k1[0], k1[1]])
    x, y = np.abs(px), py.copy()
    for k in (k1, k2):
        d = np.maximum(k[0] * x + k[1] * y, 0) * 2
        x, y = x - d * k[0], y - d * k[1]
    x = np.abs(x)
    y = y - r
    ba = np.array([-rf * k1[1], rf * k1[0] - 1])
    h = np.clip((x * ba[0] + y * ba[1]) / (ba @ ba), 0, r)
    dx, dy = x - ba[0] * h, y - ba[1] * h
    return np.hypot(dx, dy) * np.sign(y * ba[0] - x * ba[1])


def render(G, seed=2):
    rng = np.random.default_rng(seed)
    D = 64.0
    out = np.zeros((nframes(D), G.N, 3))
    X, Z = G.pos[:, 0], G.pos[:, 2]
    cx, cz = -22.0, -400.0                       # the star sits over the porch, between the wings
    hx, hz = -22.0, 1400.0                       # centre of the horizon circle, far out past the street
    dh = np.hypot(X - hx, Z - hz)
    ang = np.arctan2(X - cx, -(Z - cz))          # 0 = toward the back of the house
    rad = np.hypot(X - cx, Z - cz)
    tw = Flicker(rng, G.N, 0.5, 2.0)
    bursts = [27.0, 31.5, 35.0, 38.0, 40.6, 43.0, 45.2, 47.2]

    for f in range(len(out)):
        t = f * DT
        fr = out[f]

        # the horizon: a circle of radius R around a point beyond the street; red inside, blue beyond
        R = keys(t, [(0, 1400 - 200), (3, 1400 - 120), (15, 1400 + 400), (50, 1400 + 400 + 40),
                     (58, 1400 + 400), (63, 1400 + 300)])
        R = R + 18 * np.sin(2 * np.pi * t / 7) * smoothstep(16, 20, t)
        s = dh - R                                # <0 red ground, >0 blue sky
        fields = keys(t, [(0, 0), (3, 0.25), (15, 0.42), (24, 0.42), (26, 0.32), (50, 0.32),
                          (56, 0.45), (61, 0.45), (64, 0)])
        redI = fields * smoothstep(12, -12, s)
        blueI = fields * smoothstep(-12, 12, s) * (0.85 + 0.15 * tw(t))
        fr += light(RED, redI) + light(BLUE, blueI)
        line = np.exp(-(s / 10) ** 2) * keys(t, [(2, 0), (4, 1), (60, 0.8), (64, 0)])
        fr += light(lerp(DAWN, WHITE, smoothstep(4, 14, t)), 0.85 * line)

        # the star: born as a point, grows, turns
        size = keys(t, [(17, 0), (23, 330), (49, 330), (52, 420), (61, 0)])
        if size > 1:
            spin = 0.25 * (t - 17) + 0.6 * smoothstep(48, 60, t) * (t - 48)
            c, sn = np.cos(spin), np.sin(spin)
            px = (X - cx) * c - (-(Z - cz)) * sn
            py = (X - cx) * sn + (-(Z - cz)) * c
            d = star5(px, py, size, 0.42)
            inside = smoothstep(10, -10, d)
            edge = np.exp(-(d / 12) ** 2)
            corona = 0.35 * np.exp(-np.clip(d, 0, None) / 45) * (1 - inside)
            fr *= (1 - 0.9 * inside)[:, None]
            fr += light(WHITE, 0.6 * inside + 0.55 * edge) + light(DAWN, corona * smoothstep(17, 24, t))

        # the nova outline: a twelve-point burst ring flaring out from the star
        for tb in bursts:
            u = t - tb
            if 0 <= u < 3.5:
                Rb = 230 + 330 * u ** 0.8
                spikes = 1 + 0.22 * np.abs(np.cos(6 * (ang - 0.15 * tb))) ** 3 - 0.1
                rr = rad - Rb * spikes
                ring = np.exp(-(rr / 22) ** 2) * np.exp(-u / 1.2) * smoothstep(0, 0.15, u)
                wake = np.where(rr < 0, np.exp(rr / 120), 0) * 0.35 * np.exp(-u / 0.9)
                fr += light(WHITE, ring) + light(DAWN, wake)
        if 51.5 < t < 55:                                     # the last, biggest flare
            u = t - 51.5
            fr += light(WHITE, 0.85 * np.exp(-u / 0.35) * smoothstep(0, 0.08, u))
    return out
