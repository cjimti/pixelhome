"""Storm: the prelude to Die Walküre, a storm in D minor. Under the violins' tremolo D, hissing like rain, the
cellos and basses drive the storm motif, the run that rears up and the steps that plod down and back: each bar
is a gust that tears along the roofline from the free end of Right to the back of Side, its steps pulsing in the
cloud, louder and louder. Rain flies along every run in wind-driven drops. At the height of it the brass hurl
Donner's call to the thunder again and again, and each call cracks a fork of lightning along another run; the
strings climb in a chromatic scream to the top, and the whole house goes white. Then the thunder: the basses roll
on a low A, and three times the orchestra crashes down in great falling chords. The first is Wotan's spear
cutting through the storm, a pale line of light shooting out from the middle of the porch to both ends of the
house, chord by chord, over a wash of Wotan's blue.

Then the storm passes. The thunder rolls weaker each time and draws back across the house toward the door at the
free end of Right, and inside Hunding's hut is lit for the first time: a spark in the hearth on Left catches and
glows, the great ash tree takes shape in the middle of Porch Front, its trunk and then its leaves spreading over
the porch, and for a moment the gold hilt of a sword buried in the trunk glints. At the end the storm is only
outside the door, and the room waits for someone to come in out of it.

The music is Wagner's own: the prelude to Act I, its first eleven bars and then bars 52 to 90, the crescendo, the
climax and the thunder, as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the Wagner
Ring Dataset's piano reduction of the score (pixelhome/ring.py): the right hand's tremolo is the violins'
tremolo, the storm motif in the left hand is cellos and basses, Donner's call and the falling chords are horns,
trumpets and trombones over the tuba, with timpani and cymbals on the climaxes. Around the score, as a staging
would: rain hisses and wind gusts with the storm, every fork of lightning has its thunder (a crack and a boom
when it is near, a late, soft rumble when far), the spear lands with a blow and ringing steel, and when the hut
appears its hearth crackles. The effects lead through the storm and its climax; they give way to the strings'
chromatic scream before it, and recede to rain at the door and a quiet hearth once the hut appears.

compose() tags every note of the excerpt; stage() and room() are the hut, shared word for word by Act I's first
scenes, on a clock that runs on from scene to scene; render() and score() read the same timings."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK01'
TITLE = 'Storm'
KIND = 'show'
DESCRIPTION = ('Die Walküre begins in a storm. Rain lashes the house, lightning crawls along the roof, and the '
               "low strings drive the storm on until Wotan's spear cuts through it; then it passes, and a fire "
               'glows in a hut built round a great ash tree.')
VOICEOVER = ('Die Walküre. A storm in the forest, and a man running from it, with nothing left but his life. '
             'Somewhere ahead there is a fire.')

EX = excerpt(__file__)                      # Act I, bars 0-11 and 52-90, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
K = 0                                       # this scene's place on Act I's shared clock: T = t + 80 K
GUSTS = list(range(1, 12)) + list(range(52, 80))        # a gust on every bar of the storm motif
DONNER = list(range(61, 77, 2))             # Donner's call in the brass, every other bar of the climax
DONNER_AT = [('Porch Left', 0.5), ('Right', 0.35), ('Left', 0.6), ('Porch Right', 0.5), ('Porch Front', 0.3),
             ('Right', 0.6), ('Left', 0.3), ('Porch Front', 0.7)]
THUNDER = [80, 81, 84, 85, 88, 89]          # the basses roll on a low A
CRASHES = [82, 86, 90]                      # the falling chords; the first is Wotan's spear
T_CLIMAX = BAR[80]
T_SPEAR = BAR[82] + 0.46                    # the first chord of the spear
T_HUT = BAR[82] + 1.0                       # the hut begins to appear
BOLTS = ([(BAR[b], seg, u, 0) for b, (seg, u) in zip(DONNER, DONNER_AT)] +
         [(BAR[6], 'Right', 0.7, 0), (BAR[10], 'Porch Left', 0.4, 0), (BAR[55], 'Left', 0.3, 0),
          (BAR[58], 'Porch Front', 0.6, 0), (BAR[77], 'Side', 0.6, 0), (BAR[78], 'Right', 0.3, 0),
          (BAR[79], 'Left', 0.7, 0), (T_CLIMAX, 'Porch Front', 0.5, 1), (T_SPEAR, 'Porch Front', 0.5, 1),
          (BAR[86] + 0.3, 'Right', 0.8, 0), (BAR[90] + 0.34, 'Right', 0.92, 0)])

HUT = hexc('#3a1a0a')                       # the room, warm and dark
HEARTH = hexc('#ff6a10')
EMBER = hexc('#ff3000')
TRUNK = hexc('#5a3010')
LEAVES = hexc('#50b030')
HILT = hexc('#ffcc40')
STORM = hexc('#5a6a8a')
RAIN = hexc('#a8bcdc')
BOLT = hexc('#e8f0ff')
GLOW = hexc('#7080ff')                      # the fork's afterimage
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
WHITE = hexc('#ffffff')

# the hut at the end, as WK02 begins: perceptual levels of each part of room()
END = dict(bed=0.20, hearth=0.62, trunk=0.95, leaves=0.62, hilt=0.45, door=0.5)


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Hunding's hut as profiles over the house: the hearth on Left, the ash tree in the middle of Porch Front with
    its leaves over the porch and the sword's hilt in its trunk, the door at the free end of Right."""
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    rng = np.random.default_rng(1874)       # the same fire, leaves and rain in every scene, so the cuts match
    trunk = np.exp(-((d - pf) / 16) ** 2)
    clumps = 0.55 + 0.45 * smooth_noise(rng, d, 45.0)
    return dict(
        d=d, pf=pf,
        hearth=np.exp(-((d - at(G, 'Left', 0.4)) / 125) ** 2),
        trunk=trunk,
        hilt=np.exp(-((d - pf) / 5) ** 2),
        canopy=porch * np.exp(-((d - pf) / 310) ** 2) * clumps * (1 - trunk),
        door=smoothstep(at(G, 'Right', 0.7), at(G, 'Right', 1.0), d),
        fire=Flicker(rng, G.N, 0.8, 3.2),
        stir=Flicker(rng, G.N, 0.08, 0.35),
        rain=Flicker(rng, G.N, 4.0, 11.0),
    )


def room(S, T, lv):
    """The hut at shared time T with levels lv (bed, hearth, trunk, leaves, hilt, door)."""
    fire = S['fire'](T)
    stir = S['stir'](T)
    fr = light(HUT, lv['bed'] * (0.9 + 0.1 * stir))
    fr += light(HEARTH, lv['hearth'] * S['hearth'] * (0.86 + 0.14 * fire))
    fr += light(EMBER, 0.55 * lv['hearth'] * S['hearth'] ** 3 * (0.7 + 0.3 * fire))
    fr += light(TRUNK, lv['trunk'] * S['trunk'])
    fr += light(LEAVES, lv['leaves'] * S['canopy'] * (0.82 + 0.18 * stir))
    fr += light(HILT, lv['hilt'] * S['hilt'] * (0.8 + 0.2 * np.sin(2 * np.pi * 0.45 * T)))
    rain = np.clip(S['rain'](T), 0, None) ** 2 / 3
    fr += light(STORM, lv['door'] * S['door'] * (0.62 + 0.38 * rain))
    return fr


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The right hand's repeated notes
    are the violins' tremolo ('trem', held as one note); in the gust bars the left hand is the storm motif
    ('storm', k = the gust); in Donner's bars the right hand's long notes are his call ('donner', k = the call)
    and its runs the strings ('run'); the thunder bars are the basses' roll ('thunder'); the falling chords are
    'crash' (k = which crash) in both hands; the chromatic climb before the climax is 'climb'."""
    bar_of = lambda t: max(m for m, bt in EX['bars'] if bt <= t + 1e-6)
    raw = sorted(EX['notes'])
    # grace-note clusters (all at one instant) become quick runs, lowest first
    notes, i = [], 0
    while i < len(raw):
        j = i
        while j < len(raw) and raw[j][0] == raw[i][0] and raw[j][1] <= 0.031 and raw[j][4] == raw[i][4]:
            j += 1
        if j - i > 1:
            grp = sorted({(n[2], n[4]): n for n in raw[i:j]}.values(), key=lambda n: n[2])
            for q, n in enumerate(grp):
                notes.append([n[0] + 0.035 * q, 0.06, n[2], n[3], n[4]])
            i = j
        else:
            notes.append(raw[i])
            i += 1
    N, trem = [], {}
    for t, d, m, v, h in sorted(notes):
        b = bar_of(t)
        if b in CRASHES or b in (83, 87):
            N.append((t, d, m, v, 'crash', CRASHES.index(b if b in CRASHES else b - 1)))
        elif h == 0 and d < 0.2 and b not in range(77, 80) and (b < 61 or b > 76):
            key = (m,)                      # the tremolo: repeated notes merge into one held note
            if key in trem and t - trem[key][1] < 0.4:
                trem[key][1] = t + d
            else:
                if key in trem:
                    N.append((trem[key][0], trem[key][1] - trem[key][0], m, trem[key][2], 'trem', None))
                trem[key] = [t, t + d, v]
        elif h == 0 and b in range(77, 80):
            N.append((t, d, m, v, 'climb', None))
        elif h == 0:
            k = DONNER.index(b if b in DONNER else b - 1)
            N.append((t, d, m, v, 'donner' if d >= 0.3 else 'run', k))
        elif b in THUNDER:
            N.append((t, d, m, v, 'thunder', b))
        else:
            N.append((t, d, m, v, 'storm', b if b in GUSTS else None))
    for m, (t0, t1, v) in trem.items():
        N.append((t0, t1 - t0, m[0], v, 'trem', None))
    return sorted(N, key=lambda e: e[0])


def bar_len(b):
    nxt = [t for m, t in EX['bars'] if m == b + 1]
    return (nxt[0] if nxt else D) - BAR[b]


def gust_pos(S, t0, t, span):
    """Where a gust front is, span seconds after t0 it set out: from the free end of Right to the back of Side."""
    return S['d'].max() + 150 - (S['d'].max() + 300) * (t - t0) / span


def storm_level(t):
    return keys(t, [(0, 0.3), (3, 0.5), (BAR[9], 0.55), (BAR[12], 0.4), (BAR[53], 0.45), (BAR[61], 0.9),
                    (BAR[77], 1.0), (T_CLIMAX + 3, 1.0), (BAR[84], 0.7), (BAR[88], 0.35), (D, 0.15)])


def retreat(S, t):
    """After the climax the storm draws back toward the door."""
    edge = keys(t, [(T_SPEAR, -600.0), (D - 2, 2420.0)])
    return smoothstep(edge - 350, edge + 80, S['d'])


def render(G, seed=1):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, pf = S['d'], S['pf']
    order = G.path
    ds = d[order]
    N = compose()
    storm_on = {b: np.array([e[0] for e in N if e[4] == 'storm' and e[5] == b]) for b in GUSTS}
    gust_v = {b: max([e[3] for e in N if e[4] == 'storm' and e[5] == b], default=60) for b in GUSTS}
    calls = [(e[0], e[5]) for e in N if e[4] == 'donner']
    climb = np.array([e[0] for e in N if e[4] == 'climb'])
    thunder = np.array([(e[0], e[3]) for e in N if e[4] == 'thunder'])
    spear = sorted({round(e[0], 2) for e in N if e[4] == 'crash' and e[5] == 0})
    bolt_fx = []
    for t, seg, u, big in BOLTS:
        mask = (G.seg_of == seg) | (big and np.ones(G.N, bool))
        bolt_fx.append(dict(t=t, c=at(G, seg, u), mask=mask, big=big, jag=rng.uniform(0.25, 1.0, G.N),
                            half=0.5 * (G.pd[G.seg[seg]].max() - G.pd[G.seg[seg]].min())))
    door_c = at(G, 'Right', 0.85)
    drops = dict(p=np.zeros(0), v=np.zeros(0), age=np.zeros(0), life=np.ones(0), b=np.zeros(0))
    glint = BAR[86] + 0.3

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        sl = storm_level(t)
        rm = retreat(S, t)
        lv = {k: keys(t, pts) for k, pts in (
            ('bed', [(T_HUT, 0.0), (T_HUT + 9, END['bed'])]),
            ('hearth', [(T_HUT, 0.0), (T_HUT + 1.0, 0.25), (T_HUT + 4, 0.3), (T_HUT + 9, END['hearth'])]),
            ('trunk', [(T_HUT + 2, 0.0), (T_HUT + 8, END['trunk'])]),
            ('leaves', [(T_HUT + 4, 0.0), (T_HUT + 10, END['leaves'])]),
            ('hilt', [(glint - 0.5, 0.0), (glint, 1.0), (glint + 4, END['hilt'])]),
            ('door', [(T_HUT + 1, 0.0), (T_HUT + 10, END['door'])]))}
        fr = room(S, T, lv)

        # the storm cloud, rolling with the wind toward the back of Side
        cloud = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 820 + 0.13 * T))
        cloud2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 330 + 0.31 * T) + 1.3)
        fr += light(STORM, sl * rm * (0.1 + 0.25 * cloud * (0.4 + 0.6 * cloud2)))

        # the gusts: one per bar of the storm motif, its steps pulsing as it tears along the house in two bars
        for b in GUSTS:
            t0 = BAR[b]
            span = 2 * bar_len(b)
            if not t0 <= t < t0 + span + 0.6 or not len(storm_on[b]):
                continue
            on = storm_on[b]
            j = max(0, int(np.searchsorted(on, t, side='right')) - 1)
            pulse = 0.6 + 0.4 * np.exp(-(t - on[j]) / 0.12)
            p = gust_pos(S, t0, t, span)
            band = np.exp(-((d - p) / 240) ** 2) + 0.5 * smoothstep(p, p + 600, d) * smoothstep(p + 1200, p + 600, d)
            amp = (min(gust_v[b], 124) / 124) ** 1.6 * (1 - smoothstep(t0 + span, t0 + span + 0.6, t))
            fr += light(STORM, 0.95 * amp * pulse * band * np.maximum(rm, 0.25 * (t < T_SPEAR)))
            fr += light(RAIN, 0.5 * amp * pulse * np.exp(-((d - p) / 60) ** 2) * rm)

        # Donner's calls: each one flares where it sounds, a crown of white over a blue glow
        for tc, k in calls:
            a = t - tc
            if 0 <= a < 1.6:
                c = at(G, *DONNER_AT[k])
                fr += light(GLOW, 0.9 * np.exp(-a / 0.5) * np.exp(-((d - c) / 420) ** 2))
                fr += light(BOLT, np.exp(-a / 0.22) * np.exp(-((d - c) / 160) ** 2))
                fr += light(STORM, 0.35 * np.exp(-a / 0.3))

        # the strings' climb before the climax: the whole house brightens, flickering with every note
        if len(climb) and climb[0] <= t < T_CLIMAX:
            j = int(np.searchsorted(climb, t, side='right')) - 1
            up = smoothstep(climb[0], T_CLIMAX, t)
            fl = 0.7 + 0.3 * np.exp(-(t - climb[j]) / 0.06)
            fr += light(GLOW, 0.35 * up * fl * (0.5 + 0.5 * np.cos(2 * np.pi * (d / 260 - 3 * t))))
            fr += light(BOLT, 0.45 * up ** 2 * fl * rm)

        # the thunder: the basses' roll rumbles in the cloud, drawing back toward the door
        if len(thunder):
            near = thunder[(thunder[:, 0] <= t) & (thunder[:, 0] > t - 0.15)]
            if len(near):
                v = near[:, 1].max() / 127
                c = keys(t, [(T_CLIMAX, d.max() * 0.4), (D, door_c)])
                fr += light(STORM, 0.7 * v ** 1.5 * np.exp(-((d - c) / 700) ** 2) * (0.6 + 0.4 * rng.uniform(size=G.N)))

        # rain: wind-driven drops flying along every run
        n_new = rng.poisson(170 * sl * DT * (1 + 0.6 * (t > BAR[61])))
        if n_new:
            p = rng.uniform(0, d.max(), n_new)
            keep = rng.uniform(size=n_new) < np.interp(p, ds, rm[order])
            p = p[keep]
            k = len(p)
            drops = {key: np.concatenate([drops[key], val]) for key, val in (
                ('p', p), ('v', -rng.uniform(250, 520, k)), ('age', np.zeros(k)), ('life', rng.uniform(0.2, 0.55, k)),
                ('b', rng.uniform(0.45, 0.95, k)))}
        drops['age'] += DT
        drops['p'] += drops['v'] * DT
        alive = (drops['age'] < drops['life']) & (drops['p'] > 0)
        drops = {key: val[alive] for key, val in drops.items()}
        if len(drops['p']):
            idx = order[np.clip(np.searchsorted(ds, drops['p']), 0, G.N - 1)]
            b = np.zeros(G.N)
            np.maximum.at(b, idx, drops['b'] * (1 - drops['age'] / drops['life']))
            fr = fr * (1 - 0.5 * b[:, None]) + light(RAIN, b)

        # Wotan's spear: a pale line shoots out from the middle of the porch, one falling chord at a time
        if T_SPEAR - 0.2 <= t < T_SPEAR + 6.5:
            j = max([i for i, e in enumerate(spear) if e <= t], default=-1)
            wash = smoothstep(T_SPEAR - 0.2, T_SPEAR + 0.4, t) * (1 - smoothstep(T_SPEAR + 4.5, T_SPEAR + 6.5, t))
            fr += light(WOTAN, 0.42 * wash * np.exp(-((d - pf) / 700) ** 2))
            if j >= 0:
                tj = spear[j]
                r = 90 + 160 * j + 115 * smoothstep(tj, tj + 0.18, t)
                u = np.abs(d - pf)
                line = smoothstep(r + 10, r - 30, u) * (0.55 + 0.45 * np.exp(-((u - r) / 40) ** 2))
                hit = 0.55 + 0.45 * np.exp(-(t - tj) / 0.2)
                fr += light(SPEAR, 0.85 * hit * wash * line)

        # lightning: a fork crawls along a run and flickers; the near ones light the whole house a little
        for bf in bolt_fx:
            a = t - bf['t']
            if not 0 <= a < 1.4:
                continue
            env = np.exp(-a / 0.05) + 0.8 * np.exp(-((a - 0.14) / 0.03) ** 2) + 0.5 * np.exp(-((a - 0.27) / 0.04) ** 2)
            reach = (bf['half'] * 1.1 + (1500 if bf['big'] else 0)) * smoothstep(0, 0.08, a)
            fork = bf['mask'] * smoothstep(reach, reach - 60, np.abs(d - bf['c'])) * bf['jag']
            far = 0.5 if bf['t'] >= T_HUT else 1.0
            fr += light(BOLT, min(1.0, env) * fork * far)
            fr += light(STORM, 0.45 * min(1.0, env) * far * (0.6 + 0.4 * rm))
            fr += light(GLOW, 0.5 * far * np.exp(-a / 0.4) * smoothstep(0.05, 0.15, a) * fork)
            if bf['big'] and a < 0.18:
                fr += light(WHITE, 0.85 * np.exp(-a / 0.07))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction: the tremolo on violins, the storm on cellos and basses,
    Donner's call on horns and trumpets, the falling chords on the whole brass over the tuba, the thunder on the
    basses with the timpani rolling under it, and cymbals where the lightning strikes."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.55)
    S = {'d': G.pd}
    door = pan_at(at(G, 'Right', 0.92))
    for t, d, m, v, part, k in compose():
        if part == 'trem':
            o.play('violins trem', m, t, d, v, 0.15 if m >= 60 else -0.15, 0.6)
            if m < 60:
                o.play('violas', m, t, d, v - 20, -0.2, 0.25)
        elif part == 'storm':
            pa = pan_at(gust_pos(S, BAR[k], t, 2 * bar_len(k))) if k else 0.0
            o.play('cellos', m, t, max(d, 0.1), v, pa, 0.85)
            o.play('basses', m - 12 if m >= 40 else m, t, 0.1, v - 4, pa, 0.7)
            if v >= 100:
                o.play('bassoons', m, t, 0.1, v - 20, pa, 0.4)
        elif part == 'donner':
            pa = pan_at(at(G, *DONNER_AT[k]))
            o.play('horns', m - 12, t, d, v, pa, 0.9)
            o.play('trumpets', m - 12, t, d, v - 10, pa, 0.5)
        elif part == 'run':
            o.play('violins', m, t, d, v - 10, 0.3, 0.5)
            if m >= 77:
                o.play('flutes', m, t, 0.1, v - 20, -0.4, 0.35)
        elif part == 'climb':
            o.play('violins', m, t, d, v - 6, 0.3, 0.55)
            o.play('violas', m - 12, t, d, v - 14, -0.2, 0.4)
        elif part == 'thunder':
            o.play('cellos', m + 12 if m < 36 else m, t, 0.1, v - 10, door * 0.5, 0.5)
            o.play('basses', m, t, 0.1, v - 10, door * 0.5, 0.45)
        elif part == 'crash':
            g = (1.0, 0.75, 0.55)[k]
            if m >= 60:
                o.play('trumpets', m - 12, t, d, v - 6, -0.25, 0.45 * g)
                o.play('horns', m - 12, t, d, v - 4, 0.25, 0.6 * g)
            else:
                o.play('trombones', m, t, d, v, 0.0, 0.7 * g)
                o.play('tuba', m - 12, t, d, v - 6, 0.0, 0.6 * g)
    for b in THUNDER[::2]:                  # the timpani roll under each roll of thunder
        o.hit('timpani roll', BAR[b], 112 - 6 * THUNDER.index(b), gain=0.7, pan=door * 0.5)
    for i, (t, seg, u, big) in enumerate(BOLTS):     # every fork of lightning has its thunder, late when far
        pa = 0.0 if big else pan_at(at(G, seg, u))
        near = 1.0 if big else (0.3 if t >= T_HUT else 0.35 + 0.6 * storm_level(t))
        o.thunder(t, near, pa, gain=1.2 if big else 0.9, seed=i + 1)
        if big:
            o.hit('timpani', t, 124, pitch=-5, gain=0.9)
            o.boom(t, 0.0, 0.8)
    # the storm leads; the strings' scream before the climax is let through, then the room is quiet but for the rain
    o.effects([(0.0, 0.0), (BAR[77], -2.0), (T_CLIMAX - 0.2, -4.0), (T_CLIMAX, 1.0), (T_SPEAR + 2.5, 0.0),
               (T_HUT + 4.0, -6.0), (D, -9.0)])
    o.boom(T_SPEAR, 0.0, 1.0)                        # the spear cuts the storm: a blow and steel ringing
    o.clash(T_SPEAR, 0.0, 124, 0.8)
    # the storm itself: wind gusting with the storm, then drawing back toward the door
    o.wind(0.0, D, lambda tt: 0.35 + 0.65 * np.array([storm_level(x) for x in tt[::400]]).repeat(400)[:len(tt)],
           lambda t: door * smoothstep(T_SPEAR, D, t), seed=11)
    rain(M, o, door)
    # inside, the hearth catches and crackles
    o.fire(T_HUT, D, lambda tt: 0.25 * smoothstep(T_HUT, T_HUT + 9, tt), pan_at(at(G, 'Left', 0.5)), crackle=14, seed=3)


def rain(M, o, door):
    """Rain hissing on the roof, heavy at the height of the storm, outside the door at the end."""
    from pixelhome.audio import SR
    n = int(D * SR)
    tt = np.arange(n) / SR
    lv = np.interp(tt, np.linspace(0, D, 200), [storm_level(x) for x in np.linspace(0, D, 200)])
    hiss = o._noise(0, 2500, 11000, 21, n=n) * (0.4 + 0.6 * o._wobble(n, 12, 22, 0.6)) * lv
    hiss *= np.clip(tt / 1.0, 0, 1) * np.clip((D - tt) / 1.5, 0, 1)
    for k, side in enumerate((-0.6, 0.6)):
        M.add('fx', np.vstack([hiss, hiss]) * (0.9 if k else 1.0), 0.0, 0.32, side)
