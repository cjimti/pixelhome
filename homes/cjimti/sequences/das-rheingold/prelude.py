"""Prelude: the opening of Das Rheingold. Out of darkness the double basses' low E flat glows up from the back
of the porch (the bottom of the river) until the whole roof is a dim indigo, and the bassoons' B flat adds a slow
teal swell. The horns enter in canon, each with the Nature motif (the rising E flat arpeggio), and each opens a
bloom of light from its own place on the house that widens note by note as the arpeggio climbs. Then the full
flood: the strings' flowing Rhine figure in wave trains along the roofline, crests brightening as it climbs, foam
off the violins and glints off the highest notes; the river runs faster as the whole orchestra surges up its last
scales, the crest rolls out from the porch to both ends of the house, and the key turns to A flat as the curtain
rises: sunlit water, three silver glints, and Woglinde's first "Weia! Waga!".

The music is Wagner's own: bars 1-5, 17-33 and 113-138 of the prelude (the drone, the horns' canon, the flood to
the curtain), timed bar by bar like Barenboim's 1991 Bayreuth recording (Solti's annotation has timing glitches
here). The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the pedal on basses,
tuba and bassoons, the canon on horns, the flood on strings with horns and woodwinds as it grows, the last chord
held as the curtain rises. Woglinde's first bar is from the printed vocal score (Klindworth, Schott; archive.org
dasrheingold00wagn2, p. 5) on oboe and flute. A cymbal swell carries the crest; a soft river rush under the depths
is pulled away once the flood is in the orchestra.

compose() holds every note; render() lights the house from it and score() plays the same list."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'RG01'
TITLE = 'Prelude'
KIND = 'show'
DESCRIPTION = ('The Rhine before the story begins: one long E flat chord rises out of the dark, eight horns '
               'bloom across the house one after another, and the river starts to flow, faster and brighter, '
               'until the curtain rises.')
VOICEOVER = ('Das Rheingold. Before the gods, before the gold, before anyone wanted anything, '
             'there was only the river, and one deep note.')

EX = excerpt(__file__)                      # bars 1-5, 17-33, 113-138, Barenboim 1991
S2, S3 = EX['segments'][1]['start'], EX['segments'][2]['start']


def bar_time(m):
    """When bar m starts in the excerpt."""
    return next(t for b, t in reversed(EX['bars']) if b == m)


T_FIFTH = S2 - 1.5                          # the bassoons' B flat over the basses' E flat
T_SURGE = bar_time(129)                     # the last scales: the whole orchestra surges
T_CREST = bar_time(135)                     # the crest rolls out from the porch
T_AB = bar_time(137)                        # A flat: the curtain rises
D = round(EX['seconds'] + 2.5, 3)           # the last chord rings on
WOGLINDE = [(0, 2, 'F5'), (2, 1, 'Eb5'), (3, 2, 'C5'), (5, 1, 'Bb4')]     # "Weia! Waga!", in eighths of 6/8

ORIGINS = [('Porch Front', 0.5), ('Left', 0.55), ('Right', 0.45), ('Porch Left', 0.5), ('Porch Right', 0.5),
           ('Left', 0.15), ('Right', 0.85), ('Porch Front', 0.5)]

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


def bar_of(t):
    """The bar a time falls in (the excerpt's three passages share no bar numbers)."""
    return max(b for b, bt in EX['bars'] if bt <= t + 1e-6 and (t < S2 or b >= 17) and (t < S3 or b >= 113))


def compose(G):
    """Every note of the excerpt: (time, seconds, midi, velocity, part, k). The pedal is 'bass'; in the canon the
    right hand is the horns ('horn', k = which horn, by when it enters); in the flood the right hand is the violins,
    the left hand's upper notes the violas and its lower the celli, the right hand's highest notes woodwind glints
    ('winds', k = the path distance of the glint), and the left hand's rising scales at the end all the horns
    together ('tutti'). Woglinde's first bar is 'voice'."""
    N = []
    rng = np.random.default_rng(7)
    front = np.concatenate([G.pd[G.seg[s]] for s in ('Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right')])
    for t, d, m, v, h in EX['notes']:
        b = bar_of(t)
        if t < S3 and (h == 1 or t < S2):
            N.append((t, d, m, v, 'bass', None))
        elif t < S3:
            N.append((t, d, m, v, 'horn', min(7, (b - 17) // 4 if b < 29 else 3 + (b - 29))))
        elif h == 1 and b >= 129:
            N.append((t, d, m, v, 'tutti', 12))
        elif h == 1:
            N.append((t, d, m, v, 'violas' if m >= 51 else 'celli', None))
        else:
            N.append((t, d, m, v, 'violins', None))
            if m >= 86:
                N.append((t, 0.6, m, v, 'winds', float(rng.choice(front))))
    e8 = (bar_time(138) - T_AB) / 6
    for x, n, name in WOGLINDE:
        N.append((T_AB + x * e8, n * e8, note(name), 72, 'voice', None))
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
    horn = [ev for ev in horn if ev]
    tut = [e for e in N if e[4] == 'tutti' and e[5] == 12]
    layers = []
    for part, lam, speed, sharp, col, lo in (('celli', 520.0, 120.0, 1.4, CELLI, 27),
                                             ('violas', 270.0, 170.0, 2.0, VIOLAS, 51),
                                             ('violins', 120.0, 240.0, 3.0, VIOLINS, 63)):
        ev = [e for e in N if e[4] == part]       # the figure spans E flat to G an octave and a third up
        layers.append(dict(on=np.array([e[0] for e in ev]), m=np.array([e[2] for e in ev]),
                           v=np.array([e[3] for e in ev]), lam=lam, speed=speed, sharp=sharp, col=col, lo=lo,
                           hi=lo + 28 if part != 'violins' else lo + 36))
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
    """Wagner's notes on the orchestra: the pedal on basses, tuba and bassoons, the canon on horns, the flood in full
    orchestra growing to the crest, the A flat chord held as the curtain rises, Woglinde's first bar on oboe."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    org = [at(G, s, u) for s, u in ORIGINS]
    o = Orchestra(M, level=2.1)
    N = compose(G)
    ring_on = lambda t, d: D - 0.4 - t if t >= T_AB - 0.01 else d          # the last chord rings to the end
    for t, d, m, v, part, k in N:
        d = ring_on(t, d)
        if part == 'bass':                                              # the pedal, swelling slowly in
            if m <= 34:
                o.play('basses', m + 12, t, d, 96, 0.0, 0.7)
                o.play('tuba', m + 12, t, d, 70, 0.0, 0.45)
            else:
                o.play('bassoons', m, t, d, 84, -0.1, 0.6)
                o.play('cellos', m, t, d, 60, -0.2, 0.35)
        elif part == 'horn':                                            # the canon: each horn from its place
            o.play('horns', m, t, d * 1.2, 78, pan_at(org[k]), 0.5)
        elif part == 'voice':
            o.play('oboes', m, t, d, 92, pan_at(at(G, 'Porch Front', 0.5)), 0.8)
            o.play('flutes', m, t, d, 80, pan_at(at(G, 'Porch Front', 0.5)), 0.4)
    grow = lambda t: 0.45 + 0.55 * float(np.clip((t - S3) / (T_CREST - S3), 0, 1))
    flood = [n for n in tidy([n for n in EX['notes'] if n[0] >= S3 - 0.01])]
    flood = [[t, ring_on(t, d), m, v, h] + n[5:] for n in flood for t, d, m, v, h in [n[:5]]]

    def role(t, d, m, v, h):
        g = 0.7 + 0.9 * (grow(t) - 0.45) / 0.55                        # the flood grows into the crest
        if t >= T_AB - 0.01:                                            # A flat: horns and strings, softly
            return [('horns', 0, 10, 0.6), ('violins' if m >= 55 else 'cellos', 0, 0, 0.5)]
        if h == 0:                                                      # the Rhine figure: violins, flutes on top
            parts = [('violins', 0, 6, 0.8 * g), ('violas', -12, -6, 0.35 * g)]
            if m >= 79:
                parts.append(('flutes', 0, -4, 0.45 * g))
            return parts
        if d >= 0.3:                                                    # the left hand's long notes: horns
            parts = [('horns', 0, 8, 0.8 * g), ('cellos', 0, 0, 0.5 * g)]
            if m < 46:
                parts.append(('basses', 12 if m < 40 else 0, 0, 0.6 * g))
            if t >= T_SURGE:
                parts.append(('trombones', 0, 0, 0.5 * g))
            return parts
        return [('violas' if m >= 55 else 'cellos', 0, 8, 0.75 * g), ('horns', 0, -4, 0.3 * g * (t >= T_SURGE))]

    o.tutti(flood, size=grow, role=role, pan=lambda t, m: float(np.clip((m - 60) / 30, -0.7, 0.7)))
    # the stage: a soft rush of deep water under the depths, gone once the flood carries it; the crest swells
    o.wind(0.0, S3 + 3.0, level=lambda tt: 0.35 + 0.25 * np.clip(tt / S3, 0, 1), pan=0.0)
    o.hit('cymbal swell', T_CREST - 2.6, 96, gain=0.5)
    o.hit('timpani roll', T_SURGE, 90, pitch=-3, gain=0.35)
    o.hit('crash', T_CREST + 0.9, 70, gain=0.25)
    o.effects([(0.0, -9), (S2, -12), (S3, -20), (T_CREST - 3.0, -6), (T_AB, -8), (D, -10)])
