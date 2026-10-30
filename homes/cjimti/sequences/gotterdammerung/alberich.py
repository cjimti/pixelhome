"""Alberich: night on the shore before the hall of the Gibichungs. The porch is the hall's doors, dark wood with a
torch glow at the seams; the wings and Side are the shore under a deep blue night and a cold moon; Hagen's spear
stands on Porch Front, a steel glint. Hagen, ultraviolet in black, sleeps sitting against the doors, and every
long swell of the prelude is his breath, a violet swell over the doors and out along the shore.

The music is Wagner's own, Act II as Solti's 1958 Vienna Philharmonic recording takes it: the prelude's swells
(bars 30-33), the moonlight surging and "Schläfst du, Hagen, mein Sohn?" (39-44), "den Ring gewinnen ... Schwörst
du mir's, Hagen, mein Sohn?" (158-163), and the dawn on the Rhine (219-226). The notes come from the Wagner Ring
Dataset's piano reduction (pixelhome/ring.py): the swells on horns and bassoons over murmuring low strings, the
Ring on clarinets and oboes, the three strokes before the oath on timpani and gong, the Curse on trombones and
tuba, the dawn on horns and then trumpets with cymbals as it blazes. The stage adds the river under the moon and
the dream rushing in and breaking apart.

The moonlight surges and his father comes to him in a dream: Alberich, red in his muddy halo, creeps in from the
free end of Right. His phrases roll red waves out over the house from where he stands, the sleeping son answers in
violet, and where they meet they crack white. On "den Ring gewinnen" the Ring races round the whole house as a
gold loop. Three hammer strokes demand an oath, harder each time, and each time the whole house flashes red and
the son's violet floods back over it; on the last the Curse slashes blood red from the doors out to both ends.

The dream breaks: Alberich shrinks back out of the free end of Right as a red comet, and dawn comes up red over
the shore in great surges from the river end, while Hagen rises and stands by his spear.

compose() tags every note; stage(), shore(), figure(), torches(), crowd() and sparks() are the shore, shared word
for word by Act II's scenes (GD15-GD21) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'GD15'
TITLE = 'Alberich'
KIND = 'show'
DESCRIPTION = ('Night on the shore. Hagen sleeps by his spear, and his father Alberich comes to him in a dream: red '
               'waves against violet, the Ring racing round the house, until he swears to win it. Then a red dawn.')
VOICEOVER = ('Hagen sleeps with his eyes open. In the moonlight, his father creeps up beside him, and whispers '
             'about the Ring.')

K = 0                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 30-33, 39-44, 158-163 and 219-226, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
SEG = [s['start'] for s in EX['segments']] + [D]
T_IN = SEG[1]                               # the moonlight surges and Alberich creeps in
T_THERE = BAR[43]                           # "Schläfst du, Hagen, mein Sohn?"
PHRASES = [(BAR[43], 'a'), (BAR[44], 'h'), (SEG[2], 'a'), (BAR[162], 'a'), (BAR[162] + 2.6, 'h')]
T_SWEAR = [BAR[159], BAR[160], BAR[161]]    # the three hammer strokes before "Schwörst du mir's, Hagen?"
T_GONE = BAR[163]                           # the dream breaks
T_DAWN = SEG[3]                             # dawn on the Rhine

NIGHT = hexc('#1a2ab0')
MOON = hexc('#80a0ff')
RED_DAWN = hexc('#ff1030')
ORANGE_DAWN = hexc('#ff6a10')
WOOD = hexc('#5a2008')
HALL = hexc('#ff8a20')
SPEAR = hexc('#c8d8ff')
TORCH = hexc('#ff6a10')
FLAME = hexc('#ffd060')
HAGEN = hexc('#7a00ff')
ALBERICH = hexc('#ff1000')
MUD = hexc('#5a1200')
GUNTHER = hexc('#ffb020')
GUTRUNE = hexc('#ff4090')
GOLD = hexc('#ffaa00')
BLOOD = hexc('#c00010')
WHITE = hexc('#ffffff')

START = dict(night=0.62, moon=0.45, dawn=0.0, hall=0.45, spear=0.55)
END = dict(night=0.3, moon=0.1, dawn=0.6, hall=0.5, spear=0.6)        # where GD16 picks the shore up
HAGEN_AT = ('Porch Front', 0.35)            # by the doors, beside his spear
HAGEN_LVL = (0.45, 0.8)                     # asleep at the start; standing at the end


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """The shore before the hall as profiles over the house: the porch is the hall's doors, its seams lit from
    inside, the spear upright in the middle of Porch Front; the wings and Side are the shore, the river beyond the
    free end of Right."""
    d = G.pd
    rng = np.random.default_rng(1874)       # the same shore, moonlight and torches in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    spear = at(G, 'Porch Front', 0.5)
    L = d.max()
    return dict(
        d=d, L=L, porch=porch, shore=~porch, spear=spear,
        doors=porch * (0.65 + 0.35 * smooth_noise(rng, d, 30.0)),
        seams=porch * np.clip(np.sin(2 * np.pi * (d - at(G, 'Porch Left', 0.0)) / 95) * 3 - 2.2, 0, 1),
        tip=np.exp(-((d - spear) / 7) ** 2),
        river=smoothstep(L - 600, L, d),      # the dawn comes up from the river end
        sand=~porch * (0.7 + 0.3 * smooth_noise(rng, d, 70.0)),
        flick=Flicker(rng, G.N, 3.0, 9.0),
        glow=Flicker(rng, G.N, 0.6, 2.0),
    )


def shore(S, T, lv):
    """The shore at shared time T with levels lv (night, moon, dawn, hall, spear)."""
    d = S['d']
    drift = np.sin(2 * np.pi * (d / 310 + 0.07 * T)) * np.sin(2 * np.pi * (d / 170 - 0.05 * T) + 0.6)
    fr = light(NIGHT, lv['night'] * S['sand'] * (0.85 + 0.15 * drift))
    u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 600 - 0.03 * T))
    fr += light(MOON, lv['moon'] * S['shore'] * (0.4 + 0.6 * u) ** 2)
    sky = RED_DAWN + (ORANGE_DAWN - RED_DAWN) * (0.5 + 0.5 * np.sin(2 * np.pi * (d / 450 + 0.05 * T)))[:, None]
    fr += light(sky, lv['dawn'] * S['shore'] * (0.75 + 0.25 * drift) * (0.7 + 0.3 * S['river']))
    fr += light(WOOD, (0.4 + 0.6 * lv['hall']) * S['doors'])
    fr += light(HALL, lv['hall'] * S['seams'] * (0.8 + 0.2 * S['glow'](T)))
    fr += light(SPEAR, lv['spear'] * S['tip'] * (0.85 + 0.15 * np.sin(2 * np.pi * 0.7 * T)))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the shore, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def crowd(S, n, seed=1717):
    """Where n vassals stand with their torches, spread over the shore and the porch runs (not on the spear)."""
    rng = np.random.default_rng(seed)
    p = np.sort(rng.uniform(20, S['L'] - 15, n))
    return p[np.abs(p - S['spear']) > 30]


def torches(S, T, ps, lvl, seed=7):
    """Torches at path distances ps (lvl a scalar or one per torch): orange flames with a flickering gold core."""
    d = S['d']
    lvl = np.broadcast_to(np.asarray(lvl, float), np.shape(ps))
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 2 * np.pi, len(ps))
    fq = rng.uniform(5, 11, len(ps))
    fl = 0.8 + 0.2 * np.sin(fq * T + ph)
    g = np.exp(-((d[None, :] - np.asarray(ps)[:, None]) / 7) ** 2)
    out = light(TORCH, np.clip((lvl * fl)[:, None] * g, 0, None).sum(0).clip(0, 1.2))
    return out + light(FLAME, np.clip((0.6 * lvl * fl ** 3)[:, None] * g ** 4, 0, None).sum(0).clip(0, 1))


def sparks(S, hits, t, seed, n=14, reach=1.0):
    """Bursts [(time, strength, where)]: each throws n sparks both ways along the roofline, -> perceptual."""
    d = S['d']
    out = np.zeros_like(d)
    for i, (th, s, p0) in enumerate(hits):
        a = t - th
        if not 0 <= a < 1.6:
            continue
        rng = np.random.default_rng(seed * 1000 + i)
        v = rng.uniform(500, 2600, n) * rng.choice([-1, 1], n) * reach
        ps = p0 + v * (1 - np.exp(-a / 0.6)) * 0.6
        life = np.exp(-a / rng.uniform(0.35, 0.9, n))
        out += (s * life[:, None] * np.exp(-((d[None, :] - ps[:, None]) / 7) ** 2)).sum(0)
    return out


def part_of(t, d, m, v, h):
    """What a note of the excerpt is: its part, see compose()."""
    if t < SEG[1] and d >= 2.0 and v >= 105:
        return 'hagen'
    if SEG[2] <= t < T_SWEAR[0] and h == 0:
        return 'ring'
    if T_SWEAR[2] + 1.0 <= t < T_SWEAR[2] + 1.5 and h == 1 and v >= 120:
        return 'curse'
    if t >= T_DAWN and h == 0 and d >= 0.3 and v >= 85:
        return 'dawn'
    return 'music'


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The prelude's long swells are the
    sleeper's tritone ('hagen'); "den Ring gewinnen" is the Ring ('ring'); the fortissimo stroke after the third
    oath is the Curse ('curse'); the right hand's notes of the dawn are its surges ('dawn'). Everything else is
    'music'."""
    return [(float(t), float(d), int(m), int(v), part_of(t, d, m, v, h), None) for t, d, m, v, h, _ in tidy(EX['notes'])]


def alberich_at(G, t):
    """Where Alberich is at time t (None when he is not there)."""
    if t < T_IN or t > T_GONE + 2.0:
        return None
    a, b = G.pd.max() + 30, at(G, 'Porch Front', 0.62)
    if t < T_GONE:
        return a + (b - a) * smoothstep(T_IN, T_THERE, t)
    return b + (a - b) * smoothstep(T_GONE, T_GONE + 2.0, t)


def render(G, seed=15):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_h = at(G, *HAGEN_AT)
    ring_on = np.array(sorted({e[0] for e in N if e[4] == 'ring'}))
    curse_on = np.array(sorted({e[0] for e in N if e[4] == 'curse'}))
    dawn_on = np.array(sorted({e[0] for e in N if e[4] == 'dawn'}))
    sleep_on = [(e[0], e[1]) for e in N if e[4] == 'hagen']

    def recent(ts, t, span):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return (t - ts[i], i) if i >= 0 and t - ts[i] < span else (None, i)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_DAWN, START[k]), (T_DAWN + 14, END[k])]) for k in START}
        dream = smoothstep(T_IN - 2, T_IN + 2, t) * (1 - smoothstep(T_GONE, T_GONE + 2.5, t))
        lv['moon'] += 0.3 * dream
        fr = shore(S, T, lv)

        # each dream phrase: red rolls out from the father, violet from the son, and they crack white where they meet
        pa = alberich_at(G, t)
        for t0, who in PHRASES:
            a = t - t0
            if 0 <= a < 3.2:
                src = alberich_at(G, t0) if who == 'a' else p_h
                r = 1500 * (1 - np.exp(-a / 1.2))
                ring_ = np.exp(-((np.abs(d - src) - r) / 230) ** 2) * np.exp(-a / 1.4)
                fr += light(ALBERICH if who == 'a' else HAGEN, 1.0 * ring_)
                fr += light(MUD if who == 'a' else NIGHT, 0.6 * np.exp(-a / 0.8) * np.exp(-((d - src) / 200) ** 2))

        # the Ring: a gold loop racing round the whole house on each of its notes
        a, i = recent(ring_on, t, 3.0)
        if a is not None:
            c = (ring_on[i] * 211 + a * 1400) % L
            fr += light(GOLD, np.exp(-a / 0.9) * (np.exp(-((d - c) / 60) ** 2) + np.exp(-((d - (L - c)) / 60) ** 2)))
            fr += light(WHITE, 0.6 * np.exp(-a / 0.2) * np.exp(-((d - c) / 12) ** 2))

        # the Curse: blood red slashes from the doors out to both ends
        a, i = recent(curse_on, t, 2.5)
        if a is not None:
            front = min(1.0, a / 0.7) * max(S['spear'], L - S['spear'])
            slash = smoothstep(front + 50, front - 50, np.abs(d - S['spear']))
            fr += light(BLOOD, 0.95 * slash * np.exp(-a / 1.1))

        # three oaths demanded: the whole house red, then the son's violet answer flooding over it
        for k, t0 in enumerate(T_SWEAR):
            a = t - t0
            if 0 <= a < 2.4:
                s = 0.8 + 0.1 * k
                fr = fr * (1 - 0.5 * np.exp(-a / 0.6))
                fr += light(ALBERICH, s * smoothstep(0, 0.08, a) * np.exp(-a / 0.9))
                b = a - 1.0
                if b >= 0:
                    fr += light(HAGEN, s * np.exp(-b / 0.6) * smoothstep(1100 * b + 60, 1100 * b - 60, np.abs(d - p_h)))
                    fr += light(WHITE, 0.6 * np.exp(-b / 0.08) * np.exp(-((d - p_h) / 30) ** 2))

        # Alberich: creeping in, and the dream breaking as he shrinks out of the free end of Right
        if pa is not None:
            lvl = 0.85 * dream * (1 - 0.3 * smoothstep(T_GONE, T_GONE + 1.5, t))
            fr += light(MUD, 0.65 * lvl * np.exp(-((d - pa) / 80) ** 2))
            fr = figure(fr, S, pa, ALBERICH, lvl)
            if t > T_GONE:
                tail = smoothstep(pa, pa - 260, d) * (d > pa - 260) * (d <= pa)
                fr += light(ALBERICH, 0.7 * lvl * tail * (d - pa + 260) / 260)

        # dawn: red surges in from the river end on each note of the Dawn motif
        a, i = recent(dawn_on, t, 3.0)
        if a is not None:
            front = L - 2700 * (1 - np.exp(-a / 0.9))
            fr += light(RED_DAWN, 0.85 * np.exp(-a / 1.4) * smoothstep(front - 80, front + 80, d) * S['shore'])
            fr += light(ORANGE_DAWN, 0.8 * np.exp(-a / 0.6) * np.exp(-((d - front) / 50) ** 2))

        # the sleeper's tritone: each note a violet swell over the doors and out along the shore
        for t0, dur in sleep_on:
            a = t - t0
            if 0 <= a < dur + 1.5:
                g = smoothstep(0, 0.3, a) * np.exp(-a / (dur + 0.5))
                fr += light(HAGEN, 0.75 * g * np.exp(-((d - p_h) / (250 + 400 * a)) ** 2))

        # Hagen: asleep against the doors, breathing; he rises at dawn
        breath = 0.5 + 0.5 * np.sin(2 * np.pi * t / 4.5)
        rise = smoothstep(T_DAWN + 2, T_DAWN + 8, t)
        lvl = HAGEN_LVL[0] * (0.8 + 0.2 * breath) * (1 - rise) + HAGEN_LVL[1] * rise
        fr = figure(fr, S, p_h, HAGEN, lvl)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the night shore round the sleeper and the dream
    breaking."""
    from pixelhome.audio import whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=2.3)
    hp = pan_at(at(G, *HAGEN_AT))
    river = pan_at(G.pd.max() - 40)

    def role(t, d, m, v, h):
        part = part_of(t, d, m, v, h)
        if part == 'hagen':                                 # the sleeper's tritone: horns and bassoons, dark
            return [('horns', -12 if m >= 62 else 0, 0, 0.7), ('bassoons', -12, -6, 0.5)]
        if t < SEG[1]:                                      # the prelude's murmur: low strings and tuba
            if h == 1:
                return [('cellos trem' if d >= 1.0 else 'cellos', 0, -4, 0.6), ('basses', -12 if m >= 40 else 0, -8, 0.4)]
            return [('violas', 0, -6, 0.45), ('clarinets', -12 if m >= 72 else 0, -10, 0.35)]
        if part == 'ring':
            return [('clarinets', 0, 0, 0.7), ('oboes', 0, -8, 0.4)]
        if part == 'curse':
            return [('trombones', 12, 4, 0.9), ('tuba', 0, 0, 0.75)]
        if part == 'dawn':                                  # the dawn: horns, then trumpets as it blazes
            return [('horns', 0, 0, 0.8)] + ([('trumpets', 0, -6, 0.55)] if v >= 120 else [])
        return None

    def pan(t, m):
        pa = alberich_at(G, t)
        if pa is not None and SEG[1] <= t < T_GONE:
            return 0.5 * (pan_at(pa) + hp)
        return hp * 0.5

    o.tutti(tidy(EX['notes']), size=lambda t: 0.7 if t < T_DAWN else 0.6 + 0.4 * (t - T_DAWN) / (D - T_DAWN),
            role=role, pan=pan)
    for k, t0 in enumerate(T_SWEAR):                        # the three strokes: timpani and gong, harder each time
        o.hit('timpani', t0, 100 + 10 * k, pitch=-6, gain=0.6 + 0.15 * k, pan=hp)
        o.hit('gong', t0 + 0.02, 96 + 10 * k, gain=0.35 + 0.15 * k, pan=hp)
    o.hit('crash', T_SWEAR[2], 124, gain=0.7)
    o.hit('cymbal swell', T_IN - 2.5, 90, gain=0.35, pan=river)
    o.hit('crash', BAR[224], 118, gain=0.6)
    o.hit('crash', BAR[226], 124, gain=0.8)
    o.hit('timpani roll', BAR[223], 104, pitch=-4, gain=0.5)

    # the stage: the river under the moon, the dream rushing in and breaking apart
    o.wind(0.0, T_DAWN + 3.0, level=0.3, pan=river, seed=15)
    M.add('fx', whoosh(1.2, 400, 3000, 0.6, seed=150), T_IN - 0.9, 0.8, river)
    M.add('fx', whoosh(1.6, 3500, 300, 0.6, seed=151), T_GONE - 0.2, 0.9, river)
    o.effects([(0, -6), (T_IN - 1.2, -6), (T_IN, 0), (T_IN + 1.5, -14), (T_GONE - 0.5, -14), (T_GONE, -2),
               (T_GONE + 2.0, -2), (T_DAWN, -16), (D, -16)])
