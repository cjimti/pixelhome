"""Prelude: the opera's 136 bars of E flat major, folded into eighty seconds. Out of darkness the double
basses' low E flat glows up from the back of the porch (the bottom of the river) until the whole roof is a dim
indigo, and the bassoons' B flat adds a slow teal swell. Eight horns enter in canon, each with the Nature motif
(the rising E flat arpeggio, Donington 1), and each opens a bloom of light from its own place on the house that
widens note by note as the arpeggio climbs, so the river fills horn by horn. Then the water starts to move:
cellos, violas and violins take up the flowing Rhine figure (Donington 2) in turn, each a train of waves along
the roofline whose crests brighten as the figure climbs and dim as it falls; the violins' sixteenths throw foam
and woodwinds add glints. The whole orchestra surges, all eight horns sound the motif together twice over the
full flood, the last crest rolls out from the porch to both ends of the house, and the key turns to A flat as
the curtain rises: sunlit water, and three silver glints where the Rhinemaidens will be.

compose() holds every note; render() lights the house from it and score() plays the same list."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, colormap
from pixelhome.leitmotifs import play, melody

CODE = 'RG01'
TITLE = 'Prelude'
KIND = 'show'
DESCRIPTION = ('The Rhine before the story begins: one long E flat chord rises out of the dark, eight horns '
               'bloom across the house one after another, and the river starts to flow, faster and brighter, '
               'until the curtain rises.')
VOICEOVER = ('Das Rheingold. Before the gods, before the gold, before anyone wanted anything, '
             'there was only the river, and one deep note.')

BAR = 2.0                                   # a bar of 6/8
BEAT = BAR / 3                              # a quarter note: the motif tables count in these
T_FIFTH = 6.0                               # the bassoons' B flat over the basses' E flat
HORNS = [10.0 + 4.0 * k for k in range(8)]  # eight horns in canon, one every two bars
T_CELLI, T_VIOLAS, T_VIOLINS, T_WINDS = 26.0, 34.0, 42.0, 50.0
T_SURGE = 58.0                              # all the horns together, twice
T_CREST = 74.0                              # the last surge rolls out from the porch
T_AB = 76.0                                 # A flat: the curtain rises
D = 80.0

ORIGINS = [('Porch Front', 0.5), ('Left', 0.55), ('Right', 0.45), ('Porch Left', 0.5), ('Porch Right', 0.5),
           ('Left', 0.15), ('Right', 0.85), ('Porch Front', 0.5)]
FIG = [m for b, _, m in melody('rhine') if b < 6]      # the flowing figure: 24 sixteenths, E flat 4 to G5 and back
WIND_TONES = ['Bb4', 'Eb5', 'G5', 'Bb5', 'G5', 'Eb5', 'Bb4', 'G4']

DEEP = hexc('#0c1c8c')
TEAL = hexc('#0a7c8a')
HORN = colormap([(39, hexc('#0a28c8')), (51, hexc('#0078d0')), (60, hexc('#00c8b8')), (67, hexc('#50ffc0'))])
CELLI = hexc('#1050e0')
VIOLAS = hexc('#00b8a0')
VIOLINS = hexc('#40f0e8')
FOAM = hexc('#e0fff8')
GLINT = hexc('#fff0a0')
SUN = hexc('#30f090')
SILVER = hexc('#d8f0ff')
CREST = hexc('#a0fff0')


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose(G):
    """Every note: (time, seconds, midi, velocity, part, k). k is the horn (0-7), the step of the figure, or for
    the winds the path distance of the glint they make."""
    N = []
    for k, t0 in enumerate(HORNS):
        for t, m, v, d in play('nature', t0, BEAT, 12 * (k % 2), 52 + 7 * k):
            N.append((t, d, m, v, 'horn', k))
    for t0, v in ((T_SURGE, 100), (T_SURGE + 4 * BAR, 118)):
        for tr in (0, 12, 24):
            for t, m, _, d in play('nature', t0, BEAT, tr, v):
                N.append((t, d, m, v, 'tutti', tr))

    def figure(part, t0, step, tr, v0, v1, phase=0):
        n = int(round((T_AB - t0) / step))
        for i in range(n):
            t = t0 + i * step
            k = (i + phase) % 24
            N.append((t, step, FIG[k] + tr, int(v0 + (v1 - v0) * i / n), part, k))

    figure('celli', T_CELLI, BEAT / 2, -24, 48, 116)
    figure('violas', T_VIOLAS, BEAT / 2, -12, 46, 114, 12)
    figure('violins', T_VIOLINS, BEAT / 4, 0, 44, 112)
    rng = np.random.default_rng(7)
    front = np.concatenate([G.pd[G.seg[s]] for s in ('Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right')])
    for i, t in enumerate(np.arange(T_WINDS, T_CREST, 1.5 * BEAT)):
        N.append((float(t), 1.4 * BEAT, note(WIND_TONES[i % len(WIND_TONES)]), 70 + 2 * i, 'winds',
                  float(rng.choice(front))))
    return sorted(N, key=lambda e: e[0])


def render(G, seed=1):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    org = np.array([at(G, s, u) for s, u in ORIGINS])
    N = compose(G)

    horn = [[e for e in N if e[4] == 'horn' and e[5] == k] for k in range(8)]
    tut = [e for e in N if e[4] == 'tutti' and e[5] == 12]
    layers = []
    for part, lam, speed, sharp, col, lo in (('celli', 520.0, 120.0, 1.4, CELLI, 39),
                                             ('violas', 270.0, 170.0, 2.0, VIOLAS, 51),
                                             ('violins', 120.0, 240.0, 3.0, VIOLINS, 63)):
        ev = [e for e in N if e[4] == part]       # the figure spans E flat to G an octave and a third up
        layers.append(dict(on=np.array([e[0] for e in ev]), m=np.array([e[2] for e in ev]),
                           v=np.array([e[3] for e in ev]), lam=lam, speed=speed, sharp=sharp, col=col, lo=lo,
                           hi=lo + 28))
    winds = [e for e in N if e[4] == 'winds']
    vn_on = layers[2]['on']

    # the river runs faster as the music surges: integrate the speed so the waves never jump
    ts = np.arange(F) * DT
    pace = 1 + 0.9 * smoothstep(T_SURGE - 8, T_CREST, ts)
    travel = np.cumsum(pace) * DT

    def bloom(o, r, t):
        u = np.abs(d - o)
        ring = 0.82 + 0.18 * np.cos(2 * np.pi * (u - 70 * t) / 90)
        r = max(r, 1.0)
        return smoothstep(r, 0.5 * r, u) * ring

    foam = np.zeros(G.N)
    fi = 0
    for f in range(F):
        t = ts[f]
        fr = np.zeros((G.N, 3))
        live = 1 - smoothstep(T_AB, T_AB + 1.6, t)          # the depths give way to the surface

        # the basses' E flat: up from the bottom of the river until it covers the roof, then breathing
        rad = 1600 * smoothstep(0, 6.5, t) ** 0.8
        bed = 0.24 * smoothstep(rad, rad - 350, np.abs(d - pf)) * (1 + 0.1 * np.sin(2 * np.pi * 0.07 * t))
        fr += light(DEEP, bed * (0.4 + 0.6 * live))
        # the bassoons' B flat: one long slow teal swell
        fifth = 0.2 * smoothstep(T_FIFTH, T_FIFTH + 3, t) * (0.5 + 0.5 * np.cos(2 * np.pi * (d / 900 - 0.05 * t)))
        fr += light(TEAL, fifth * live)

        # the horns: each note of a horn's arpeggio widens its bloom; after its statement it settles to a glow
        for k, ev in enumerate(horn):
            if t < ev[0][0]:
                continue
            j = max(i for i, e in enumerate(ev) if e[0] <= t)
            tj = ev[j][0]
            r0, r1 = 60 + 45 * max(j - 1, 0), 60 + 45 * j
            r = r0 + (r1 - r0) * smoothstep(tj, tj + 0.35, t) if j else r1 * smoothstep(tj, tj + 0.35, t)
            end = ev[-1][0] + ev[-1][1]
            b = (0.3 + 0.4 * np.exp(-(t - tj) / 0.45)) * (0.55 + 0.45 * ev[j][3] / 101)
            if t > end:
                b = 0.17 + (b - 0.17) * np.exp(-(t - end) / 3.0)
            fr += light(HORN(ev[j][2]), b * bloom(org[k], r, t) * live)

        # all eight together: every origin blooms at once and the blooms grow wide enough to meet
        if tut and t >= tut[0][0]:
            j = max(i for i, e in enumerate(tut) if e[0] <= t)
            tj, st = tut[j][0], j % 7
            first = tut[j - st][0]
            r0 = 110 + 70 * (st - 1) if st else 0
            r = r0 + (110 + 70 * st - r0) * smoothstep(tj, tj + 0.3, t)
            b = (0.36 + 0.42 * np.exp(-(t - tj) / 0.4)) * smoothstep(first, first + 0.3, t) * tut[j][3] / 118
            col = HORN(tut[j][2])
            glow = np.max([bloom(o, r, t) for o in org[:7]], axis=0)
            fr += light(col, b * glow * live)

        # the strings: wave trains along the roofline, brighter as their figure climbs
        for ly in layers:
            if not len(ly['on']) or t < ly['on'][0]:
                continue
            i = int(np.searchsorted(ly['on'], t, side='right')) - 1
            hgt = (ly['m'][i] - ly['lo']) / (ly['hi'] - ly['lo'])
            accent = 1 + 0.4 * np.exp(-(t - ly['on'][i]) / 0.1)
            amp = smoothstep(ly['on'][0], ly['on'][0] + 2.5, t) * ly['v'][i] / 110
            w = (0.5 + 0.5 * np.cos(2 * np.pi * (d - ly['speed'] * travel[f]) / ly['lam'])) ** ly['sharp']
            ly['w'] = w
            fr += light(ly['col'], (0.2 + 0.7 * hgt) * accent * amp * w * live)

        # foam off the violins' sixteenths, near the crests of their waves
        foam *= np.exp(-DT / 0.14)
        while fi < len(vn_on) and vn_on[fi] <= t:
            idx = rng.choice(G.N, 12, replace=False)
            foam[idx] += 0.5 + 0.5 * layers[2]['v'][fi] / 108
            fi += 1
        if 'w' in layers[2]:
            fr += light(FOAM, foam * (0.25 + 0.75 * layers[2]['w']) * live)

        # woodwind glints
        for tn, dn, m, v, _, pos in winds:
            if tn <= t < tn + 2.0:
                g = np.exp(-((d - pos) / 22) ** 2) * np.exp(-(t - tn) / 0.55) * v / 100
                fr += light(GLINT, 0.9 * g * live)

        # the crest rolls out from the porch to both ends; behind it the whole river is lit
        if T_CREST <= t:
            rf = 1550 * smoothstep(T_CREST, T_AB + 0.3, t)
            u = np.abs(d - pf)
            c = np.exp(-((u - rf) / 110) ** 2) * (1 - smoothstep(T_AB + 0.2, T_AB + 1.4, t))
            behind = 0.5 * smoothstep(rf, rf - 200, u) * live
            fr += light(CREST, 0.95 * c) + light(VIOLINS, behind)

        # A flat: the surface, sunlit, and three silver glints where the Rhinemaidens will appear
        if t >= T_AB:
            up = smoothstep(T_AB, T_AB + 1.4, t) * (1 - smoothstep(D - 1.2, D, t))
            sw = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - 0.35 * (t - T_AB)))
            fr += light(SUN, up * (0.18 + 0.2 * sw))
            for k, (s, u) in enumerate((('Left', 0.5), ('Porch Front', 0.5), ('Right', 0.5))):
                tw = 0.6 + 0.4 * np.sin(2 * np.pi * (1.3 + 0.4 * k) * t + k)
                start = T_AB + 0.8 + 0.5 * k
                fr += light(SILVER, up * smoothstep(start, start + 0.6, t) * tw * 0.8 *
                            np.exp(-((d - at(G, s, u)) / 20) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR
    n = note
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    for name, gain, rev in (('bass', 0.16, 0.18), ('horns', 0.14, 0.38), ('strings', 0.13, 0.32),
                            ('winds', 0.11, 0.4), ('harp', 0.2, 0.45)):
        M.bus(name, gain=gain, reverb=rev)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=1.5, fall=1.5, gain=1.0):
        """A note sustained from t0 to t1 (and released over `fall`): overlapping windows of its sample."""
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            env = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * env, t, gain, pan)
            t += step

    pf = at(G, 'Porch Front', 0.5)
    org = [at(G, s, u) for s, u in ORIGINS]
    hold('bass', cb, n('Eb1'), 0.0, T_AB + 0.3, 92, 0.0, rise=9.0)
    hold('bass', cb, n('Eb2'), 3.0, T_AB + 0.3, 70, 0.1, rise=8.0)
    hold('bass', bsn, n('Bb1'), T_FIFTH, T_AB + 0.3, 78, -0.1, rise=3.0, gain=0.8)
    hold('bass', tuba, n('Eb2'), T_SURGE, T_AB + 0.3, 96, 0.0, rise=6.0, gain=0.7)
    hold('horns', tbn, n('Bb2'), T_SURGE, T_AB + 0.3, 90, -0.3, rise=6.0, gain=0.5)
    hold('horns', tbn, n('Eb3'), T_SURGE + 4, T_AB + 0.3, 90, 0.3, rise=6.0, gain=0.5)

    for t, d, m, v, part, k in compose(G):
        if part == 'horn':
            M.add('horns', horn.play(m, v, dur=d, release=0.6), t, 1.0, pan_at(org[k]))
        elif part == 'tutti':
            M.add('horns', horn.play(m, v, dur=d, release=0.6), t, 0.75, {0: -0.5, 12: 0.0, 24: 0.5}[k])
            if k == 0:
                M.add('horns', tbn.play(m, v - 6, dur=d, release=0.5), t, 0.5, -0.2)
        elif part == 'celli':
            M.add('strings', vc.play(m, v, dur=d * 1.6, release=0.2), t, 1.0, -0.45)
        elif part == 'violas':
            M.add('strings', va.play(m, v, dur=d * 1.6, release=0.2), t, 0.9, 0.35)
        elif part == 'violins':
            M.add('strings', vn.play(m, v, dur=d * 1.8, release=0.15), t, 0.75, -0.6 + 1.2 * (m - 63) / 28)
        elif part == 'winds':
            M.add('winds', fl.play(m, v, dur=d, release=0.4), t, 0.8, pan_at(k))
            M.add('winds', cl.play(m - 12, v - 10, dur=d, release=0.4), t, 0.6, pan_at(k))

    # A flat: the curtain rises on the river's surface; a flute remembers how Woglinde will begin
    for m, g, p in (('Ab1', 1.0, 0.0), ('Ab2', 0.7, 0.0)):
        hold('bass', cb, n(m), T_AB, D, 84, p, rise=0.4, fall=1.0, gain=g)
    hold('bass', tuba, n('Ab1'), T_AB, T_AB + 2.0, 100, 0.0, rise=0.2, fall=1.0, gain=0.6)
    for m, p in (('Eb3', -0.4), ('Ab3', 0.0), ('C4', 0.4)):
        hold('horns', horn, n(m), T_AB, D, 88, p, rise=0.3, fall=1.2, gain=0.7)
    for m, p in (('Ab4', -0.5), ('C5', 0.0), ('Eb5', 0.5)):
        hold('strings', trem, n(m), T_AB, D, 70, p, rise=0.6, fall=1.2, gain=0.6)
    gl = [x for x in range(n('Ab2'), n('Eb6') + 1) if x % 12 in (8, 0, 3)]
    for i, m in enumerate(gl):
        M.add('harp', harp.play(m, 96 - i), T_AB + i * 1.5 / len(gl), 1.0, -0.8 + 1.6 * i / len(gl))
    M.add('winds', fl.play(n('F5'), 74, dur=0.9, release=0.3), T_AB + 2.2, 0.9, pan_at(pf))
    M.add('winds', fl.play(n('Eb5'), 70, dur=1.2, release=0.6), T_AB + 2.2 + BEAT * 1.5, 0.9, pan_at(pf))
