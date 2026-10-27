"""Reveille: Before dawn a bugler stands at the middle of the porch front. Every note of the call is a
ring of light expanding through real 3-D space from that spot; the higher the note, the farther its
ring carries, so the melody is drawn as reach. Then the sun comes up behind the house: its light is
computed through the atmosphere (Rayleigh-like extinction over the air mass), so the first light on
the back of the roof is deep red, warming to gold and then pale morning as it climbs, and the line of
first light sweeps forward from the back of the house toward the street."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, Flicker, nframes

CODE = 'VT08'
TITLE = 'Reveille'
KIND = 'show'
DESCRIPTION = ('A bugler on the porch plays the call, each note a ring of light carrying out across the house. '
               'Then dawn rises behind the roof, red to gold to morning, sweeping toward the street.')

NAVY = hexc('#1c34ff')
BRASS = hexc('#ffc070')
SKY = hexc('#5a7aff')

# bugle notes: 0 G4, 1 C5, 2 E5, 3 G5, 4 C6 ; durations in eighths
CALL = [(0, 1), (1, 0.5), (2, 0.5), (1, 1), (0, 1), (1, 0.5), (2, 0.5), (1, 1), (0, 1),
        (1, 0.5), (2, 0.5), (1, 1), (2, 1), (3, 2),
        (1, 0.5), (2, 0.5), (3, 1), (2, 1), (1, 1), (2, 0.5), (3, 0.5), (4, 2), (3, 1), (2, 1),
        (0, 1), (1, 0.5), (2, 0.5), (1, 1), (0, 1), (1, 0.5), (2, 0.5), (1, 1), (0, 1), (1, 2), (1, 3)]


def render(G, seed=28):
    rng = np.random.default_rng(seed)
    D = 78.0
    out = np.zeros((nframes(D), G.N, 3))
    P = G.pos
    pf = G.seg['Porch Front']
    bugler = np.array([P[pf, 0].mean(), 150.0, -569.0])
    dist = np.linalg.norm(P - bugler, axis=1)
    hush = Flicker(rng, G.N, 0.05, 0.25)
    # drifting cloud shadows: a smooth random field over the ground plane, sliding across the house
    cw = rng.normal(size=(5, 4))

    notes, t = [], 5.0
    eighth = 0.4
    for p, d in CALL:
        notes.append((t, p, d * eighth))
        t += d * eighth
    t_call = t

    # depth: 0 at the front of the wings, 1 at the very back of Side
    depth = np.clip((-P[:, 2] - 146) / 491, 0, 1)
    ext = np.array([0.25, 0.75, 1.9])            # extinction per air mass, red < green < blue
    sunc = np.array([1.0, 0.82, 0.62])           # sun colour above the air

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        night = keys(t, [(0, 0), (3, 0.14), (t_call + 4, 0.14), (t_call + 22, 0.0)])
        fr += light(NAVY, night * (1 + 0.12 * hush(t)))

        # the call
        for t0, p, d in notes:
            tau = t - t0
            if tau < 0 or tau > 3.0:
                continue
            reach = 220 + 210 * p
            r = 650 * tau
            ring = np.exp(-((dist - r) / (40 + 25 * p)) ** 2) * np.clip(1 - r / reach, 0, 1) ** 1.2
            held = np.exp(-(dist / 30) ** 2) * (tau < d) * (0.6 + 0.4 * np.sin(np.pi * min(1, tau / d)))
            fr += light(BRASS, 0.85 * ring + 0.7 * held)

        # dawn: sun elevation in degrees, rising behind the house; the back of the roof sees it first
        el = keys(t, [(t_call + 1, -7.0), (D - 6, 15.0)])
        eff = el + 5.5 * depth
        up = smoothstep(-1.2, 0.8, eff)                  # the line of first light
        h = np.radians(np.clip(eff, 0.3, 90))
        mass = 1 / (np.sin(h) + 0.15 * np.exp(-np.degrees(h) / 3))
        mass = np.clip(mass, 1, 40)
        T = np.exp(-ext[None, :] * mass[:, None] * 0.38)
        sunlight = sunc * T
        lvl = keys(t, [(t_call + 2, 0), (t_call + 30, 0.5), (D - 8, 0.56), (D, 0)])
        inten = lvl * up * (0.4 + 0.6 * np.clip(T[:, 1] / T[:, 1].max() if T[:, 1].max() > 0 else 0, 0, 1))
        col = sunlight / np.maximum(sunlight.max(1, keepdims=True), 1e-6)
        xs = (P[:, 0] - 38 * t) / 520.0
        zs = P[:, 2] / 380.0
        cloud = sum(cw[k, 0] * np.sin((k + 1) * 1.3 * xs + cw[k, 1] * 3) * np.cos((k % 2 + 1) * zs + cw[k, 2] * 3)
                    for k in range(5)) / 3.0
        shade = 1 - 0.45 * smoothstep(0.05, 0.6, cloud) * smoothstep(t_call + 18, t_call + 30, t)
        inten = inten * shade
        fr += perc(inten)[:, None] * col
        # skylight: scattered blue before the sun clears, strongest just before first light
        sky = keys(t, [(t_call - 4, 0), (t_call + 10, 0.2), (t_call + 30, 0.14), (D - 8, 0.08), (D, 0)])
        fr += light(SKY, sky * (0.6 + 0.4 * depth) * (1 - 0.6 * up))
    return out
