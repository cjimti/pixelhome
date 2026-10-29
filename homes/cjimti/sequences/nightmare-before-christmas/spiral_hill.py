"""Spiral Hill: an all-night loop. A deep blue night with a few slow stars and the curl of the hill as
a paler hump on the left wing. A full moon glows over the porch. Once a loop a lone figure walks in from
the free right end, along the right wing and round the porch corner to stand under the moon, stays there
a while (the moon brightens a little while he looks at it), and fades into the moonlight. Everything else is periodic
in the loop length, so the seam is clean."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, keys, nframes, looped

CODE = 'NB12'
TITLE = 'Spiral Hill'
KIND = 'ambient'
DESCRIPTION = ('A full moon over the porch and the curl of the hill on the left wing. Now and then a lone '
               'figure walks in along the right wing and stands under the moon a while.')

NIGHT = hexc('#0c1c70')
HILL = hexc('#2c50b0')
MOON = hexc('#d8e4ff')
FIGURE = hexc('#f2f4ff')
STAR = hexc('#b8ccff')
LOOP = 150.0
WALK, ARRIVE, LOOK, STAY, LOOKED, GONE = 10.0, 72.0, 82.0, 98.0, 100.0, 118.0   # the figure's evening


def blob(x, c, w):
    return np.exp(-((x - c) / w) ** 2)


def _stars(rng, n):
    """Pixels, whole cycles per loop and phases of the twinkling stars."""
    return rng.choice(n, 30, replace=False), rng.integers(4, 13, 30), rng.uniform(0, 2 * np.pi, 30)


def _walk(t, mid, L):
    """Where the figure is along the path, walking in from the free right end to the moon."""
    return keys(t, [(WALK, L - 15), (ARRIVE, mid + 55)])


def render(G, seed=41):
    rng = np.random.default_rng(seed)
    d = G.pd[G.path]
    mid = G.pd[G.seg['Porch Front']].mean()
    hill = G.pd[G.seg['Left']].mean()
    stars, scyc, sph = _stars(rng, G.N)
    w = 2 * np.pi / LOOP

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        for f in range(len(out)):
            t = f * DT
            bed = 0.13 + 0.025 * np.sin(d / 140 - 3 * w * t) * np.sin(d / 61 + 2 * w * t)
            curl = 0.1 * blob(d, hill, 150) * (1 + 0.2 * np.sin(2 * w * t + d / 90))
            # the figure: walks in, stands under the moon, fades into it
            fig = np.zeros(G.N)
            env = keys(t, [(WALK, 0), (WALK + 4, 1), (STAY, 1), (GONE, 0)])
            if env > 0:
                at = _walk(t, mid, G.length)
                fig = 0.36 * env * (1 + 0.08 * np.sin(2 * np.pi * 1.5 * t) * (t < ARRIVE)) * blob(d, at, 11)
            look = keys(t, [(ARRIVE, 0), (LOOK, 1), (LOOKED, 1), (GONE, 0)])
            moon = (0.3 + 0.03 * np.sin(3 * w * t) + 0.06 * look) * blob(d, mid, 110)
            tw = np.zeros(G.N)
            tw[stars] = 0.22 * np.clip(np.sin(scyc * w * t + sph), 0, 1) ** 4
            fr = (perc(bed)[:, None] * NIGHT + perc(curl)[:, None] * HILL + perc(moon)[:, None] * MOON +
                  perc(fig)[:, None] * FIGURE + perc(tw)[:, None] * STAR)
            out[f][G.path] = fr
        return out
    return looped(draw, LOOP, floor=(0.08, NIGHT))


# ---- music: an all-night loop, moonlit and alone. A ghostly pad moves through six slow chords; each star's
# twinkle is a faint music-box note where it is on the roof; while the figure walks, a far-off flute plays
# the occasion's THEME four times slower, following him along the house; when he looks at the moon the
# violins swell under it, a harp rolls up as he arrives and the theme's last bar falls away as he fades. ----

THEME = [                                   # (beat, note, beats): four bars, as in The Town Square
    (0, 'D4', 1), (1, 'F4', .5), (1.5, 'E4', .5), (2, 'D4', 1), (3, 'A3', 1),
    (4, 'Bb3', .5), (4.5, 'C4', .5), (5, 'D4', .5), (5.5, 'E4', .5), (6, 'F4', 1), (7, 'E4', 1),
    (8, 'G4', 1), (9, 'F4', .5), (9.5, 'E4', .5), (10, 'F4', 1), (11, 'D4', 1),
    (12, 'E4', .5), (12.5, 'C#4', .5), (13, 'A3', 1), (14, 'D4', 2)]
SECTION = LOOP / 6
PADS = [('D3', 'A3', 'F4'), ('Bb2', 'F3', 'D4'), ('G2', 'D3', 'Bb3'), ('D3', 'A3', 'F4'), ('Bb2', 'F3', 'D4'),
        ('A2', 'E3', 'C#4')]
SLOW = 2.0                                  # seconds a beat of the theme lasts on the hill


def score(M, G):
    from pixelhome.audio import note as n
    rng = np.random.default_rng(141)
    mid = G.pd[G.seg['Porch Front']].mean()
    order = np.argsort(G.pd)
    ds, xs = G.pd[order], G.pos[order, 0]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, from the street
        return float(0.8 * (2 * (np.interp(d, ds, xs) - x0) / (x1 - x0) - 1))

    pad = M.synth('Pads/Ghost Pad')
    box = M.synth('Plucks/Magic Music Box')
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    for name, gain, rev in (('pad', 0.216, 0.45), ('stars', 0.068, 0.7), ('flute', 0.203, 0.6),
                            ('swell', 0.121, 0.55), ('harp', 0.176, 0.55)):
        M.bus(name, gain=gain, reverb=rev)

    def hold(bus, inst, m, t0, t1, vel, gain, p, gr=4.0):
        """A note held from t0 to t1 by overlapping grains, swelling in and out at the ends."""
        win = np.sin(np.pi * np.arange(int(gr * 48000)) / (gr * 48000)) ** 2
        for g in np.arange(t0 - gr / 2, t1, gr / 2):
            fade = np.clip(min(g + gr / 2 - t0, t1 - g - gr / 2) / 6, 0, 1)
            if fade <= 0:
                continue
            s = inst.play(n(m), vel)[:, int(0.4 * 48000):int(0.4 * 48000) + len(win)]
            s = np.pad(s, ((0, 0), (0, len(win) - s.shape[1])))
            M.add(bus, s * win * np.sin(np.pi / 2 * fade) ** 2, g, gain, p)

    # the pad: one chord a section, each overlapping the next; the last rings round onto the first
    notes = [(k * SECTION, n(m), 52, SECTION + 3) for k, ch in enumerate(PADS) for m in ch]
    M.add('pad', pad.render(notes, LOOP + 10), 0.0)

    # the stars: a note at the top of some twinkles, from the chord of the moment
    stars, scyc, sph = _stars(np.random.default_rng(41), G.N)
    w = 2 * np.pi / LOOP
    for px, c, ph in zip(stars, scyc, sph):
        for k in range(int(c)):
            t = ((np.pi / 2 - ph) % (2 * np.pi) + 2 * np.pi * k) / (c * w)
            if t >= LOOP or rng.random() > 0.3:
                continue
            ch = PADS[int(t // SECTION)]
            m = n(ch[int(rng.integers(3))]) + 12 * int(rng.integers(1, 3))
            M.add('stars', box.render([(0.0, m, int(rng.integers(30, 55)), 0.4)], 4.0), t, 1.0,
                  pan_at(G.pd[G.path[px]]))

    # the walk: the theme, four times slower, on a far-off flute that follows him
    for t0, part in ((WALK + 2, THEME), (WALK + 2 + 16 * SLOW + 2, [x for x in THEME if x[0] >= 8])):
        b0 = part[0][0]
        for b, m, ln in part:
            t = t0 + (b - b0) * SLOW
            M.add('flute', flute.play(n(m), 70, dur=ln * SLOW * 0.95, release=0.8), t, 1.0,
                  pan_at(_walk(t, mid, G.length)))

    # he arrives and looks: a harp rolls up under the moon, the violins swell, and the last bar falls away
    for k, m in enumerate(('D3', 'A3', 'D4', 'F4', 'A4')):
        M.add('harp', harp.play(n(m), 70), ARRIVE + 0.3 * k, 1.0, pan_at(mid) + 0.1 * (k - 2))
    for m, p in (('D4', -0.2), ('A4', 0.2), ('E5', 0.0)):
        hold('swell', vln, m, ARRIVE, GONE, 55, 1.0, p)
    for k, (b, m, ln) in enumerate([x for x in THEME if x[0] >= 12]):
        M.add('harp', harp.play(n(m), 60 - 4 * k), LOOKED + 4 * k, 1.0, pan_at(mid))
