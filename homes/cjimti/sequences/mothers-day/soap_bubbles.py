"""Soap Bubbles: Bubbles as true spheres in the house's 3-D space, lit where their shell crosses
the roofline and coloured by thin-film interference (film thickness per pixel, so each ring shows
the pinks, greens and golds of a real soap film, thinning as it ages). A big first bubble is blown
on the porch and floats toward the street, its shell sliding down both porch sides onto the wings.
Then the kids blow streams: small bubbles rise up through the roof plane, so each one appears as a
point, opens into a ring and closes again. A giant bubble swells from the porch until the whole
house is inside it, wobbles, and pops the way films do, the hole racing round from one point.
A last little bubble lands on the porch and goes pip."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, Flicker, nframes

CODE = 'MO10'
TITLE = 'Soap Bubbles'
KIND = 'show'
DESCRIPTION = 'Bubbles as real spheres in 3-D, coloured by thin-film interference: one floats from the porch to the street, streams rise through the roof, a giant one swallows the house and pops.'

WHITE = hexc('#fff4ec')
SPRAY = hexc('#e8f0ff')
N_FILM = 1.33
LAMBDA = np.array([640.0, 540.0, 455.0])


def film(tau):
    """Reflected colour of a soap film of thickness tau (nm), softened toward pastel."""
    tau = np.asarray(tau, float)[..., None]
    r = np.sin(2 * np.pi * N_FILM * tau / LAMBDA) ** 2
    return 0.35 + 0.65 * r


def render(G, seed=30):
    rng = np.random.default_rng(seed)
    D = 68.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    P = G.pos
    WAND = np.array([-20.0, 150.0, -500.0])
    HC = np.array([16.0, 150.0, -390.0])
    tw = Flicker(rng, n, 2, 6)

    def shell(c, r, w, tau0, swirl, t, I):
        d = np.linalg.norm(P - c, axis=1)
        phi = np.arctan2(P[:, 2] - c[2], P[:, 0] - c[0])
        tau = tau0 * (1 + 0.25 * np.sin(2 * phi + swirl * t) + 0.1 * np.sin(5 * phi - 0.7 * t))
        ring = np.exp(-((d - r) / w) ** 2)
        inside = smoothstep(r + 2, r - 20, d) * 0.06
        return film(tau) * perc(I * (ring + inside))[:, None], d

    def spray_at(c, r, u, I):
        d = np.linalg.norm(P - c, axis=1)
        ring = np.exp(-((d - r - 500 * u) / 25) ** 2) * np.exp(-u / 0.25)
        return light(SPRAY, I * ring * np.clip(tw(u * 7) + 0.5, 0, 1))

    # streams of small bubbles rising through the roof plane
    small = []
    for k in range(30):
        t0 = 19 + k * 0.7 + rng.uniform(-0.3, 0.3)
        node = rng.integers(n)
        r = rng.uniform(40, 110)
        c0 = P[node] + np.array([rng.uniform(-30, 30), -r - 10, rng.uniform(-30, 30)])
        vel = np.array([rng.uniform(-25, 25), rng.uniform(22, 38), rng.uniform(-10, 25)])
        life = (2 * r + 20) / vel[1] * rng.uniform(0.5, 1.1)
        small.append((t0, c0, vel, r, life, rng.uniform(380, 560)))

    for f in range(len(out)):
        t = f * DT
        fr = np.zeros((n, 3))
        night = keys(t, [(0, 0), (2, 0.05), (64, 0.05), (68, 0)])
        fr += light(hexc('#8a70e0'), night * np.ones(n))

        # 1. the first bubble: blown, released, floats to the street, pops
        if 1.5 < t < 22:
            r = keys(t, [(1.5, 0), (7.5, 235)]) * (1 + 0.03 * np.sin(2 * np.pi * 1.7 * t) * smoothstep(10, 8, t))
            c = WAND if t < 8 else WAND + np.array([8 * (t - 8), 0, 34 * (t - 8)]) * smoothstep(8, 9, t)
            tau = keys(t, [(1.5, 650), (20, 300)])
            if t < 20.0:
                img, _ = shell(c, r, 8, tau, 0.8, t, 0.75 * smoothstep(1.5, 3, t))
                fr += img
            else:
                fr += spray_at(c, r, t - 20.0, 0.8)

        # 2. streams
        for t0, c0, vel, r, life, tau0 in small:
            u = t - t0
            if 0 < u < life + 0.5:
                c = c0 + vel * u
                if u < life:
                    img, _ = shell(c, r, 8, tau0 * (1 - 0.35 * u / life), 1.2, t, 0.7)
                    fr += img
                else:
                    cut = np.sqrt(max(r * r - (c[1] - 150) ** 2, 1.0))
                    fr += spray_at(np.array([c[0], 150, c[2]]), cut, u - life, 0.6)

        # 3. the giant bubble swallows the house
        TP = 57.0
        if 41 < t < TP + 2.5:
            R = keys(t, [(41, 0), (51, 700), (TP, 700)])
            wob = 0.035 * smoothstep(50, 52, t)
            d = np.linalg.norm(P - HC, axis=1)
            phi = np.arctan2(P[:, 2] - HC[2], P[:, 0] - HC[0])
            Rl = R * (1 + wob * np.sin(2 * phi + 2.2 * t) + 0.6 * wob * np.sin(3 * phi - 1.6 * t))
            tau = keys(t, [(41, 700), (TP, 360)]) * (1 + 0.3 * np.sin(phi + 0.5 * t) + 0.15 * np.sin(4 * phi - t))
            ringI = 0.8 * np.exp(-((d - Rl) / 14) ** 2)
            insideI = 0.17 * smoothstep(Rl + 5, Rl - 40, d)
            if t > TP:                              # the hole races round from the right free end
                phi0 = np.arctan2(P[G.path[-1], 2] - HC[2], P[G.path[-1], 0] - HC[0])
                ang = np.abs(np.angle(np.exp(1j * (phi - phi0))))
                front = (t - TP) * 2.6
                gone = ang < front
                rim = np.exp(-((ang - front) / 0.12) ** 2) * (front < np.pi + 0.3)
                ringI = ringI * ~gone
                insideI = insideI * ~gone
                fr += light(SPRAY, 0.9 * rim * smoothstep(Rl + 40, Rl - 200, d) * np.clip(tw(t) + 0.6, 0, 1))
            fr += film(tau) * perc(ringI + insideI)[:, None]

        # 4. a last little bubble lands on the porch, sits, and goes pip
        if 60 < t < 66.5:
            land = P[G.seg['Porch Front'][len(G.seg['Porch Front']) // 2]]
            yc = keys(t, [(60, 150 + 120), (62.5, 150 + 18)])
            c = np.array([land[0] + 20 * np.sin(0.8 * t), yc, land[2]])
            r = 34 * (1 + 0.04 * np.sin(2 * np.pi * 2.1 * t) * (t > 62.5))
            if t < 65.2:
                img, _ = shell(c, r, 5, keys(t, [(60, 520), (65.2, 260)]), 1.5, t, 0.75)
                fr += img
            else:
                fr += spray_at(np.array([c[0], 150, c[2]]), 25, t - 65.2, 0.8)
        out[f] = fr
    return out
