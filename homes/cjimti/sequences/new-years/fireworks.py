"""Fireworks: Real particle physics in 3-D around the house. Shells launch from the yard, burst
just above and beside the roof, and their stars fly out under gravity and air drag (closed-form
motion), cooling from white-hot to colour to ember. The roofline shows the slice of each burst that
crosses it, and every burst lights the whole roof by its distance: the near wing blazes, the far
porch catches a glow. Singles, mirrored pairs, a slow gold willow, and a finale."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, nframes

CODE = 'NY03'
TITLE = 'Fireworks'
KIND = 'show'
DESCRIPTION = 'Shells burst in 3-D around the house; stars fly under gravity and drag and the roof lights by distance from each burst. Pairs, a gold willow and a finale.'

G_ACC = 260.0        # gravity, layout units / s^2
WHITE = hexc('#fff4e4')
EMBER = hexc('#ff3008')
NAVY = hexc('#060c30')
PALETTE = {
    'gold': hexc('#ffa020'), 'red': hexc('#ff1830'), 'blue': hexc('#2050ff'), 'green': hexc('#20ff70'),
    'violet': hexc('#9030ff'), 'silver': hexc('#c8d8ff'), 'rose': hexc('#ff5090'), 'teal': hexc('#20e0d0'),
}

# (time, type, (x, y, z), colour, size)
PLAN = [
    (3.0, 'peony', (-760, 225, -700), 'gold', 0.8),
    (6.0, 'peony', (-400, 195, -60), 'red', 1.0),
    (9.0, 'ring', (420, 185, -120), 'teal', 1.0),
    (12.5, 'crossette', (-20, 225, -360), 'silver', 1.0),
    (14.5, 'peony', (650, 200, -420), 'gold', 0.7),
    (16.0, 'peony', (-640, 195, -380), 'violet', 1.0),
    (18.5, 'glitter', (700, 205, -200), 'silver', 0.9),
    (20.5, 'ring', (-640, 200, -150), 'rose', 0.9),
    (22.0, 'peony', (-300, 185, -350), 'green', 0.9),
    (24.0, 'peony', (320, 185, -400), 'rose', 0.9),
    (28.0, 'peony', (-420, 205, -80), 'blue', 1.0),
    (28.0, 'peony', (450, 205, -120), 'blue', 1.0),
    (31.5, 'ring', (-420, 195, -150), 'gold', 1.0),
    (31.5, 'ring', (450, 195, -190), 'gold', 1.0),
    (35.0, 'crossette', (-250, 205, -560), 'red', 0.9),
    (35.0, 'crossette', (210, 205, -560), 'red', 0.9),
    (38.5, 'glitter', (-20, 195, -120), 'silver', 1.1),
    (42.5, 'willow', (-20, 215, -400), 'gold', 1.25),
    (48.5, 'peony', (-20, 195, -720), 'rose', 0.7),
    (50.5, 'ring', (-20, 185, -380), 'silver', 0.9),
    (52.5, 'crossette', (-450, 195, -150), 'green', 0.8),
    (52.5, 'crossette', (480, 195, -190), 'green', 0.8),
    (55.0, 'peony', (-500, 185, -150), 'red', 0.9),
    (55.6, 'peony', (520, 185, -190), 'green', 0.9),
    (56.2, 'peony', (-20, 205, -500), 'blue', 0.9),
    (57.0, 'ring', (-600, 205, -500), 'violet', 1.0),
    (57.6, 'ring', (620, 205, -200), 'violet', 1.0),
    (58.4, 'crossette', (-300, 205, -250), 'gold', 1.0),
    (58.9, 'crossette', (300, 205, -280), 'gold', 1.0),
    (59.6, 'peony', (-650, 185, -150), 'rose', 0.9),
    (60.0, 'peony', (100, 185, -420), 'teal', 0.9),
    (60.4, 'peony', (-180, 195, -150), 'silver', 0.9),
    (60.9, 'peony', (380, 195, -190), 'red', 0.9),
    (61.5, 'glitter', (-450, 225, -300), 'silver', 1.0),
    (61.5, 'glitter', (450, 225, -300), 'silver', 1.0),
    (62.3, 'willow', (-400, 205, -200), 'gold', 1.0),
    (62.3, 'willow', (400, 205, -200), 'gold', 1.0),
    (63.2, 'peony', (-20, 215, -380), 'gold', 1.3),
    (64.0, 'glitter', (-20, 245, -250), 'silver', 1.3),
]


def make_shell(rng, t0, kind, c, colour, size):
    """Star initial velocities and per-star properties for one shell."""
    n = {'peony': 260, 'ring': 140, 'crossette': 70, 'glitter': 280, 'willow': 400}[kind]
    if kind == 'ring':
        a = np.linspace(0, 2 * np.pi, n, endpoint=False) + rng.normal(0, 0.02, n)
        tilt = rng.uniform(0.3, 0.9)
        d = np.stack([np.cos(a), np.sin(a) * np.cos(tilt), np.sin(a) * np.sin(tilt)], 1)
    else:
        d = rng.normal(size=(n, 3))
        d /= np.linalg.norm(d, axis=1, keepdims=True)
    speed = {'peony': 380, 'ring': 400, 'crossette': 300, 'glitter': 330, 'willow': 300}[kind] * size
    v0 = d * speed * rng.uniform(0.9, 1.05, (n, 1))
    drag = {'peony': 1.6, 'ring': 1.6, 'crossette': 1.4, 'glitter': 1.8, 'willow': 2.6}[kind]
    life = {'peony': 2.6, 'ring': 2.4, 'crossette': 0.75, 'glitter': 3.0, 'willow': 7.0}[kind]
    life = life * rng.uniform(0.75, 1.15, n)
    return dict(t0=t0, kind=kind, c=np.array(c, float), col=PALETTE[colour], v0=v0, k=drag, life=life,
                glit=rng.uniform(0, 1, n), size=size)


def star_pos(s, tau):
    """Closed-form position with linear drag and gravity."""
    k = s['k']
    g = np.array([0, -G_ACC, 0])
    e = (1 - np.exp(-k * tau)) / k
    return s['c'] + s['v0'] * e + g / k * (tau - e)


def star_vel(s, tau):
    k = s['k']
    g = np.array([0, -G_ACC, 0])
    return s['v0'] * np.exp(-k * tau) + g / k * (1 - np.exp(-k * tau))


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    D = 71.0
    out = np.zeros((nframes(D), G.N, 3))
    P = G.pos
    shells = []
    for t0, kind, c, colour, size in PLAN:
        s = make_shell(rng, t0, kind, c, colour, size)
        shells.append(s)
        if kind == 'crossette':                   # every star splits into four at the end of its life
            tau = s['life']
            kids = []
            for i in range(len(tau)):
                p = star_pos(dict(s, v0=s['v0'][i:i + 1]), tau[i])[0]
                v = star_vel(dict(s, v0=s['v0'][i:i + 1]), tau[i])[0]
                for j in range(4):
                    b = rng.normal(size=3)
                    b /= np.linalg.norm(b)
                    kids.append((t0 + tau[i], p, v + b * 160))
            kt = np.array([k[0] for k in kids])
            # group children by spawn time into a few batches for speed
            for tb in np.unique(np.round(kt, 1)):
                m = np.abs(np.round(kt, 1) - tb) < 1e-6
                sel = [kids[i] for i in np.where(m)[0]]
                n = len(sel)
                shells.append(dict(t0=tb, kind='kid', c=None, cs=np.array([k[1] for k in sel]),
                                   col=s['col'], v0=np.array([k[2] for k in sel]), k=1.8,
                                   life=rng.uniform(0.6, 1.0, n), glit=rng.uniform(0, 1, n), size=0.5))
    # comets: each shell rises from the yard toward its burst point over ~1.1 s
    comets = []
    for t0, kind, c, colour, size in PLAN:
        start = np.array([c[0] + rng.uniform(-40, 40), -20.0, max(c[2], -300) + 250])
        comets.append((t0 - 1.1, t0, start, np.array(c, float)))

    sig2 = 46.0 ** 2
    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        fr += light(NAVY, keys(t, [(0, 0), (2, 0.1), (D - 4, 0.1), (D, 0)]))
        # rising comets: a dim orange spark climbing, seen where it passes near the roof
        for ts, te, a, b in comets:
            if ts <= t < te:
                u = (t - ts) / (te - ts)
                p = a + (b - a) * np.array([u, 1 - (1 - u) ** 2, u])
                d2 = ((P - p) ** 2).sum(1)
                fr += light(EMBER, 0.5 * np.exp(-d2 / (70 ** 2)) + 0.06 / (1 + d2 / 300 ** 2))
        acc = np.zeros((G.N, 3))
        for s in shells:
            tau = t - s['t0']
            if tau < 0 or tau > s['life'].max():
                continue
            if s['kind'] == 'kid':
                k = s['k']
                g = np.array([0, -G_ACC, 0])
                e = (1 - np.exp(-k * tau)) / k
                pos = s['cs'] + s['v0'] * e + g / k * (tau - e)
            else:
                pos = star_pos(s, tau)
            age = tau / s['life']
            alive = age < 1
            # brightness: flash, sustain, fade; colour cools white -> colour -> ember
            b = np.where(alive, np.exp(-tau / 0.08) * 0.6 + np.clip(1 - age, 0, 1) ** 1.5, 0)
            if s['kind'] == 'glitter':
                b = b * (np.sin(2 * np.pi * (9 * tau + s['glit'] * 7) * (1 + s['glit'])) > 0.6) * 1.4
            if s['kind'] == 'willow':
                b = 1.2 * np.where(alive, np.clip(1 - age, 0, 1) ** 0.7, 0) * (0.75 + 0.25 * np.sin(tau * 30 + s['glit'] * 40))
            hot = np.exp(-tau / 0.18)
            cold = smoothstep(0.55, 1.0, age)
            col = WHITE * hot + s['col'] * (1 - hot)
            col = col[None, :] * (1 - cold[:, None]) + EMBER * cold[:, None]
            near = np.abs(pos[:, 1] - 150) < 110
            if near.any():
                d2 = ((P[:, None, :] - pos[None, near, :]) ** 2).sum(2)
                w = np.exp(-d2 / sig2)
                acc += w @ (col[near] * perc(np.clip(b[near], 0, 1.5))[:, None])
            # the whole roof catches the burst by distance (light from the shell's centre of mass)
            if s['kind'] != 'kid':
                cm = pos[alive].mean(0) if alive.any() else s['c']
                d2 = ((P - cm) ** 2).sum(1)
                tot = b.mean() * (0.9 + 1.4 * np.exp(-tau / 0.09)) * s['size']
                acc += (perc(np.clip(0.45 * tot, 0, 1)) / (1 + d2 / (190 ** 2)) ** 1.5)[:, None] * (0.6 * s['col'] + 0.4 * WHITE)
        fr += acc
    np.clip(out, 0, 1, out=out)
    return out
