"""Ghost Dog: an all-night loop. Pale blue wisps drift both ways along the roof, and a little ghost dog
plays among them: a warm orange nose that wanders, darts, doubles back and sniffs about, trailing a
faint white tail. The nose's path is a sum of sines that repeat a whole number of times per loop, so
the loop has no seam."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, nframes, looped

CODE = 'NM22'
TITLE = 'Ghost Dog'
KIND = 'ambient'
DESCRIPTION = ('Pale wisps drift along the roof while a little ghost dog plays among them: a glowing orange '
               'nose that wanders, darts and doubles back, with a faint white tail behind it.')

GHOST = hexc('#a8c4ff')
TAIL = hexc('#eef2ff')
NOSE = hexc('#ff4a10')
LOOP = 150.0


def blob(x, c, w):
    return np.exp(-((x - c) / w) ** 2)


def _nose(G, rng):
    """The nose's path distance at time t (a sum of sines that repeat a whole number of times per loop),
    and the phase of its sniffing."""
    L = G.length
    w = 2 * np.pi / LOOP
    cyc = np.array([2, 5, 9])
    amp = np.array([0.6, 0.28, 0.12])
    ph = rng.uniform(0, 2 * np.pi, 3)
    sniff = rng.uniform(0, 2 * np.pi)

    def nose(t):
        return L / 2 + 0.4 * L * (amp * np.sin(cyc * w * t + ph)).sum()
    return nose, sniff


def render(G, seed=43):
    rng = np.random.default_rng(seed)
    d = G.pd[G.path]
    w = 2 * np.pi / LOOP
    nose, sniff = _nose(G, rng)

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        for f in range(len(out)):
            t = f * DT
            wisp = (0.13 + 0.05 * np.sin(2 * np.pi * d / 330 - 5 * w * t) +
                    0.04 * np.sin(2 * np.pi * d / 170 + 3 * w * t + 1.3) +
                    0.03 * np.sin(2 * np.pi * d / 95 - 11 * w * t + 0.4))
            n = nose(t)
            tail = np.zeros(G.N)
            for j in range(1, 13):
                tail = np.maximum(tail, 0.22 * (1 - j / 13) * blob(d, nose(t - 0.14 * j), 14))
            glow = 0.38 * (1 + 0.1 * np.sin(17 * w * t + sniff)) * blob(d, n, 9)
            halo = 0.14 * blob(d, n, 55)
            fr = (perc(wisp)[:, None] * GHOST + perc(tail)[:, None] * TAIL +
                  perc(glow)[:, None] * NOSE + perc(halo)[:, None] * NOSE)
            out[f][G.path] = fr
        return out
    return looped(draw, LOOP, floor=(0.08, GHOST))


# ---- music: an all-night loop, playful and quiet. A soft pad drifts through five chords like the wisps;
# the nose is a music box that steps up the scale while it runs right and down while it runs left, a note
# for every stretch of roof it covers, panned where it is, and a little pizzicato yip each time it doubles
# back. ----

SECTION = LOOP / 5
PADS = [('D3', 'A3', 'F4'), ('G2', 'D3', 'Bb3'), ('Bb2', 'F3', 'D4'), ('F2', 'C3', 'A3'), ('A2', 'E3', 'C#4')]
SCALE = ['D4', 'E4', 'F4', 'G4', 'A4', 'Bb4', 'C5', 'D5']     # the nose's steps
STEP = 140.0                                                    # roof travelled per note


def score(M, G):
    from pixelhome.audio import note as n
    rng = np.random.default_rng(143)
    order = np.argsort(G.pd)
    ds, xs = G.pd[order], G.pos[order, 0]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, from the street
        return float(0.8 * (2 * (np.interp(d, ds, xs) - x0) / (x1 - x0) - 1))

    pad = M.synth('Pads/Ghost Pad')
    box = M.synth('Plucks/Magic Music Box')
    pizz = M.sampler('Strings/Solo Violin/Pizz/*.wav')
    for name, gain, rev in (('pad', 0.36, 0.45), ('nose', 0.264, 0.45), ('yip', 0.192, 0.4)):
        M.bus(name, gain=gain, reverb=rev)

    notes = [(k * SECTION, n(m), 50, SECTION + 3) for k, ch in enumerate(PADS) for m in ch]
    M.add('pad', pad.render(notes, LOOP + 10), 0.0)

    nose, _ = _nose(G, np.random.default_rng(43))
    tt = np.arange(0, LOOP, 0.02)
    pos = np.array([nose(t) for t in tt])
    vel = np.gradient(pos, tt)
    deg, run = 0, 0.0
    for i in range(1, len(tt)):
        run += abs(pos[i] - pos[i - 1])
        if np.sign(vel[i]) != np.sign(vel[i - 1]) and vel[i] != 0:    # it doubles back
            p = pan_at(pos[i])
            M.add('yip', pizz.play(n('A4'), 70), tt[i], 1.0, p)
            M.add('yip', pizz.play(n('D5'), 64), tt[i] + 0.11, 1.0, p)
            run = 0.0
        if run >= STEP:
            run -= STEP
            deg = int(np.clip(deg + (1 if vel[i] > 0 else -1), 0, len(SCALE) - 1))
            v = int(np.clip(30 + abs(vel[i]) / 4, 30, 62))
            M.add('nose', box.render([(0.0, n(SCALE[deg]), v, 0.3)], 3.0), tt[i], 1.0, pan_at(pos[i]))
